import threading
import sys
import datetime
import logging

from domain.commands import *

import time

class MachineState(object):
    def __init__(self,xyz = [0.0,0.0,0.0], speed = 1.0):
        self.x, self.y, self.z = xyz
        self.speed = speed

    @property
    def xy(self):
        return [self.x,self.y]

    @property
    def xyz(self):
        return [self.x,self.y, self.z]

    def set_state(self, cordanates, speed):
        self.x, self.y, self.z = cordanates
        self.speed = speed

class MachineError(object):
    def __init__(self,message, layer = None):
        self.timestamp = datetime.datetime.now()
        self.message = message
        self.layer = layer

class MachineStatus(object):
    def __init__(self, status_call_back = None):
        self._status_call_back = status_call_back
        self._current_layer = 0
        self._laser_state = False
        self._waiting_for_drips = True
        self._height = 0.0
        self._model_height = 0.0
        self._errors = []
        self._start_time = datetime.datetime.now()
        self._stop_time = None
        self._complete = False
        self._drips = 0
        self._drips_per_second = 0
        self._skipped_layers = 0
        self._lock = threading.Lock()

    def _update(self):
        if not self._lock.locked():
            if self._status_call_back:
                self._lock.acquire()
                try:
                    self._status_call_back(self.status())
                finally:
                    self._lock.release()

    def drip_call_back(self, drips, height,drips_per_second):
        self._height = height
        self._drips = drips
        self._drips_per_second = drips_per_second
        self._update()

    def add_layer(self):
        self._current_layer += 1
        self._update()

    def skipped_layer(self):
        self._skipped_layers += 1

    def add_error(self, error):
        self._errors.append(error)
        self._update()

    def set_waiting_for_drips(self):
        self._waiting_for_drips = True
        self._update()

    def set_not_waiting_for_drips(self):
        self._waiting_for_drips = False
        self._update()

    def set_model_height(self, model_height):
        self._model_height = model_height
        self._update()

    def set_complete(self):
        self._complete = True
        self._update()

    def _elapsed_time(self):
        return datetime.datetime.now() - self._start_time

    def _status(self):
        if self._complete:
            return 'Complete'
        if (self._drips == 0 and self._current_layer == 0):
            return 'Starting'
        else:
            return 'Running'
    
    def _formatted_errors(self):
        return [ {'time': error.timestamp, 'message' : error.message, 'layer' : error.layer} for error in self._errors ]

    def status(self): 
        return { 
            'start_time' : self._start_time,
            'elapsed_time' : self._elapsed_time(),
            'current_layer' : self._current_layer,
            'status': self._status(),
            'errors' : self._formatted_errors(),
            'waiting_for_drips' : self._waiting_for_drips,
            'height' : self._height,
            'drips' : self._drips,
            'drips_per_second' : self._drips_per_second,
            'model_height' : self._model_height,
            'skipped_layers' : self._skipped_layers,
        }

class Controller(threading.Thread,):
    def __init__(self, 
                    laser_control, 
                    path_to_audio,
                    audio_writer,
                    layer_generator,
                    zaxis = None,
                    status_call_back = None, 
                    max_lead_distance = sys.float_info.max, 
                    abort_on_error=True,
                    max_speed = None,
                    commander = None,
                    layer_start_command = "S",
                    layer_ended_command = "E",
                    print_ended_command = "Z",
                    pre_layer_delay = 0.0
                    ):
        threading.Thread.__init__(self)
        self._commander = commander
        self.deamon = True
        self._abort_on_error = abort_on_error
        self._max_lead_distance = max_lead_distance
        self._max_speed = max_speed

        self._shutting_down = False
        self.running = False
        self.starting = True
        self._shut_down = False

        self.laser_off_override = False
        
        self._laser_control = laser_control
        self._path_to_audio = path_to_audio
        self._audio_writer = audio_writer
        self._layer_generator = layer_generator
        
        self.state = MachineState()
        self._status = MachineStatus(status_call_back)
        self._zaxis = zaxis
        if self._zaxis:
            self._zaxis.set_call_back(self._status.drip_call_back)

        self._abort_current_command = False
        self._pause = False
        self._pausing = False
        self._layer_start_command = layer_start_command
        self._layer_ended_command = layer_ended_command
        self._print_ended_command = print_ended_command
        self._pre_layer_delay = pre_layer_delay

    def run(self):
        logging.info('Running Controller')
        self.running = True
        if self._zaxis:
            self._zaxis.start()
        self.starting = False
        self._process_layers()
        self.running = False
        self._terminate()
        self._status.set_complete()

    def change_generator(self, layer_generator):
        self._pause = True
        self._abort_current_command = True
        while not self._pausing:
            logging.info("Waiting for pause point")
            time.sleep(0.01)
            if self._shutting_down:
                logging.warning("Unexpected Shutdown changing generators")
                break
        self.state.set_state([0.0,0.0,1.0],100)
        self._layer_generator = layer_generator
        self._pause = False

    def get_status(self):
        return self._status.status()

    def close(self):
        logging.warning("Shutdown requested")
        if not self._shutting_down:
            self._shutting_down = True
        attempts = 20
        while not self._shut_down and attempts > 0:
            attempts -= 1
            time.sleep(1)
            logging.info("Waiting for Controller Shutdown Correctly")
        if attempts > 0:
            logging.info("Controller Shutdown Correctly")
        else:
            logging.info("Controller Failed Shutting Down.")

    def _send_command(self, command):
        if self._commander:
            self._commander.send_command(command)

    def _process_layers(self):
        ahead_by = None
        layer_count  = 0
        logging.info('Start Processing Layers')
        while not self._shutting_down:
            try:
                start = time.time()
                while self._pause:
                    # logging.debug("Pause Request")
                    self._pausing = True
                    time.sleep(0.1)
                self._pausing = False
                layer = self._layer_generator.next()
                
                # logging.debug('Layer Generator Time: %.2f' % (time.time()-start))
                layer_count += 1
                self._status.add_layer()
                self._status.set_model_height(layer.z)
                if self._zaxis:
                    self._zaxis.move_to(layer.z + self._max_lead_distance)
                    self._wait_till(layer.z)
                    ahead_by = self._zaxis.current_z_location_mm() - layer.z
                if self._should_process(ahead_by):
                    self._send_command(self._layer_start_command)
                    if self._pre_layer_delay:
                        time.sleep(self._pre_layer_delay)
                    self._process_layer(layer)
                    self._send_command(self._layer_ended_command)
                else:
                    logging.warning('Dripping too fast, Skipping layer')
                    print ("Skipped at: %s" % time.time())
                    self._status.skipped_layer()
                # logging.debug("Layer Total Time: %.2f" % (time.time()-start))
            except StopIteration:
                logging.info('Layers Complete')
                self._shutting_down = True
            except Exception as ex:
                self._status.add_error(MachineError(str(ex),layer_count))
                logging.error('Unexpected Error: %s' % str(ex))
                if self._abort_on_error:
                    self._terminate()
        logging.info("Processing Layers Complete")

    def _should_process(self, ahead_by_distance):
        logging.info("Ahead by: %s" % ahead_by_distance)
        if not ahead_by_distance:
            return True
        if (ahead_by_distance <= self._max_lead_distance):
            return True
        return False

    def _almost_equal(self,a,b,sig_fig=5):
        return ( a==b or int(a*10**sig_fig) == int(b*10**sig_fig))

    def _same_posisition(self,pos_1,pos_2):
        return self._almost_equal(pos_1[0],pos_2[0]) and self._almost_equal(pos_1[1],pos_2[1])

    def _process_layer(self, layer):
        for command in layer.commands:
            # logging.info("Processing command: %s" % command)
            if self._shutting_down:
                return
            if self._abort_current_command:
                self._abort_current_command = False
                return
            if type(command) == LateralDraw:
                if not self._same_posisition(self.state.xy, command.start):
                    self._move_lateral(command.start,layer.z,command.speed)
                self._draw_lateral(command.end, layer.z, command.speed )
            elif type(command) == LateralMove:
                self._move_lateral(command.end, layer.z, command.speed)

    def _move_lateral(self,(to_x,to_y), to_z,speed):
        self._laser_control.set_laser_off()
        self._write_lateral(to_x,to_y,to_z,speed)

    def _draw_lateral(self,(to_x,to_y), to_z,speed):
            if self.laser_off_override:
            self._laser_control.set_laser_off()
        else:
            self._laser_control.set_laser_on()
        self._write_lateral(to_x,to_y,to_z,speed)
    
    def _write_lateral(self,to_x,to_y, to_z,speed):
        if self._max_speed and speed > self._max_speed:
            speed = self._max_speed
        to_xyz = [to_x,to_y,to_z]
        path = self._path_to_audio.process(self.state.xyz,to_xyz , speed)
        modulated_path = self._laser_control.modulate(path)
        if self._audio_writer:
            self._audio_writer.write_chunk(modulated_path)
        self.state.set_state(to_xyz,speed)

    def _wait_till(self, height):
        while self._zaxis.current_z_location_mm() < height:
            if self._shutting_down:
                return
            self._status.set_waiting_for_drips()
            self._move_lateral(self.state.xy, self.state.z,self.state.speed)
        self._status.set_not_waiting_for_drips()

    def _terminate(self):
        logging.info('Controller shutdown requested')
        self._shutting_down = True
        self._send_command(self._layer_ended_command)
        self._send_command(self._print_ended_command)
        try:
            self._audio_writer.close()
            logging.info("Audio shutdown correctly")
        except Exception as ex:
            logging.error(ex)
        if self._zaxis:
            try:
                self._zaxis.close()
                logging.info("Zaxis shutdown correctly")
            except Exception as ex:
                logging.error(ex)
        if self._commander:
            try:
                self._commander.close()
                logging.info("Commander shutdown correctly")
            except Exception as ex:
                logging.error(ex)
        self._shut_down = True

