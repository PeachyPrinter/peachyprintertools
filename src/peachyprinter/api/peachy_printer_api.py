from peachyprinter.api.configuration_api import ConfigurationAPI
from peachyprinter.api.calibration_api import CalibrationAPI
from peachyprinter.api.print_api import PrintAPI, PrintQueueAPI
from peachyprinter.api.test_print_api import TestPrintAPI

from peachyprinter.infrastructure.communicator import MissingPrinterException
from peachyprinter.infrastructure.configuration_manager import CircutSourcedConfigurationManager


class PrinterAPI(object):
    def __init__(self, ):

        self._configuration_manager = CircutSourcedConfigurationManager()
        self._configuration_api = ConfigurationAPI(self._configuration_manager)
        self._test_print_api = None


    '''Loads a connected printer'''
    def load_printer(self):
        self._configuration_api.load_printer()

    def current_printer(self):
        return self._configuration_api.current_printer()

    def get_print_api(self, start_height=0.0, status_call_back=None):
        return PrintAPI(self._configuration_api.get_current_config(), start_height=start_height, status_call_back=status_call_back)

    def get_print_queue_api(self, status_call_back=None):
        return PrintQueueAPI(self._configuration_api.get_current_config(), status_call_back=status_call_back)

    def get_calibration_api(self, ):
        return CalibrationAPI(self._configuration_manager)

    def get_configuration_api(self):
        return self._configuration_api

    def get_test_print_api(self, ):
        if not self._test_print_api:
            self._test_print_api = TestPrintAPI()
        return self._test_print_api
