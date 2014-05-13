import threading
import sys
import datetime
import logging

from domain.commands import *

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
    def __init__(self,message):
        self.timestamp = datetime.datetime.now()
        self.message = message

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
        self._skipped_layers = 0

    def _update(self):
        if self._status_call_back:
            self._status_call_back(self.status())

    def drip_call_back(self, drips, height):
        self._height = height
        self._drips = drips
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
        return [ {'time': error.timestamp, 'message' : error.message} for error in self._errors ]

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
                    zaxis_control = None,
                    status_call_back = None, 
                    max_lead_distance = sys.float_info.max, 
                    ):
        threading.Thread.__init__(self)
        self.deamon = True
        self._max_lead_distance = max_lead_distance
        self._zaxis_control = zaxis_control

        self._shutting_down = False
        self.running = False
        self.starting = True
        
        self._laser_control = laser_control
        self._path_to_audio = path_to_audio
        self._audio_writer = audio_writer
        self._layer_generator = layer_generator
        
        self.state = MachineState()
        self._status = MachineStatus(status_call_back)
        self._zaxis = zaxis
        if self._zaxis:
            self._zaxis.set_drip_call_back(self._status.drip_call_back)
        self._abort_current_command = False
        logging.info("Starting print")


    def run(self):
        self.running = True
        if self._zaxis:
            self._zaxis.start()
        if self._zaxis_control:
            self._zaxis_control.move_up()
        self.starting = False
        self._process_layers()
        self._status.set_complete()
        self._terminate()

    def change_generator(self, layer_generator):
        self._layer_generator = layer_generator
        self._abort_current_command = True

    def get_status(self):
        return self._status.status()

    def stop(self):
        logging.warning("Shutdown requested")
        self._shutting_down = True

    def _process_layers(self):
        ahead_by = None
        while not self._shutting_down:
            try:
                layer = self._layer_generator.next()
                self._status.set_model_height(layer.z)
                if self._zaxis:
                    self._wait_till(layer.z)
                    ahead_by = self._zaxis.current_z_location_mm() - layer.z

                if self._should_process(ahead_by):
                    if self._zaxis_control and ahead_by and ahead_by >= self._max_lead_distance:
                        self._zaxis_control.stop()
                    self._process_layer(layer)
                else:
                    logging.warning("Dripping too fast, Skipping layer")
                    self._status.skipped_layer()

                self._status.add_layer()
            except StopIteration:
                self._shutting_down = True

    def _should_process(self, ahead_by_distance):
        if not ahead_by_distance:
            return True
        if (ahead_by_distance <= self._max_lead_distance):
            return True
        else:
            if self._zaxis_control:
                return True
        return False

    def _process_layer(self, layer):
        for command in layer.commands:
            if self._shutting_down:
                return
            if self._abort_current_command:
                self._abort_current_command = False
                break
            if type(command) == LateralDraw:
                if self.state.xy != command.start:
                    self._laser_control.set_laser_off()
                    self._move_lateral(command.start,layer.z,command.speed)
                self._laser_control.set_laser_on()
                self._move_lateral(command.end, layer.z, command.speed )
            elif type(command) == LateralMove:
                self._laser_control.set_laser_off()
                self._move_lateral(command.end, layer.z, command.speed)

    def _move_lateral(self,(to_x,to_y), to_z,speed):
        to_xyz = [to_x,to_y,to_z]
        logging.debug("creating path")
        path = self._path_to_audio.process(self.state.xyz,to_xyz , speed)
        logging.debug("modulating path")
        modulated_path = self._laser_control.modulate(path)
        logging.debug("writing audio")
        self._audio_writer.write_chunk(modulated_path)
        logging.debug("Done writing audio")
        self.state.set_state(to_xyz,speed)

    def _wait_till(self, height):
        while self._zaxis.current_z_location_mm() < height:
            if self._zaxis_control:
                self._zaxis_control.move_up()
            logging.info("Controller: Waiting for drips")
            self._status.set_waiting_for_drips()
            if self._shutting_down:
                return
            self._laser_control.set_laser_off()
            self._move_lateral(self.state.xy, self.state.z,self.state.speed)
        self._status.set_not_waiting_for_drips()


    def _terminate(self):
        self._shutting_down = True
        if self._zaxis:
            try:
                self._zaxis.stop()
            except Exception as ex:
                logging.error(ex)
        try:
            self._audio_writer.close()
        except Exception as ex:
            logging.error(ex)
        if self._zaxis_control:
            self._zaxis_control.stop()
            self._zaxis_control.close()
        self.running = False

