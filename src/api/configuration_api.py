#TODO JT 2014-04-08 - Domain Audio Setup
from infrastructure.audio import AudioSetup
from infrastructure.audio import human_readable_depths

class ConfigurationAPI(object):
    _BEST_AUDIO_OPTIONS = [
        '48000, 32 bit Floating Point', 
        '48000, 24 bit', 
        '48000, 16 bit',
        '44100, 32 bit Floating Point', 
        '44100, 24 bit', 
        '44100, 16 bit']
    def __init__(self, configuration_manager):
        self._configuration_manager = configuration_manager
        self._current_config = None
        self.audio_setup = AudioSetup()
    
    def current_printer(self):
        if self._current_config:
            self._current_config[u'name']
        else:
            return None

    def get_available_printers(self):
        return self._configuration_manager.list()

    def add_printer(self, name):
        self._current_config = self._configuration_manager.new(name)
        self.save()

    def load_printer(self, name):
        self._current_config = self._configuration_manager.load(name)
    
    def save(self):
        self._configuration_manager.save(self._current_config)

    def get_available_audio_options(self):
        options = self.audio_setup.get_valid_sampling_options()
        inputs = dict([ (self._audio_as_plain_text(option), option) for option in options['input']])
        inputs = self._audio_mark_recommend(inputs)
        outputs = dict([ (self._audio_as_plain_text(option), option) for option in options['output']])
        outputs = self._audio_mark_recommend(outputs)
        return { 'inputs': inputs ,'outputs' : outputs}

    def _audio_as_plain_text(self, audio_option):
        return "%s, %s" % (audio_option['sample_rate'],human_readable_depths[audio_option['depth']])

    def _audio_mark_recommend(self, available_audio_settings):
        for option in self._BEST_AUDIO_OPTIONS:
            if available_audio_settings.has_key(option):
                available_audio_settings["%s (Recommended)" % option] = available_audio_settings[option]
                del available_audio_settings[option]
                return available_audio_settings
        return available_audio_settings

    def set_audio_output_options(self, sample_frequency,bit_depth):
        if sample_frequency == 44100:
            self._current_config[u'on_modulation_frequency'] = 11025
            self._current_config[u'off_modulation_frequency'] = 3675
        else:
            self._current_config[u'on_modulation_frequency'] = 12000
            self._current_config[u'off_modulation_frequency'] = 8000
        self._current_config[u'output_bit_depth'] = bit_depth
        self._current_config[u'output_sample_frequency'] = sample_frequency
        self.save()

    def set_audio_input_options(self,sample_frequency, bit_depth):
        self._current_config[u'input_bit_depth'] = bit_depth
        self._current_config[u'input_sample_frequency'] = sample_frequency
        self.save()

