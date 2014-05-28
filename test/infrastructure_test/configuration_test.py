import unittest
import os
import sys
import json
import hashlib

from StringIO import StringIO

from mock import patch, MagicMock,mock_open

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from infrastructure.configuration import FileBasedConfigurationManager as ConfigurationManager
from infrastructure.configuration import Configuration, ConfigurationGenerator
import test_helpers

class ConfigurationTests(unittest.TestCase,test_helpers.TestHelpers):
    def test_can_set_and_get_values(self):
        expected_name = "PP"
        expected_output_bit_depth = "16"
        expected_output_sample_frequency =  48000
        expected_on_modulation_frequency = 8000
        expected_off_modulation_frequency = 2000
        expected_input_bit_depth = "8"
        expected_input_sample_frequency = 4800
        expected_sublayer_height_mm = 0.
        expected_laser_thickness_mm = 0.1
        expected_drips_per_mm = 10.1
        expected_max_deflection = 75.2
        expected_calibration_height = 1.0
        expected_calibration_lower_points = { (1.0, 1.0):( 1.0,  1.0), (0.0, 1.0):(-1.0,  1.0), (1.0, 0.0):( 1.0, -1.0), (0.0, 0.0):(-1.0, -1.0) }
        expected_calibration_upper_points = { (1.0, 1.0):( 1.0,  1.0), (0.0, 1.0):(-1.0,  1.0), (1.0, 0.0):( 1.0, -1.0), (0.0, 0.0):(-1.0, -1.0) }
        expected_draw_speed = 2.0
        expected_max_lead_distance_mm = 0.2
        expected_use_serial_zaxis = True
        expected_serial_port = "COM2"
        expected_serial_on = "12"
        expected_serial_off = "13"
        expected_laser_offset = [ 0.1, 0.1]
        config = Configuration()

        config.name                                 = expected_name
        config.audio.output.bit_depth               = expected_output_bit_depth
        config.audio.output.sample_rate             = expected_output_sample_frequency
        config.audio.output.modulation_on_frequency = expected_on_modulation_frequency
        config.audio.output.modulation_off_frequency= expected_off_modulation_frequency
        config.audio.input.bit_depth                = expected_input_bit_depth
        config.audio.input.sample_rate              = expected_input_sample_frequency
        config.options.sublayer_height_mm           = expected_sublayer_height_mm
        config.options.laser_thickness_mm           = expected_laser_thickness_mm
        config.dripper.drips_per_mm                 = expected_drips_per_mm
        config.calibration.max_deflection           = expected_max_deflection
        config.calibration.height                   = expected_calibration_height
        config.calibration.lower_points             = expected_calibration_lower_points
        config.calibration.upper_points             = expected_calibration_upper_points
        config.options.draw_speed                   = expected_draw_speed
        config.dripper.max_lead_distance_mm         = expected_max_lead_distance_mm
        config.serial.on                            = expected_use_serial_zaxis
        config.serial.port                          = expected_serial_port
        config.serial.on_command                    = expected_serial_on
        config.serial.off_command                   = expected_serial_off
        config.options.laser_offset                 = expected_laser_offset

        self.assertEquals(expected_name, config.name )
        self.assertEquals(expected_output_bit_depth, config.audio.output.bit_depth )
        self.assertEquals(expected_output_sample_frequency, config.audio.output.sample_rate )
        self.assertEquals(expected_on_modulation_frequency, config.audio.output.modulation_on_frequency )
        self.assertEquals(expected_off_modulation_frequency, config.audio.output.modulation_off_frequency )
        self.assertEquals(expected_input_bit_depth, config.audio.input.bit_depth )
        self.assertEquals(expected_input_sample_frequency, config.audio.input.sample_rate )
        self.assertEquals(expected_sublayer_height_mm, config.options.sublayer_height_mm )
        self.assertEquals(expected_laser_thickness_mm, config.options.laser_thickness_mm )
        self.assertEquals(expected_drips_per_mm, config.dripper.drips_per_mm )
        self.assertEquals(expected_max_deflection, config.calibration.max_deflection )
        self.assertEquals(expected_calibration_height, config.calibration.height )
        self.assertEquals(expected_calibration_lower_points, config.calibration.lower_points )
        self.assertEquals(expected_calibration_upper_points, config.calibration.upper_points )
        self.assertEquals(expected_draw_speed, config.options.draw_speed )
        self.assertEquals(expected_max_lead_distance_mm, config.dripper.max_lead_distance_mm )
        self.assertEquals(expected_use_serial_zaxis, config.serial.on )
        self.assertEquals(expected_serial_port, config.serial.port )
        self.assertEquals(expected_serial_on, config.serial.on_command )
        self.assertEquals(expected_serial_off, config.serial.off_command )
        self.assertEquals(expected_laser_offset, config.options.laser_offset )

    def test_set_should_fail_for_incorrect_values(self):
        expected_name = True
        expected_output_bit_depth = True
        expected_output_sample_frequency = True
        expected_on_modulation_frequency = True
        expected_off_modulation_frequency = True
        expected_input_bit_depth = True
        expected_input_sample_frequency = True
        expected_sublayer_height_mm = True
        expected_laser_thickness_mm = True
        expected_drips_per_mm = True
        expected_max_deflection = True
        expected_calibration_height = True
        expected_calibration_lower_points = True
        expected_calibration_upper_points = True
        expected_draw_speed = True
        expected_max_lead_distance_mm = True
        expected_use_serial_zaxis = "!@#!@#"
        expected_serial_port = True
        expected_serial_on = True
        expected_serial_off = True
        expected_laser_offset = True
        config = Configuration()

        with self.assertRaises(Exception):
            config.name = expected_name
        with self.assertRaises(Exception):
            config.audio.output.bit_depth = expected_output_bit_depth
        with self.assertRaises(Exception):
            config.audio.output.sample_rate = expected_output_sample_frequency
        with self.assertRaises(Exception):
            config.audio.output.modulation_on_frequency = expected_on_modulation_frequency
        with self.assertRaises(Exception):
            config.audio.output.modulation_off_frequency = expected_off_modulation_frequency
        with self.assertRaises(Exception):
            config.audio.input.bit_depth = expected_input_bit_depth
        with self.assertRaises(Exception):
            config.audio.input.sample_rate = expected_input_sample_frequency
        with self.assertRaises(Exception):
            config.options.sublayer_height_mm = expected_sublayer_height_mm
        with self.assertRaises(Exception):
            config.options.laser_thickness_mm = expected_laser_thickness_mm
        with self.assertRaises(Exception):
            config.dripper.drips_per_mm = expected_drips_per_mm
        with self.assertRaises(Exception):
            config.calibration.max_deflection = expected_max_deflection
        with self.assertRaises(Exception):
            config.calibration.height = expected_calibration_height
        with self.assertRaises(Exception):
            config.calibration.lower_points = expected_calibration_lower_points
        with self.assertRaises(Exception):
            config.calibration.upper_points = expected_calibration_upper_points
        with self.assertRaises(Exception):
            config.options.draw_speed = expected_draw_speed
        with self.assertRaises(Exception):
            config.dripper.max_lead_distance_mm = expected_max_lead_distance_mm
        with self.assertRaises(Exception):
            config.serial.on = expected_use_serial_zaxis
        with self.assertRaises(Exception):
            config.serial.port = expected_serial_port
        with self.assertRaises(Exception):
            config.serial.on_command = expected_serial_on
        with self.assertRaises(Exception):
            config.serial.off_command = expected_serial_off
        with self.assertRaises(Exception):
            config.options.laser_offset = expected_laser_offset

    def test_can_create_json(self):
        expected_name = "PP"
        expected_output_bit_depth = "16"
        expected_output_sample_frequency =  48000
        expected_on_modulation_frequency = 8000
        expected_off_modulation_frequency = 2000
        expected_input_bit_depth = "8"
        expected_input_sample_frequency = 4800
        expected_sublayer_height_mm = 0.
        expected_laser_thickness_mm = 0.1
        expected_drips_per_mm = 10.1
        expected_max_deflection = 75.2
        expected_calibration_height = 1.0
        expected_calibration_lower_points = { (1.0, 1.0):( 1.0,  1.0), (0.0, 1.0):(-1.0,  1.0), (1.0, 0.0):( 1.0, -1.0), (0.0, 0.0):(-1.0, -1.0) }
        expected_calibration_upper_points = { (1.0, 1.0):( 1.0,  1.0), (0.0, 1.0):(-1.0,  1.0), (1.0, 0.0):( 1.0, -1.0), (0.0, 0.0):(-1.0, -1.0) }
        expected_draw_speed = 2.0
        expected_max_lead_distance_mm = 0.2
        expected_use_serial_zaxis = True
        expected_serial_port = "COM2"
        expected_serial_on = "12"
        expected_serial_off = "13"
        expected_laser_offset = [ 0.1, 0.1]
        config = Configuration()

        config.name                                 = expected_name
        config.audio.output.bit_depth               = expected_output_bit_depth
        config.audio.output.sample_rate             = expected_output_sample_frequency
        config.audio.output.modulation_on_frequency = expected_on_modulation_frequency
        config.audio.output.modulation_off_frequency= expected_off_modulation_frequency
        config.audio.input.bit_depth                = expected_input_bit_depth
        config.audio.input.sample_rate              = expected_input_sample_frequency
        config.options.sublayer_height_mm           = expected_sublayer_height_mm
        config.options.laser_thickness_mm           = expected_laser_thickness_mm
        config.dripper.drips_per_mm                 = expected_drips_per_mm
        config.calibration.max_deflection           = expected_max_deflection
        config.calibration.height                   = expected_calibration_height
        config.calibration.lower_points             = expected_calibration_lower_points
        config.calibration.upper_points             = expected_calibration_upper_points
        config.options.draw_speed                   = expected_draw_speed
        config.dripper.max_lead_distance_mm         = expected_max_lead_distance_mm
        config.serial.on                            = expected_use_serial_zaxis
        config.serial.port                          = expected_serial_port
        config.serial.on_command                    = expected_serial_on
        config.serial.off_command                   = expected_serial_off
        config.options.laser_offset                 = expected_laser_offset

        expected_json = json.loads('{"name": "PP", "calibration": {"max_deflection": 75.2, "upper_points": [[[0.0, 1.0], [-1.0, 1.0]], [[1.0, 0.0], [1.0, -1.0]], [[0.0, 0.0], [-1.0, -1.0]], [[1.0, 1.0], [1.0, 1.0]]], "lower_points": [[[0.0, 1.0], [-1.0, 1.0]], [[1.0, 0.0], [1.0, -1.0]], [[0.0, 0.0], [-1.0, -1.0]], [[1.0, 1.0], [1.0, 1.0]]], "height": 1.0 }, "dripper": {"max_lead_distance_mm": 0.2, "drips_per_mm": 10.1}, "serial": {"on": true, "on_command": "12", "port": "COM2", "off_command": "13"}, "audio": {"input": {"bit_depth": "8", "sample_rate": 4800}, "output": {"bit_depth": "16", "modulation_off_frequency": 2000, "sample_rate": 48000, "modulation_on_frequency": 8000}}, "options": {"laser_offset": [0.1, 0.1], "sublayer_height_mm": 0.0, "draw_speed": 2.0, "laser_thickness_mm": 0.1}}')

        actual_json = json.loads(config.toJson())
        self.assertDictEqual(expected_json, actual_json)

    def test_can_load_from_json(self):
        expected_name = "PP"
        expected_output_bit_depth = "16"
        expected_output_sample_frequency =  48000
        expected_on_modulation_frequency = 8000
        expected_off_modulation_frequency = 2000
        expected_input_bit_depth = "8"
        expected_input_sample_frequency = 4800
        expected_sublayer_height_mm = 0.
        expected_laser_thickness_mm = 0.1
        expected_drips_per_mm = 10.1
        expected_max_deflection = 75.2
        expected_calibration_height = 1.0
        expected_calibration_lower_points = { (1.0, 1.0):( 1.0,  1.0), (0.0, 1.0):(-1.0,  1.0), (1.0, 0.0):( 1.0, -1.0), (0.0, 0.0):(-1.0, -1.0) }
        expected_calibration_upper_points = { (1.0, 1.0):( 1.0,  1.0), (0.0, 1.0):(-1.0,  1.0), (1.0, 0.0):( 1.0, -1.0), (0.0, 0.0):(-1.0, -1.0) }
        expected_draw_speed = 2.0
        expected_max_lead_distance_mm = 0.2
        expected_use_serial_zaxis = True
        expected_serial_port = "COM2"
        expected_serial_on = "12"
        expected_serial_off = "13"
        expected_laser_offset = [ 0.1, 0.1]

        json_file = '''{
        "name": "PP", 
        "calibration": {
                        "max_deflection": 75.2, 
                        "upper_points": [[[0.0, 1.0], [-1.0, 1.0]], [[1.0, 0.0], [1.0, -1.0]], [[0.0, 0.0], [-1.0, -1.0]], [[1.0, 1.0], [1.0, 1.0]]], 
                        "lower_points": [[[0.0, 1.0], [-1.0, 1.0]], [[1.0, 0.0], [1.0, -1.0]], [[0.0, 0.0], [-1.0, -1.0]], [[1.0, 1.0], [1.0, 1.0]]],
                        "height": 1.0
                        }, "dripper": {"max_lead_distance_mm": 0.2, "drips_per_mm": 10.1}, "serial": {"on": true, "on_command": "12", "port": "COM2", "off_command": "13"}, "audio": {"input": {"bit_depth": "8", "sample_rate": 4800}, "output": {"bit_depth": "16", "modulation_off_frequency": 2000, "sample_rate": 48000, "modulation_on_frequency": 8000}}, "options": {"laser_offset": [0.1, 0.1], "sublayer_height_mm": 0.0, "draw_speed": 2.0, "laser_thickness_mm": 0.1}}'''
        config = Configuration(souce_dict = json.loads(json_file))

        self.maxDiff = None
        self.assertEquals(expected_name, config.name )
        self.assertEquals(expected_output_bit_depth, config.audio.output.bit_depth )
        self.assertEquals(expected_output_sample_frequency, config.audio.output.sample_rate )
        self.assertEquals(expected_on_modulation_frequency, config.audio.output.modulation_on_frequency )
        self.assertEquals(expected_off_modulation_frequency, config.audio.output.modulation_off_frequency )
        self.assertEquals(expected_input_bit_depth, config.audio.input.bit_depth )
        self.assertEquals(expected_input_sample_frequency, config.audio.input.sample_rate )
        self.assertEquals(expected_sublayer_height_mm, config.options.sublayer_height_mm )
        self.assertEquals(expected_laser_thickness_mm, config.options.laser_thickness_mm )
        self.assertEquals(expected_drips_per_mm, config.dripper.drips_per_mm )
        self.assertEquals(expected_max_deflection, config.calibration.max_deflection )
        self.assertEquals(expected_calibration_height, config.calibration.height )
        self.assertEquals(expected_calibration_lower_points, config.calibration.lower_points )
        self.assertEquals(expected_calibration_upper_points, config.calibration.upper_points )
        self.assertEquals(expected_draw_speed, config.options.draw_speed )
        self.assertEquals(expected_max_lead_distance_mm, config.dripper.max_lead_distance_mm )
        self.assertEquals(expected_use_serial_zaxis, config.serial.on )
        self.assertEquals(expected_serial_port, config.serial.port )
        self.assertEquals(expected_serial_on, config.serial.on_command )
        self.assertEquals(expected_serial_off, config.serial.off_command )
        self.assertEquals(expected_laser_offset, config.options.laser_offset )


class ConfigurationManagerTests(unittest.TestCase,test_helpers.TestHelpers):
    
    maxDiff = None
    def test_new_creates_a_new_configution_dict_with_sane_values(self):
        cm = ConfigurationManager()

        actual =  cm.new('Peachy Printer')
        expected = self.default_config
        self.assertConfigurationEqual(expected, actual)

    @patch.object(os.path, 'exists')
    @patch.object(os, 'makedirs')
    def test_save_printers_configuration_dictionary_to_peachyprintertools_folder_in_home(self, mock_makedirs,mock_exists):
        mock_exists.return_value = True
        printer_name = 'Test1'
        expected_path = os.path.join(os.path.expanduser('~'), '.peachyprintertools', printer_name + '.cfg' )
        mocked_open = mock_open(read_data=self.default_config.toJson())
        with patch('infrastructure.configuration.open', mocked_open, create=True):
            cm = ConfigurationManager()
            data = cm.new(printer_name)
            expected_data = data.toJson()
            cm.save(data)

        self.assertFalse(mock_makedirs.called)
        mocked_open.assert_called_with(expected_path, 'w')
        mocked_open().write.assert_called_with(expected_data)

    @patch.object(os.path, 'exists')
    @patch.object(os, 'makedirs')
    def test_save_should_create_data_folder_if_it_does_not_exist(self,mock_makedirs,mock_exists):
        mock_exists.return_value = False
        expected_path =  expected_path = os.path.join(os.path.expanduser('~'), '.peachyprintertools')
        with patch('infrastructure.configuration.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=file)
            cm = ConfigurationManager()
            data = cm.new('Test1')

            cm.save(data)

        mock_makedirs.assert_called_with(expected_path)

    @patch.object(os.path, 'exists')
    def test_list_should_return_empty_list_when_folder_doesnt_exist(self, mock_exists):
        mock_exists.return_value = False
        with patch('infrastructure.configuration.open', create=True) as mock_open:
            cm = ConfigurationManager()
            self.assertEquals([] , cm.list())

    @patch.object(os.path, 'exists')
    @patch.object(os, 'listdir')
    def test_list_should_return_empty_list_when_folder_contains_no_configurations(self, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = []
        with patch('infrastructure.configuration.open', create=True) as mock_open:
            cm = ConfigurationManager()
            self.assertEquals([] , cm.list())

    @patch.object(os.path, 'exists')
    @patch.object(os, 'listdir')
    def test_list_should_return_name_of_configurations(self, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = [ 'blabla.cfg' ]
        expected = [ self.default_config.name ]
        mocked_open = mock_open(read_data=self.default_config.toJson())
        with patch('infrastructure.configuration.open', mocked_open, create=True):
            cm = ConfigurationManager()

            actual = cm.list()

            self.assertEquals(expected, actual)

    @patch.object(os.path, 'exists')
    @patch.object(os, 'listdir')
    def test_list_should_only_process_cfg_files(self, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = [ 'blabla.cow' ]
        expected = [ ]
        mocked_open = mock_open(read_data=self.default_config.toJson())
        with patch('infrastructure.configuration.open', mocked_open, create=True):
            cm = ConfigurationManager()
            actual = cm.list()
            self.assertEquals(expected, actual)

    @patch.object(os.path, 'exists')
    @patch.object(os, 'listdir')
    @patch.object(os, 'makedirs')
    def test_load_should_throw_exception_not_there(self, mock_makedirs, mock_listdir, mock_exists):
        mock_exists.return_value = False
        mocked_open = mock_open()
        with patch('infrastructure.configuration.open', mocked_open, create=True):
            cm = ConfigurationManager()
            with self.assertRaises(Exception):
                cm.load(u"Not There")

    @patch.object(os.path, 'exists')
    def test_load_should_throw_exception_if_bad_data(self,  mock_exists):
        mock_exists.return_value = True
        with patch('infrastructure.configuration.open', create=True) as mock_open:
            manager = mock_open.return_value.__enter__.return_value
            manager.read.return_value = StringIO("ASDFASDFASD")
            cm = ConfigurationManager()

            with self.assertRaises(Exception):
                cm.load(u"Some Printer")

    @patch.object(os.path, 'exists')
    def test_load_should_load_data(self,mock_exists):
        mock_exists.return_value = True
        
        expected = self.default_config
        mocked_open = mock_open(read_data=self.default_config.toJson())
        
        with patch('infrastructure.configuration.open', mocked_open, create=True):
            cm = ConfigurationManager()
            actual = cm.load('Some Printer')
            self.assertConfigurationEqual(expected, actual)

    def test_new_should_return_a_config_with_defaults_and_correct_name(self):
        name = "Apple"
        expected = self.default_config
        expected.name = name
        cm = ConfigurationManager()
        
        actual = cm.new(name)

        self.assertConfigurationEqual(expected,actual)

if __name__ == '__main__':
    unittest.main()