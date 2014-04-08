#TODO JT 2014-04-08 - Domain Audio Setup
from infrastructure.audio import AudioSetup

class ConfigurationAPI(object):
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
        return self.audio_setup.get_valid_sampling_options()

    def set_audio_output_options(self, sample_frequency,bit_depth):
        pass

    def set_audio_input_options(self,sample_frequency, bit_depth):
        pass

