import unittest
import os
import sys
import json

from StringIO import StringIO

from mock import patch, MagicMock, mock_open

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from peachyprinter.infrastructure.configuration_manager import *
from peachyprinter.infrastructure.messages import IAmMessage
from peachyprinter.infrastructure.communicator import MissingPrinterException

import test_helpers


class CircutSourcedConfigurationManagerTests(unittest.TestCase, test_helpers.TestHelpers):
    def test_new_should_raise_exception(self):
        cscm = CircutSourcedConfigurationManager()
        with self.assertRaises(Exception):
            cscm.new("Phish")

    def test_load_requires_None_for_printer_name(self):
        cscm = CircutSourcedConfigurationManager()
        with self.assertRaises(Exception):
            cscm.load("Phish")

    @patch.object(os.path, 'exists')
    @patch.object(os.path, 'isfile')
    @patch('peachyprinter.infrastructure.configuration_manager.UsbPacketCommunicator')
    def test_load_should_load_printer_based_on_returned_serial(self, mock_UsbPacketCommunicator, mock_isfile, mock_exists):
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_communicator = mock_UsbPacketCommunicator.return_value
        expected_config = self.default_config
        printer_name = 'sn'
        expected_config.name = printer_name

        expected_path = os.path.join(os.path.expanduser('~'), '.peachyprintertools', 'sn.cfg')
        mocked_open = mock_open(read_data=expected_config.toJson())

        with patch('peachyprinter.infrastructure.configuration_manager.open', mocked_open, create=True):
            cscm = CircutSourcedConfigurationManager()
            def side_effect(self):
                cscm._ident_call_back(IAmMessage('swrev', 'hwrev', printer_name, 9600))

            mock_communicator.send.side_effect = side_effect
            actual = cscm.load()

            self.assertEquals(printer_name, actual.name)
            self.assertEquals(mocked_open.call_args_list[0][0][0], expected_path)
            mock_communicator.start.assert_called_with()
            mock_communicator.register_handler.assert_called_with(IAmMessage,cscm._ident_call_back)
            mock_communicator.stop.assert_called_with()
            
    @patch.object(os.path, 'exists')
    @patch.object(os.path, 'isfile')
    @patch.object(os, 'makedirs')
    @patch('peachyprinter.infrastructure.configuration_manager.UsbPacketCommunicator')
    def test_load_should_create_a_printer_config_if_none_exists(self, mock_UsbPacketCommunicator, mock_makedirs, mock_isfile, mock_exists):
        mock_exists.return_value = False
        mock_isfile.return_value = False
        mock_communicator = mock_UsbPacketCommunicator.return_value
        
        expected_path = os.path.join(os.path.expanduser('~'), '.peachyprintertools', 'sn.cfg')
        mocked_open = mock_open()
        
        with patch('peachyprinter.infrastructure.configuration_manager.open', mocked_open, create=True):
            cscm = CircutSourcedConfigurationManager()
            def side_effect(self):
                cscm._ident_call_back(IAmMessage('swrev', 'hwrev', 'sn', 9600))

            mock_communicator.send.side_effect = side_effect
            cscm.load()

            mock_makedirs.assert_called_with(os.path.join(os.path.expanduser('~'), '.peachyprintertools',))
            mocked_open.assert_called_with(expected_path,'w')

    @patch.object(os.path, 'exists')
    @patch.object(os.path, 'isfile')
    @patch('peachyprinter.infrastructure.configuration_manager.UsbPacketCommunicator')
    def test_load_should_load_printer_and_update_circut_values(self, mock_UsbPacketCommunicator, mock_isfile, mock_exists):
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_communicator = mock_UsbPacketCommunicator.return_value
        expected_config = self.default_config
        printer_name = 'sn'
        hardware_rev = "hhhwhwh"
        software_rev = "hhhwhwh"
        data_rate = 9999

        expected_config.name = printer_name

        expected_path = os.path.join(os.path.expanduser('~'), '.peachyprintertools', 'sn.cfg')
        mocked_open = mock_open(read_data=expected_config.toJson())
        
        with patch('peachyprinter.infrastructure.configuration_manager.open', mocked_open, create=True):
            cscm = CircutSourcedConfigurationManager()
            def side_effect(self):
                cscm._ident_call_back(IAmMessage(software_rev, hardware_rev, printer_name, data_rate))

            mock_communicator.send.side_effect = side_effect
            actual = cscm.load()

            self.assertEquals(printer_name, actual.name)
            self.assertEquals(actual.circut.software_revision, software_rev)
            self.assertEquals(actual.circut.hardware_revision, hardware_rev)
            self.assertEquals(actual.circut.serial_number, printer_name)
            self.assertEquals(actual.circut.data_rate, data_rate)

    @patch.object(os.path, 'exists')
    @patch.object(os.path, 'isfile')
    @patch('peachyprinter.infrastructure.configuration_manager.UsbPacketCommunicator')
    def test_load_should_raise_if_communictor_raises(self, mock_UsbPacketCommunicator, mock_isfile, mock_exists):
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_communicator = mock_UsbPacketCommunicator.return_value
        expected_config = self.default_config
        printer_name = 'sn'
        hardware_rev = "hhhwhwh"
        software_rev = "hhhwhwh"
        data_rate = 9999

        expected_config.name = printer_name

        expected_path = os.path.join(os.path.expanduser('~'), '.peachyprintertools', 'sn.cfg')
        mocked_open = mock_open(read_data=expected_config.toJson())

        with patch('peachyprinter.infrastructure.configuration_manager.open', mocked_open, create=True):
            cscm = CircutSourcedConfigurationManager()
            def side_effect():
                raise MissingPrinterException()

            mock_communicator.start.side_effect = side_effect
            with self.assertRaises(MissingPrinterException):
                cscm.load()

if __name__ == '__main__':
    unittest.main()