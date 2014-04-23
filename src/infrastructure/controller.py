import threading
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

class MachineStatus(object):
    def __init__(self, zaxis = None):
        self._zaxis = zaxis
        self.current_layer = 0
        self.laser_state = False
        self.waiting_for_drips = True
        self.errors = []
        self.start_time = datetime.datetime.now()
        self.complete = False

    def add_layer(self):
        self.current_layer += 1

    @property
    def drips(self):
        if self._zaxis:
            return self._zaxis.get_drips()
        else:
            return "Not Counting Drips"

    @property
    def z_posisition(self):
        if self._zaxis:
            return self._zaxis.current_z_location_mm()
        else:
            return "Not Counting Drips"

    @property
    def elapsed_time(self):
        return datetime.datetime.now() - self.start_time


class Controller(threading.Thread,):
    def __init__(self, laser_control, path_to_audio,audio_writer,layer_generator,zaxis = None):
        threading.Thread.__init__(self)
        self.deamon = True

        self._shutting_down = False
        self.running = False
        self.starting = True
        
        self._laser_control = laser_control
        self._path_to_audio = path_to_audio
        self._audio_writer = audio_writer
        self._layer_generator = layer_generator
        self._zaxis = zaxis
        self.state = MachineState()
        self.status = MachineStatus(self._zaxis)
        self._abort_current_command = False
        logging.info("Starting print")

    def change_generator(self, layer_generator):
        self._layer_generator = layer_generator
        self._abort_current_command = True

    def _process_layers(self):
        going = True
        while going:
            try:
                logging.debug("New Layer")
                layer = self._layer_generator.next()
                if self._shutting_down:
                    return
                if self._zaxis:
                    while self._zaxis.current_z_location_mm() < layer.z:
                        logging.info("Controller: Waiting for drips")
                        self.status.waiting_for_drips = True
                        if self._shutting_down:
                            return
                        self._laser_control.set_laser_off()
                        self._move_lateral(self.state.xy, self.state.z,self.state.speed)
                self.status.waiting_for_drips = False
                for command in layer.commands:
                    if self._shutting_down:
                        return
                    if self._abort_current_command:
                        self._abort_current_command = False
                        break
                    if type(command) == LateralDraw:
                        logging.debug('Lateral Draw: %s' % command)
                        if self.state.xy != command.start:
                            self._laser_control.set_laser_off()
                            self._move_lateral(command.start,layer.z,command.speed)
                        self._laser_control.set_laser_on()
                        self._move_lateral(command.end, layer.z, command.speed )
                    elif type(command) == LateralMove:
                        logging.debug('Lateral Move: %s' % command)
                        self._laser_control.set_laser_off()
                        self._move_lateral(command.end, layer.z, command.speed)
                self.status.add_layer()
            except StopIteration:
                going = False

    def run(self):
        self.running = True
        if self._zaxis:
            self._zaxis.start()
        self.starting = False
        self._process_layers()
        self.status.complete = True
        self._terminate()

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
        self.running = False

    def stop(self):
        logging.warning("Shutdown requested")
        self._shutting_down = True

    def _move_lateral(self,(to_x,to_y), to_z,speed):
        to_xyz = [to_x,to_y,to_z]
        path = self._path_to_audio.process(self.state.xyz,to_xyz , speed)
        modulated_path = self._laser_control.modulate(path)
        self._audio_writer.write_chunk(modulated_path)
        self.state.set_state(to_xyz,speed)