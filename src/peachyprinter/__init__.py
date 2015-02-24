__configuration_manager = None
from peachyprinter.api.print_api import PrintAPI
from peachyprinter.api.configuration_api import ConfigurationAPI

def _configuration_manager():
    global __configuration_manager
    if not __configuration_manager:
        from peachyprinter.infrastructure.configuration import FileBasedConfigurationManager
        __configuration_manager = FileBasedConfigurationManager()
    return __configuration_manager

def list_printers():
    return _configuration_manager().list()

def load_printer(name):
    return Printer(_configuration_manager().load(name))


class Printer(object):
    def __init__(self, configuration):
        self.configuration = configuration

    def get_print_api(self, start_height=0.0, callback=None):
        return PrintAPI(self.configuration, start_height=start_height, status_call_back=callback)

    def get_print_queue_api(self,bla):
        pass

    def get_configuration_api(self):
        cfg = ConfigurationAPI(self.configuration)
        cfg.load_printer()

    def get_calibration_api(self, bla):
        pass



