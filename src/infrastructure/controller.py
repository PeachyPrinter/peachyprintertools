import threading

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


class Controller(threading.Thread):
    def __init__(self, laser_control, path_to_audio,audio_writer,layer_generator,zaxis = None):
        threading.Thread.__init__(self)
        self.deamon = True
        self._laser_control = laser_control
        self._path_to_audio = path_to_audio
        self._audio_writer = audio_writer
        self._layer_generator = layer_generator
        self._zaxis = zaxis
        self.state = MachineState()
        self._shutting_down = False

    def run(self):
        for layer in self._layer_generator:
            if self._shutting_down:
                break
            if self._zaxis:
                while self._zaxis.current_z_location_mm() < layer.z_posisition:
                    self._laser_control.set_laser_off()
                    self._move_lateral(self.state.xy, self.state.z,self.state.speed)
            for command in layer.commands:
                if type(command) == LateralDraw:
                    if self.state.xy != command.start:
                        self._laser_control.set_laser_off()
                        self._move_lateral(command.start,layer.z_posisition,command.speed)
                    self._laser_control.set_laser_on()
                    self._move_lateral(command.end, layer.z_posisition, command.speed )
                elif type(command) == LateralMove:
                    self._laser_control.set_laser_off()
                    self._move_lateral(command.end, layer.z_posisition, command.speed)
        self._terminate()

    @property
    def running(self):
        return not self._shutting_down

    def _terminate(self):
        self._shutting_down = True
        if self._zaxis:
            try:
                self._zaxis.stop()
            except Exception as ex:
                print(ex)
        try:
            self._audio_writer.stop()
        except Exception as ex:
            print(ex)

    def stop(self):
        self._shutting_down = True

    def _move_lateral(self,(to_x,to_y), to_z,speed):
        to_xyz = [to_x,to_y,to_z]
        path = self._path_to_audio.process(self.state.xyz,to_xyz , speed)
        modulated_path = self._laser_control.modulate(path)
        self._audio_writer.write_chunk(modulated_path)
        self.state.set_state(to_xyz,speed)