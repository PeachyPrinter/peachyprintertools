import unittest
import os
import sys
import json
import hashlib
from StringIO import StringIO

from mock import patch

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from api.configuration_api import ConfigurationAPI
from domain.configuration_manager import ConfigurationManager

class ConfigurationAPITest(unittest.TestCase):

    @patch.object(ConfigurationManager, 'new' )
    @patch.object(ConfigurationManager, 'save' )
    def test_add_printer_should_save_itself(self, mock_save, mock_new):
        capi = ConfigurationAPI(ConfigurationManager())
        mock_new.return_value = "Some Printer Config"

        capi.add_printer("NewName")

        mock_new.assert_called_with("NewName")
        mock_save.assert_called_with("Some Printer Config")

    @patch.object(ConfigurationManager, 'list' )
    def test_get_available_printers_lists_printers(self, mock_list):
        printers = ['Tom','Dick','Harry']
        capi = ConfigurationAPI(ConfigurationManager())
        mock_list.return_value = printers

        actual = capi.get_available_printers()

        mock_list.assert_called_with()
        self.assertEqual(printers,actual)

    def test_current_printer_returns_none_when_no_printer_loaded(self):
        capi = ConfigurationAPI(ConfigurationManager())
        
        actual = capi.current_printer()

        self.assertEqual(None, actual)

    def test_current_printer_returns_printer_name(self):
        capi = ConfigurationAPI(ConfigurationManager())
        
        actual = capi.current_printer()

        self.assertEqual(None, actual)

    @patch.object(ConfigurationManager, 'load' )
    def test_load_printer_calls_load(self, mock_load):
        printer_name = u'MegaPrint'
        mock_load.return_value = { u'name':printer_name}
        capi = ConfigurationAPI(ConfigurationManager())
        
        capi.load_printer(printer_name)

        mock_load.assert_called_with(printer_name)

    @patch.object(ConfigurationManager, 'load' )
    def test_cannot_add_printer_that_already_exists(self, mock_load):
        printer_name = u'MegaPrint'
        mock_load.return_value = { u'name':printer_name }
        capi = ConfigurationAPI(ConfigurationManager())
        capi.load_printer(printer_name)
        
        actual = capi.current_printer()

        self.assertEqual(printer_name, actual)

    def test_cannot_add_printer_that_already_exists(self):
        pass


if __name__ == '__main__':
    unittest.main()