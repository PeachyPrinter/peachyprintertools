from peachyprinter.infrastructure.configuration import FileBasedConfigurationManager
from peachyprinter.api.configuration_api import ConfigurationAPI

class PrinterAPI(object):
    def __init__(self, ):
        self._configuration_manager = FileBasedConfigurationManager()
        self._configuration_api = ConfigurationAPI(self._configuration_manager)

    '''Returns the current printer config in json'''
    def get_current_config(self):
        return self._configuration_api._current_config

    '''Returns a list of available printers'''
    def get_available_printers(self):
        return self._configuration_manager.list()

    '''Adds a printer by name with default settings'''
    def add_printer(self, name):
        self._configuration_api.add_printer(name)

    '''Loads a previous configured printer by name'''
    def load_printer(self, name):
        self._configuration_api.load_printer(name)

    def get_print_api(self, ):
        pass

    def get_calibration_api(self, ):
        pass

    def get_configuration_api(self, ):
       return self._configuration_api

    def get_test_print_api(self, ):
        pass
