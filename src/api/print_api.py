from infrastructure.audio import AudioWriter
from infrastructure.audiofiler import PathToAudio
from infrastructure.controller import Controller
from infrastructure.drip_based_zaxis import DripBasedZAxis
from infrastructure.laser_control import AudioModulationLaserControl
from infrastructure.gcode_layer_generator import GCodeReader
from infrastructure.transformer import OneToOneTransformer


'''This is just a referance at this time'''
class PrintAPI(object):
    def __init__(self, configuration):
        self._configuration = configuration

    def print_gcode(self, file_like_object):
        self.laser_control = AudioModulationLaserControl(
            self._configuration['output_sample_frequency'],
            self._configuration['on_modulation_frequency'],
            self._configuration['off_modulation_frequency']
            )
        self.transformer = OneToOneTransformer()
        self._path_to_audio = PathToAudio(
            self.laser_control.actual_samples_per_second,
            self.transformer, 
            self._configuration['laser_thickness_mm']
            )
        self._audio_writer = AudioWriter(
            self._configuration['output_sample_frequency'], 
            self._configuration['output_bit_depth'],
            )
        self.gcode_reader = GCodeReader(file_like_object)
        self._layer_generator = self.gcode_reader.get_layers()
        self._zaxis = DripBasedZAxis(
            drips_per_mm = self._configuration['drips_per_mm'], 
            initial_height = 0.0, 
            sample_rate = self._configuration['input_sample_frequency'],
            bit_depth = self._configuration['input_bit_depth'],
            )
        self._controller = Controller(
            self.laser_control,
            self._path_to_audio,
            self._audio_writer,
            self._layer_generator,
            self._zaxis)
        self._controller.start()

    def get_status(self):
        return self._controller.status

    def verify_gcode(self, g_code_file_like_object):
        # returns list/first errors and line numbers
        pass

    def stop(self):
        self._controller.stop()