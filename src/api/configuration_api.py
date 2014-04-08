

class ConfigurationAPI(object):
    def __init__(self, configuration_manager):
        self._configuration_manager = configuration_manager
        self._current_config = None
    
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

