import logging

from infrastructure.audio import AudioWriter
from infrastructure.audiofiler import PathToAudio
from infrastructure.controller import Controller
from infrastructure.laser_control import AudioModulationLaserControl
from infrastructure.transformer import TuningTransformer
from infrastructure.layer_generators import SinglePointGenerator, CalibrationLineGenerator, HilbertGenerator

'''TODO'''
class CalibrationAPI(object):
    def __init__(self, configuration):
        logging.info("Print API Startup")
        self._configuration = configuration
        self._patterns = { 
            'Single Point' : SinglePointGenerator(), 
            'Grid Alignment Line' :  CalibrationLineGenerator(),
            'Hilbert Space filling' : HilbertGenerator(),
            }
        self._layer_generator = self._patterns["Single Point"]
        self._laser_control = AudioModulationLaserControl(
            self._configuration['output_sample_frequency'],
            self._configuration['on_modulation_frequency'],
            self._configuration['off_modulation_frequency']
            )
        self._transformer = TuningTransformer(scale = self._configuration["max_deflection"])
        self._path_to_audio= PathToAudio(
            self._laser_control.actual_samples_per_second,
            self._transformer,
            self._configuration["laser_thickness_mm"]
            )
        self._audio_writer = None
        self._controller = None

    def start(self):
        self._audio_writer = AudioWriter(
            self._configuration['output_sample_frequency'], 
            self._configuration['output_bit_depth'],
            )
        self._controller = Controller(
            self._laser_control,
            self._path_to_audio,
            self._audio_writer,
            self._layer_generator,
            )

        self._controller.start()

    def move_to(self,xyz_computer):
        x,y,z = xyz_computer
        self._layer_generator.xy = [x,y]

    def get_patterns(self):
        return self._patterns.keys()

    def change_pattern(self, pattern):
        if pattern in self._patterns.keys():
            self._controller.change_generator(self._patterns[pattern])
        else:
            logging.error('Pattern: %s does not exist' % pattern)
            raise Exception('Pattern: %s does not exist' % pattern)

    def change_scale(self,scale):
        pass

    def get_calibration_points(self):
        return self._configuration['calibration_data']

    def get_calibration_scale(self):
        return self._configuration['calibration_scale']

    def save(self, points):
        pass

    def stop(self):
        if self._controller:
            self._controller.stop()
        else:
            raise Exception('Controller not running')