from domain.commands import *

class MachineState(object):
    def __init__(self,xy = [0.0,0.0], speed = 1.0):
        self.xy = xy
        self.speed = speed

    def set_state(self, cordanates, speed):
        self.xy = cordanates
        self.speed = speed


class Controller(object):
    def __init__(self, laser_control, path_to_audio,audio_writer,layer_generator,zaxis = None):
        self._laser_control = laser_control
        self._path_to_audio = path_to_audio
        self._audio_writer = audio_writer
        self._layer_generator = layer_generator
        self._zaxis = zaxis
        self.state = MachineState()

    def start(self):
        for layer in self._layer_generator:
            if self._zaxis:
                while self._zaxis.current_z_location_mm() < layer.z_posisition:
                    self._laser_control.set_laser_off()
                    self._move_lateral(self.state.xy, self.state.speed)
            for command in layer.commands:
                if type(command) == LateralDraw:
                    if self.state.xy != command.start:
                        self._laser_control.set_laser_off()
                        self._move_lateral(command.start,command.speed)
                    self._laser_control.set_laser_on()
                    self._move_lateral(command.end, command.speed )
                elif type(command) == LateralMove:
                    self._laser_control.set_laser_off()
                    self._move_lateral(command.end, command.speed)

    def _move_lateral(self,to_xy,speed):
        path = self._path_to_audio.process(self.state.xy, to_xy, speed)
        modulated_path = self._laser_control.modulate(path)
        self._audio_writer.write_chunk(modulated_path)
        self.state.set_state(to_xy,speed)