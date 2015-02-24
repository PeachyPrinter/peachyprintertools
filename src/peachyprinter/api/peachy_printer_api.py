from peachyprinter.infrastructure.configuration import FileBasedConfigurationManager
from peachyprinter.api.configuration_api import ConfigurationAPI
from peachyprinter.api.calibration_api import CalibrationAPI
from peachyprinter.api.print_api import PrintAPI
from peachyprinter.api.test_print_api import TestPrintAPI

class PrinterAPI(object):
    def __init__(self, ):

        self._configuration_manager = FileBasedConfigurationManager()
        self._configuration_api = ConfigurationAPI(self._configuration_manager)
        self._test_print_api = None

    '''Returns a list of available printers'''
    def get_available_printers(self):
        return self._configuration_manager.list()

    '''Adds a printer by name with default settings'''
    def add_printer(self, name):
        self._configuration_api.add_printer(name)

    '''Loads a previous configured printer by name'''
    def load_printer(self, name):
        self._configuration_api.load_printer(name)

    def get_print_api(self, callback=None):
        return PrintAPI(self._configuration_api.get_current_config(), status_call_back=callback)

    def get_calibration_api(self, ):
        return CalibrationAPI(self._configuration_api.get_current_config())

    def get_configuration_api(self, ):
       return self._configuration_api

    def get_test_print_api(self, ):
        if not self._test_print_api:
            self._test_print_api = TestPrintAPI()
        return self._test_print_api