import types
import logging

from infrastructure.audio import AudioSetup
from infrastructure.drip_based_zaxis import DripBasedZAxis


'''TODO'''
class ConfigurationAPI(object):
    _BEST_AUDIO_OUT_OPTIONS = [
        '48000, 32 bit Floating Point', 
        '48000, 24 bit', 
        '48000, 16 bit',
        '44100, 32 bit Floating Point', 
        '44100, 24 bit', 
        '44100, 16 bit']
        
    _BEST_AUDIO_IN_OPTIONS = [ 
        '48000, 16 bit', 
        '44100, 16 bit'
        ]

    def __init__(self, configuration_manager):
        self._configuration_manager = configuration_manager
        self._current_config = None
        self._audio_setup = AudioSetup()
        self._drip_detector = None
    
    def current_printer(self):
        if self._current_config:
            return self._current_config['name']
        else:
            logging.debug('Current config missing')
            return None

    def get_current_config(self):
        return self._current_config

    def get_available_printers(self):
        return self._configuration_manager.list()

    def add_printer(self, name):
        self._current_config = self._configuration_manager.new(name)
        self.save()

    def load_printer(self, name):
        self._current_config = self._configuration_manager.load(name)
        logging.debug("Loaded config:\n%s" % self._current_config)
    
    def save(self):
        self._configuration_manager.save(self._current_config)

    # ----------------------------------- Audio Setup ------------------------------------------

    def get_available_audio_options(self):
        options = self._audio_setup.get_valid_sampling_options()
        inputs = dict([ (self._audio_as_plain_text(option), option) for option in options['input']])
        inputs = self._audio_mark_recommend(inputs, 'inputs')
        outputs = dict([ (self._audio_as_plain_text(option), option) for option in options['output']])
        outputs = self._audio_mark_recommend(outputs, 'outputs')
        return { 'inputs': inputs ,'outputs' : outputs}

    def _audio_as_plain_text(self, audio_option):
        return "%s, %s" % (audio_option['sample_rate'],audio_option['depth'])

    def _audio_mark_recommend(self, available_audio_settings, io_type):
        options = self._BEST_AUDIO_IN_OPTIONS if io_type == 'inputs' else self._BEST_AUDIO_OUT_OPTIONS
        for option in options:
            if available_audio_settings.has_key(option):
                available_audio_settings["%s (Recommended)" % option] = available_audio_settings[option]
                del available_audio_settings[option]
                return available_audio_settings
        return available_audio_settings

    def set_audio_output_options(self, sample_frequency,bit_depth):
        if sample_frequency == 44100:
            self._current_config['on_modulation_frequency'] = 11025
            self._current_config['off_modulation_frequency'] = 3675
        else:
            self._current_config['on_modulation_frequency'] = 12000
            self._current_config['off_modulation_frequency'] = 4000
        self._current_config['output_bit_depth'] = bit_depth
        self._current_config['output_sample_frequency'] = sample_frequency
        self.save()

    def set_audio_input_options(self,sample_frequency, bit_depth):
        self._current_config['input_bit_depth'] = bit_depth
        self._current_config['input_sample_frequency'] = sample_frequency
        self.save()

    # ------------------------------- Drip Setup --------------------------------------

    def get_drips(self):
        return self._drip_detector.current_z_location_mm()

    def mark_drips_at_target(self):
        if self._target_height != None:
            self._marked_drips = self.get_drips()
            self._current_config['drips_per_mm'] = self.get_drips_per_mm() 
        else:
            raise Exception("Target height must be specified before marking end point")

    def set_target_height(self,height_mm):
        try:
            if float(height_mm) > 0.0:
                self._target_height = float(height_mm)
            else:
                raise Exception("Target height must be a positive numeric value")
        except:
            raise Exception("Target height must be a positive numeric value")

    def reset_drips(self):
        self._drip_detector.reset(0)

    def get_drips_per_mm(self):
        return self._marked_drips / self._target_height

    def start_counting_drips(self, drip_call_back = None):
        self._drip_detector = DripBasedZAxis(
            1,
            sample_rate = self._current_config['input_sample_frequency'], 
            bit_depth = self._current_config['input_bit_depth'],
            drip_call_back = drip_call_back
            )
        self._drip_detector.start()

    def stop_counting_drips(self):
        if self._drip_detector:
            self._drip_detector.stop()
            self._drip_detector = None

    # ----------------------------- Calibration Setup ----------------------------------

    # ----------------------------- Cure Test Setup ------------------------------------
    
    # ----------------------------- General Setup --------------------------------------

    def get_laser_thickness_mm(self):
        return self._current_config['laser_thickness_mm']

    def set_laser_thickness_mm(self, thickness_mm):
        if (type(thickness_mm) == types.FloatType  and thickness_mm > 0.0):
            self._current_config['laser_thickness_mm'] = thickness_mm
            self.save()
        else:
            raise Exception("Laser thickness must be a positive floating point number")

    def get_sublayer_height_mm(self):
        return self._current_config['sublayer_height_mm']

    def set_sublayer_height_mm(self, thickness_mm):
        if (type(thickness_mm) == types.FloatType  and thickness_mm > 0.0):
            self._current_config['sublayer_height_mm'] = thickness_mm
            self.save()
        else:
            raise Exception("Sublayer height must be a positive floating point number")