import logging

from infrastructure.audio import AudioWriter
from infrastructure.audiofiler import PathToAudio
from infrastructure.controller import Controller
from infrastructure.drip_based_zaxis import DripBasedZAxis
from infrastructure.laser_control import AudioModulationLaserControl
from infrastructure.gcode_layer_generator import GCodeReader
from infrastructure.transformer import HomogenousTransformer


'''TODO'''
class PrintAPI(object):
    def __init__(self, configuration, status_call_back = None):
        logging.info("Print API Startup")
        self._configuration = configuration
        self._controller = None
        self._status_call_back = status_call_back

    def print_gcode(self, file_like_object):
        gcode_reader = GCodeReader(file_like_object)
        layer_generator = gcode_reader.get_layers()
        self.print_layers(layer_generator)

    def print_layers(self, layer_generator):
        laser_control = AudioModulationLaserControl(
            self._configuration['output_sample_frequency'],
            self._configuration['on_modulation_frequency'],
            self._configuration['off_modulation_frequency']
            )
        transformer = HomogenousTransformer(self._configuration['calibration_data'], scale = self._configuration["max_deflection"])
        path_to_audio = PathToAudio(
            laser_control.actual_samples_per_second,
            transformer, 
            self._configuration['laser_thickness_mm']
            )
        audio_writer = AudioWriter(
            self._configuration['output_sample_frequency'], 
            self._configuration['output_bit_depth'],
            )
        zaxis = DripBasedZAxis(
            drips_per_mm = self._configuration['drips_per_mm'], 
            initial_height = 0.0, 
            sample_rate = self._configuration['input_sample_frequency'],
            bit_depth = self._configuration['input_bit_depth'],
            )
        self._controller = Controller(
            laser_control,
            path_to_audio,
            audio_writer,
            layer_generator,
            zaxis = zaxis,
            status_call_back = self._status_call_back
            )
        self._controller.start()


    def get_status(self):
        return self._controller.get_status()

    def verify_gcode(self, g_code_file_like_object):
        # returns list/first errors and line numbers
        pass

    def stop(self):
        if self._controller:
            self._controller.stop()
        else:
            logging.warning('Stopped before printing')