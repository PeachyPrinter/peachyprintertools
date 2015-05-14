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

import test_helpers


# class FileBasedConfigurationManagerTests(unittest.TestCase,test_helpers.TestHelpers):
#     maxDiff = None
#     def test_new_creates_a_new_configution_dict_with_sane_values(self):
#         cm = FileBasedConfigurationManager()

#         actual =  cm.new('Peachy Printer')
#         expected = self.default_config
#         self.assertConfigurationEqual(expected, actual)

#     @patch.object(os.path, 'exists')
#     @patch.object(os, 'makedirs')
#     def test_save_printers_configuration_dictionary_to_peachyprintertools_folder_in_home(self, mock_makedirs,mock_exists):
#         mock_exists.return_value = True
#         printer_name = 'Test1'
#         expected_path = os.path.join(os.path.expanduser('~'), '.peachyprintertools', printer_name + '.cfg')
#         mocked_open = mock_open(read_data=self.default_config.toJson())
#         with patch('peachyprinter.infrastructure.configuration.open', mocked_open, create=True):
#             cm = FileBasedConfigurationManager()
#             data = cm.new(printer_name)
#             expected_data = data.toJson()
#             cm.save(data)

#         self.assertFalse(mock_makedirs.called)
#         mocked_open.assert_called_with(expected_path, 'w')
#         mocked_open().write.assert_called_with(expected_data)

#     @patch.object(os.path, 'exists')
#     @patch.object(os, 'makedirs')
#     def test_save_should_create_data_folder_if_it_does_not_exist(self,mock_makedirs,mock_exists):
#         mock_exists.return_value = False
#         expected_path =  expected_path = os.path.join(os.path.expanduser('~'), '.peachyprintertools')
#         with patch('peachyprinter.infrastructure.configuration.open', create=True) as mock_open:
#             mock_open.return_value = MagicMock(spec=file)
#             cm = FileBasedConfigurationManager()
#             data = cm.new('Test1')

#             cm.save(data)

#         mock_makedirs.assert_called_with(expected_path)

#     @patch.object(os.path, 'exists')
#     def test_list_should_return_empty_list_when_folder_doesnt_exist(self, mock_exists):
#         mock_exists.return_value = False
#         with patch('peachyprinter.infrastructure.configuration.open', create=True) as mock_open:
#             cm = FileBasedConfigurationManager()
#             self.assertEquals([] , cm.list())

#     @patch.object(os.path, 'exists')
#     @patch.object(os, 'listdir')
#     def test_list_should_return_empty_list_when_folder_contains_no_configurations(self, mock_listdir, mock_exists):
#         mock_exists.return_value = True
#         mock_listdir.return_value = []
#         with patch('peachyprinter.infrastructure.configuration.open', create=True) as mock_open:
#             cm = FileBasedConfigurationManager()
#             self.assertEquals([] , cm.list())

#     @patch.object(os.path, 'exists')
#     @patch.object(os, 'listdir')
#     def test_list_should_return_name_of_configurations(self, mock_listdir, mock_exists):
#         mock_exists.return_value = True
#         mock_listdir.return_value = [ 'blabla.cfg' ]
#         expected = [ self.default_config.name ]
#         mocked_open = mock_open(read_data=self.default_config.toJson())
#         with patch('peachyprinter.infrastructure.configuration.open', mocked_open, create=True):
#             cm = FileBasedConfigurationManager()

#             actual = cm.list()

#             self.assertEquals(expected, actual)

#     @patch.object(os.path, 'exists')
#     @patch.object(os, 'listdir')
#     def test_list_should_only_process_cfg_files(self, mock_listdir, mock_exists):
#         mock_exists.return_value = True
#         mock_listdir.return_value = [ 'blabla.cow' ]
#         expected = [ ]
#         mocked_open = mock_open(read_data=self.default_config.toJson())
#         with patch('peachyprinter.infrastructure.configuration.open', mocked_open, create=True):
#             cm = FileBasedConfigurationManager()
#             actual = cm.list()
#             self.assertEquals(expected, actual)

#     @patch.object(os.path, 'exists')
#     @patch.object(os, 'listdir')
#     @patch.object(os, 'makedirs')
#     def test_load_should_throw_exception_not_there(self, mock_makedirs, mock_listdir, mock_exists):
#         mock_exists.return_value = False
#         mocked_open = mock_open()
#         with patch('peachyprinter.infrastructure.configuration.open', mocked_open, create=True):
#             cm = FileBasedConfigurationManager()
#             with self.assertRaises(Exception):
#                 cm.load(u"Not There")

#     @patch.object(os.path, 'exists')
#     def test_load_should_throw_exception_if_bad_data(self,  mock_exists):
#         mock_exists.return_value = True
#         with patch('peachyprinter.infrastructure.configuration.open', create=True) as mock_open:
#             manager = mock_open.return_value.__enter__.return_value
#             manager.read.return_value = StringIO("ASDFASDFASD")
#             cm = FileBasedConfigurationManager()

#             with self.assertRaises(Exception):
#                 cm.load(u"Some Printer")

#     @patch.object(os.path, 'exists')
#     def test_load_should_load_data(self,mock_exists):
#         mock_exists.return_value = True
        
#         expected = self.default_config
#         mocked_open = mock_open(read_data=self.default_config.toJson())
        
#         with patch('peachyprinter.infrastructure.configuration.open', mocked_open, create=True):
#             cm = FileBasedConfigurationManager()
#             actual = cm.load('Some Printer')
#             self.assertConfigurationEqual(expected, actual)

#     @patch.object(os.path, 'exists')
#     def test_load_should_populate_empty_data_with_defaults(self,mock_exists):
#         mock_exists.return_value = True
        
#         expected = self.default_config
#         missing = self.default_config.toJson()
#         tmp = json.loads(missing)

#         del tmp['name']
#         del tmp['options']['sublayer_height_mm']
#         del tmp['options']['laser_thickness_mm']
#         del tmp['options']['scaling_factor']
#         del tmp['options']['overlap_amount']
#         del tmp['options']['use_shufflelayers']
#         del tmp['options']['use_sublayers']
#         del tmp['options']['use_overlap']
#         del tmp['options']['print_queue_delay']
#         del tmp['options']['pre_layer_delay']
#         del tmp['options']['wait_after_move_milliseconds']
#         del tmp['dripper']['drips_per_mm']
#         del tmp['dripper']['max_lead_distance_mm']
#         del tmp['dripper']['dripper_type']
#         del tmp['dripper']['emulated_drips_per_second']
#         del tmp['dripper']['photo_zaxis_delay']
#         del tmp['calibration']['max_deflection']
#         del tmp['calibration']['height']
#         del tmp['calibration']['lower_points']
#         del tmp['calibration']['upper_points']
#         del tmp['serial']['on']
#         del tmp['serial']['port']
#         del tmp['serial']['on_command']
#         del tmp['serial']['off_command']
#         del tmp['serial']['layer_started']
#         del tmp['serial']['layer_ended']
#         del tmp['serial']['print_ended']
#         del tmp['email']['on']
#         del tmp['email']['port']
#         del tmp['email']['host']
#         del tmp['email']['sender']
#         del tmp['email']['recipient']
#         del tmp['cure_rate']['base_height']
#         del tmp['cure_rate']['total_height']
#         del tmp['cure_rate']['start_speed']
#         del tmp['cure_rate']['finish_speed']
#         del tmp['cure_rate']['draw_speed']
#         del tmp['cure_rate']['use_draw_speed']

#         missing = json.dumps(tmp)

#         mocked_open = mock_open(read_data=missing)
        
#         with patch('peachyprinter.infrastructure.configuration.open', mocked_open, create=True):
#             cm = FileBasedConfigurationManager()
#             actual = cm.load('Some Printer')
#             self.assertConfigurationEqual(expected, actual)

#     def test_new_should_return_a_config_with_defaults_and_correct_name(self):
#         name = "Apple"
#         expected = self.default_config
#         expected.name = name
#         cm = FileBasedConfigurationManager()
        
#         actual = cm.new(name)

#         self.assertConfigurationEqual(expected,actual)


class CircutSourcedConfigurationManagerTests(unittest.TestCase, test_helpers.TestHelpers):
    # def test_new_should_raise_exception(self):
    #     cscm = CircutSourcedConfigurationManager()
    #     with self.assertRaises(Exception):
    #         cscm.new("Phish")

    # def test_load_requires_None_for_printer_name(self):
    #     cscm = CircutSourcedConfigurationManager()
    #     with self.assertRaises(Exception):
    #         cscm.load("Phish")

    # @patch.object(os.path, 'exists')
    # @patch.object(os.path, 'isfile')
    # @patch('peachyprinter.infrastructure.configuration_manager.UsbPacketCommunicator')
    # def test_load_should_load_printer_based_on_returned_serial(self, mock_UsbPacketCommunicator, mock_isfile, mock_exists):
    #     mock_exists.return_value = True
    #     mock_isfile.return_value = True
    #     mock_communicator = mock_UsbPacketCommunicator.return_value
    #     expected_config = self.default_config
    #     printer_name = 'sn'
    #     expected_config.name = printer_name

    #     expected_path = os.path.join(os.path.expanduser('~'), '.peachyprintertools', 'sn.cfg')
    #     mocked_open = mock_open(read_data=expected_config.toJson())
        
    #     with patch('peachyprinter.infrastructure.configuration_manager.open', mocked_open, create=True):
    #         cscm = CircutSourcedConfigurationManager()
    #         def side_effect(self):
    #             cscm._ident_call_back(IAmMessage('swrev', 'hwrev', printer_name, 9600))

    #         mock_communicator.send.side_effect = side_effect
    #         actual = cscm.load()

    #         self.assertEquals(printer_name, actual.name)
    #         self.assertEquals(mocked_open.call_args_list[0][0][0], expected_path)
    #         mock_communicator.start.assert_called_with()
    #         mock_communicator.register_handler.assert_called_with(IAmMessage,cscm._ident_call_back)
    #         mock_communicator.stop.assert_called_with()
            
    # @patch.object(os.path, 'exists')
    # @patch.object(os.path, 'isfile')
    # @patch.object(os, 'makedirs')
    # @patch('peachyprinter.infrastructure.configuration_manager.UsbPacketCommunicator')
    # def test_load_should_create_a_printer_config_if_none_exists(self, mock_UsbPacketCommunicator, mock_makedirs, mock_isfile, mock_exists):
    #     mock_exists.return_value = False
    #     mock_isfile.return_value = False
    #     mock_communicator = mock_UsbPacketCommunicator.return_value
        
    #     expected_path = os.path.join(os.path.expanduser('~'), '.peachyprintertools', 'sn.cfg')
    #     mocked_open = mock_open()
        
    #     with patch('peachyprinter.infrastructure.configuration_manager.open', mocked_open, create=True):
    #         cscm = CircutSourcedConfigurationManager()
    #         def side_effect(self):
    #             cscm._ident_call_back(IAmMessage('swrev', 'hwrev', 'sn', 9600))

    #         mock_communicator.send.side_effect = side_effect
    #         actual_config = cscm.load()

    #         mock_makedirs.assert_called_with(os.path.join(os.path.expanduser('~'), '.peachyprintertools',))
    #         mocked_open.assert_called_with(expected_path,'w')

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
            self.assertEquals(actual.circut.software_revision, printer_name)
            self.assertEquals(actual.circut.hardware_revision, hardware_rev)
            self.assertEquals(actual.circut.serial_number, software_rev)
            self.assertEquals(actual.circut.data_rate, data_rate)



if __name__ == '__main__':
    unittest.main()