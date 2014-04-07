

class ConfigurationAPI(object):
    def __init__(self, configuration_manager):
        self._configuration_manager = configuration_manager
        self._current_config = None

    def get_available_printers(self):
        return self._configuration_manager.list()

    def add_printer(self, name):
        self._current_config = self._configuration_manager.new(name)

    def load_printer(self, name):
        pass
    
    def save(self, name):
        pass

