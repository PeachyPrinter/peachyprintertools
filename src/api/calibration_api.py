import logging
import types

from infrastructure.audio import AudioWriter
from infrastructure.audiofiler import PathToAudio
from infrastructure.controller import Controller
from infrastructure.laser_control import AudioModulationLaserControl
from infrastructure.transformer import TuningTransformer, HomogenousTransformer
from infrastructure.layer_generators import *

'''The calibration API proivides the tools required to setup a Peacy Printer'''
class CalibrationAPI(object):
    def __init__(self, configuration_manager, printer):
        logging.info("Calibartion API Startup")
        self._configuration_manager = configuration_manager
        self._printer = printer
        self._configuration = self._configuration_manager.load(self._printer)

        self._point_generator = SinglePointGenerator()
        self._blink_generator = BlinkGenerator()
        self._alignment_generator = CalibrationLineGenerator()

        self._test_patterns = { 
            'Hilbert Space Filling Curve' : HilbertGenerator(),
            'Square' : SquareGenerator(),
            'Circle' : CircleGenerator(),
            'Spiral' : SpiralGenerator()
            }
        self._current_generator = self._point_generator

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
        logging.debug("Setting up audiowriter")
        self._audio_writer = AudioWriter(
            self._configuration['output_sample_frequency'], 
            self._configuration['output_bit_depth'],
            )
        self._current_generator = self._point_generator
        self._controller = Controller(
            self._laser_control,
            self._path_to_audio,
            self._audio_writer,
            self._current_generator,
            )
        self.make_pattern_fit()
        self._controller.start()

    '''Used to show a single point with no calibration applied'''
    def show_point(self,xyz = [0.5,0.5,0.5]):
        x,y,z = xyz
        self._point_generator.xy = [x,y]
        if (self._current_generator != self._point_generator):
            self._unapply_calibration()
            self._update_generator(self._point_generator)

    '''Used to show a blinking point with no calibration applied used for aligning on and off laser posisition'''
    def show_blink(self,xyz = [0.0,0.0,0.0]):
        x,y,z = xyz
        self._blink_generator.xy = [x,y]
        if (self._current_generator != self._blink_generator):
            self._unapply_calibration()
            self._update_generator(self._blink_generator)


    '''Used to show a single line on one axis used to line up calibration grid'''
    def show_line(self):
        self._unapply_calibration()
        self._update_generator(self._alignment_generator)

    def get_max_deflection(self):
        return self._configuration['max_deflection']

    def set_max_deflection(self, deflection):
        self._configuration['max_deflection'] = deflection
        self._unapply_calibration()
        self._configuration_manager.save(self._configuration)

    '''Returns the currently configured offset for laser on and off'''
    def get_laser_offset(self):
        return self._configuration['laser_offset']

    '''Sets the currently configured offset for laser on and off'''
    def set_laser_offset(self, laser_offset):
        self._configuration['laser_offset'] = laser_offset
        self._laser_control.set_offset(laser_offset)
        self._configuration_manager.save(self._configuration)


    '''Used to show a test pattern with calibration applied'''
    def show_test_pattern(self,pattern):
        if pattern in self._test_patterns.keys():
            self._apply_calibration()
            self._update_generator(self._test_patterns[pattern])
        else:
            logging.error('Pattern: %s does not exist' % pattern)
            raise Exception('Pattern: %s does not exist' % pattern)

    '''Shows the scale square'''
    def show_scale(self):
        self._unapply_calibration()
        self._update_generator(self._test_patterns['Square'])

    '''returns a list of test patterns'''
    def get_test_patterns(self):
        return self._test_patterns.keys()

    '''Returns the current calibration for the printer'''
    def current_calibration(self):
        return self._configuration['calibration_data']

    '''Saves the suppliled calibration'''
    def save(self, calibration):
        if not self.validate(calibration):
            raise Exception('Bad Calibration %s ' % calibration)
        self._configuration['calibration_data'] = calibration
        logging.debug("Saving calibration: %s" % calibration)
        self._configuration_manager.save(self._configuration)
        self.make_pattern_fit() #TODO make this better.

    #deprecated
    def make_pattern_fit(self):
        for pattern in self._test_patterns.values():
            pattern.set_radius(self.get_largest_object_radius())

    '''Validates a calibration'''
    def validate(self, calibration):
        if not 'height' in calibration:
            return False
        if not 'upper_points' in calibration:
            return False
        if not 'lower_points' in calibration:
            return False
        if (type(calibration['height']) != types.FloatType):
            return False
        if (calibration['height'] <= 0.0):
            return False
        if not self._validate_points(calibration['upper_points']):
            return False
        if not self._validate_points(calibration['lower_points']):
            return False
        return True

    '''Must be called before shutting down applications'''
    def stop(self):
        self._controller.stop()

    def _update_generator(self, generator):
        self._current_generator = generator
        self._controller.change_generator(self._current_generator)

    def _apply_calibration(self):
        self._path_to_audio.set_transformer(HomogenousTransformer(self._configuration['calibration_data'], scale = self._configuration["max_deflection"]))

    def _unapply_calibration(self):
        self._path_to_audio.set_transformer(TuningTransformer(scale = self._configuration["max_deflection"]))
    
    def _validate_points(self,points):
        if (len(points) != 4):
            return False
        return True

    '''Based on current calibrations_gets_maximum_size_of_object at the base layer'''
    def get_largest_object_radius(self):
        lowest = None
        for (x,y) in self._configuration['calibration_data']['lower_points'].values():
            if not lowest or abs(x) < lowest:
                lowest = abs(x)
            if abs(y) < lowest:
                lowest = abs(y)
        return lowest

    def stop(self):
            self._controller.stop()