from domain.commands import *

class MachineState(object):
    def __init__(self,x = 0.0,y = 0.0, z = 0.0):
        self.x = x
        self.y = y
        self._z = z

    def set_state(self, cordanates):
        self.x,self.y = cordanates

    @property
    def z(self):
        return 0.0

    @property
    def cartesian_plane(self):
        return [self.x,self.y]


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
            for command in layer.commands:
                if type(command) == LateralDraw:
                    self._laser_control.set_laser_on()
                    self._move_lateral(command)
                elif type(command) == LateralMove:
                    self._laser_control.set_laser_off()
                    self._move_lateral(command)

    def _move_lateral(self,command):
        path = self._path_to_audio.process(self.state.cartesian_plane, command.end, command.speed)
        modulated_path = self._laser_control.modulate(path)
        self._audio_writer.write_chunk(modulated_path)
        self.state.set_state(command.end)