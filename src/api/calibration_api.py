import logging
import types

from infrastructure.audio import AudioWriter
from infrastructure.audiofiler import PathToAudio
from infrastructure.controller import Controller
from infrastructure.laser_control import AudioModulationLaserControl
from infrastructure.transformer import TuningTransformer, HomogenousTransformer
from infrastructure.layer_generators import SinglePointGenerator, CalibrationLineGenerator, HilbertGenerator

'''TODO'''
class CalibrationAPI(object):
    def __init__(self, configuration_manager, printer):
        logging.info("Calibartion API Startup")
        self._configuration_manager = configuration_manager
        self._printer = printer
        self._configuration = self._configuration_manager.load(self._printer)
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
        transformer = TuningTransformer(scale = self._configuration["max_deflection"])
        self._path_to_audio= PathToAudio(
            self._laser_control.actual_samples_per_second,
            transformer,
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

    def apply_calibration(self):
        self._path_to_audio.set_transformer(HomogenousTransformer(self._configuration['calibration_data'], scale = self._configuration["max_deflection"]))

    def unapply_calibration(self):
        self._path_to_audio.set_transformer(TuningTransformer(scale = self._configuration["max_deflection"]))

    def change_scale(self,scale):
        pass

    def load(self):
        return self._configuration['calibration_data']

    def get_calibration_scale(self):
        return self._configuration['calibration_scale']

    def save(self, data):
        if not self.validate_data(data):
            raise Exception('Bad Calibration %s ' % data)
        self._configuration['calibration_data'] = data
        logging.debug("Saving calibration: %s" % data)
        self._configuration_manager.save(self._configuration)

    def validate_data(self, data):
        if not 'height' in data:
            return False
        if not 'upper_points' in data:
            return False
        if not 'lower_points' in data:
            return False
        if (type(data['height']) != types.FloatType):
            return False
        if (data['height'] <= 0.0):
            return False
        if not self._validate_points(data['upper_points']):
            return False
        if not self._validate_points(data['lower_points']):
            return False
        return True
    
    def _validate_points(self,points):
        if (len(points) != 4):
            return False
        return True

    def stop(self):
        if self._controller:
            self._controller.stop()
        else:
            raise Exception('Controller not running')