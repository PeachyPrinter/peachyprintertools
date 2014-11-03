import threading
import sys
import datetime
import logging
import time

from domain.commands import *
from infrastructure.commander import NullCommander
from infrastructure.machine import *
from infrastructure.layer_writer import LayerWriter
from threading import Lock

class LayerProcessing():
    def __init__(self,
        writer,
        state,
        status,
        zaxis,
        max_lead_distance,
        commander,
        pre_layer_delay,
        layer_start_command,
        layer_ended_command,
        print_ended_command
        ):
        self._writer = writer
        self._layer_count = 0
        self._state = state
        self._status = status
        self._zaxis = zaxis
        self._max_lead_distance = max_lead_distance
        self._commander = commander
        self._pre_layer_delay = pre_layer_delay
        self._layer_start_command = layer_start_command
        self._layer_ended_command = layer_ended_command
        self._print_ended_command = print_ended_command


        self._shutting_down = False
        self._shutdown = False
        self._lock = Lock()

        if self._zaxis:
            self._zaxis.set_call_back(self._status.drip_call_back)
            self._zaxis.start()
            

    def process(self,layer):
        if self._shutting_down or self._shutdown:
            raise Exception("LayerProcessing alreay shutdown")
        with self._lock:
            self._layer_count += 1
            ahead_by = 0
            self._status.add_layer()
            self._status.set_model_height(layer.z)
            if self._zaxis:
                self._zaxis.move_to(layer.z + self._max_lead_distance)
                self._wait_till(layer.z)
                ahead_by = self._zaxis.current_z_location_mm() - layer.z
            if self._should_process(ahead_by):
                self._commander.send_command(self._layer_start_command)
                if self._pre_layer_delay:
                    self._writer.wait_till_time(time.time() + self._pre_layer_delay)
                self._writer.process_layer(layer)
                self._commander.send_command(self._layer_ended_command)
            else:
                logging.warning('Dripping too fast, Skipping layer')
                self._status.skipped_layer()

    def _should_process(self, ahead_by_distance):
        if not ahead_by_distance:
            return True
        if (ahead_by_distance <= self._max_lead_distance):
            logging.info("Ahead (Acceptable) by: %s" % ahead_by_distance)
            return True
        logging.info("Ahead (Unacceptably) by: %s" % ahead_by_distance)
        return False

    def _wait_till(self, height):
        while self._zaxis.current_z_location_mm() < height:
            if self._shutting_down:
                return
            self._status.set_waiting_for_drips()
            self._writer.wait_till_time(time.time() + (0.1))
        self._status.set_not_waiting_for_drips()

    def terminate(self):
        self._shutting_down = True
        with self._lock:
            self._shutdown = True
            self._commander.send_command(self._print_ended_command)
            if self._zaxis:
                try:
                    self._zaxis.close()
                    logging.info("Zaxis shutdown correctly")
                except Exception as ex:
                    logging.error(ex)
            try:
                self._commander.close()
                logging.info("Commander shutdown correctly")
            except Exception as ex:
                logging.error(ex)


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
                    override_speed = None,
                    commander = NullCommander(),
                    layer_start_command = "S",
                    layer_ended_command = "E",
                    print_ended_command = "Z",
                    pre_layer_delay = 0.0
                    ):
        threading.Thread.__init__(self)
        
        self.deamon = True
        self._abort_on_error = abort_on_error
        
        self._shutting_down = False
        self.running = False
        self.starting = True
        self._shutdown = False
        
        self._layer_generator = layer_generator
        
        self.state = MachineState()
        self._status = MachineStatus(status_call_back)

        self._pause = False
        self._pausing = False

# ----------------------------------------------------------

        self._override_speed = override_speed
        self._laser_control = laser_control
        self._path_to_audio = path_to_audio
        self._audio_writer = audio_writer
        self._writer = LayerWriter(
            self._override_speed, 
            self.state, 
            self._audio_writer, 
            self._path_to_audio, 
            self._laser_control
            )

# ----------------------------------------------------------
        self._max_lead_distance = max_lead_distance
        self._zaxis = zaxis
        self._commander = commander
        self._layer_start_command = layer_start_command
        self._layer_ended_command = layer_ended_command
        self._print_ended_command = print_ended_command
        self._pre_layer_delay = pre_layer_delay

        self._layer_processing = LayerProcessing(
            self._writer,
            self.state,
            self._status,
            self._zaxis,
            self._max_lead_distance,
            self._commander,
            self._pre_layer_delay,
            self._layer_start_command,
            self._layer_ended_command,
            self._print_ended_command
            )


    def run(self):
        logging.info('Running Controller')
        self.running = True
        self.starting = False
        self._process_layers()
        self.running = False
        self._terminate()
        self._status.set_complete()

    def change_generator(self, layer_generator):
        self._pause = True
        self._writer.abort_current_command()
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
            self._writer.terminate()
            self._layer_processing.terminate()
        attempts = 20
        while not self._shutdown and attempts > 0:
            attempts -= 1
            time.sleep(1)
            logging.info("Waiting for Controller Shutdown Correctly")
        if attempts > 0:
            logging.info("Controller Shutdown Correctly")
        else:
            logging.info("Controller Failed Shutting Down.")

    def _process_layers(self):
        logging.info('Start Processing Layers')
        while not self._shutting_down:
            try:
                start = time.time()
                while self._pause:
                    self._pausing = True
                    time.sleep(0.1)
                self._pausing = False
                layer = self._layer_generator.next()
                self._layer_processing.process(layer)
            except StopIteration:
                logging.info('Layers Complete')
                self._shutting_down = True
            except Exception as ex:
                self._status.add_error(MachineError(str(ex),self._status.status()['current_layer']))
                logging.error('Unexpected Error: %s' % str(ex))
                if self._abort_on_error:
                    self._terminate()
        logging.info("Processing Layers Complete")

    def _terminate(self):
        logging.info('Controller shutdown requested')
        self._shutting_down = True
        self._writer.terminate()
        self._layer_processing.terminate()
        self._shutdown = True

