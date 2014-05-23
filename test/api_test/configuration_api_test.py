import unittest
import os
import sys
import json
import hashlib
from StringIO import StringIO

from mock import patch

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from api.configuration_api import ConfigurationAPI, AudioSetting
from domain.configuration_manager import ConfigurationManager
from infrastructure.audio import AudioSetup
from infrastructure.drip_based_zaxis import DripBasedZAxis
import pyaudio
import test_helpers

class ConfigurationAPITest(unittest.TestCase, test_helpers.TestHelpers):

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


    @patch.object(ConfigurationManager, 'save' )
    @patch.object(ConfigurationManager, 'new' )
    def test_current_printer_returns_printer_name(self, mock_new, mock_save):
        capi = ConfigurationAPI(ConfigurationManager())
        mock_new.return_value = { 'name' : 'Spam' }
        capi.add_printer('Spam')

        actual = capi.current_printer()

        self.assertEqual('Spam', actual)

    @patch.object(ConfigurationManager, 'load' )
    def test_load_printer_calls_load(self, mock_load):
        printer_name = 'MegaPrint'
        mock_load.return_value = { 'name':printer_name}
        capi = ConfigurationAPI(ConfigurationManager())
        
        capi.load_printer(printer_name)

        mock_load.assert_called_with(printer_name)

    @patch.object(ConfigurationManager, 'load' )
    def test_cannot_add_printer_that_already_exists(self, mock_load):
        pass
    
    @patch.object(ConfigurationManager, 'load' )
    def test_get_config_returns_current_config(self, mock_load):
        expected = { 'name':'MegaPrint' }
        mock_load.return_value = expected
        capi = ConfigurationAPI(ConfigurationManager())
        capi.load_printer('printer')

        actual = capi.get_current_config()
        
        self.assertEquals(expected, actual)


# ----------------------------------- Audio Setup ------------------------------------------

    @patch.object(AudioSetup, 'get_valid_sampling_options' )
    @patch.object(ConfigurationManager, 'load' )
    def test_get_available_audio_options_should_get_list_of_settings(self, mock_load, mock_get_valid_sampling_options):
        audio_options = { 
            "input" : [{'sample_rate' : 22000, 'depth': '16 bit' }], 
            "output": [{'sample_rate' : 22000, 'depth': '32 bit Floating Point' }]
            }
        expected = {
                    "inputs" : [AudioSetting(22000,'16 bit')],
                    "outputs": [AudioSetting(22000,'32 bit Floating Point')]
                   }

        mock_get_valid_sampling_options.return_value = audio_options
        mock_load.return_value = self.DEFAULT_CONFIG
        capi = ConfigurationAPI(ConfigurationManager())
        capi.load_printer("Printer")
        
        actual = capi.get_available_audio_options()

        self.assertListContentsEqual(expected['inputs'],actual['inputs'])
        self.assertListContentsEqual(expected['outputs'],actual['outputs'])


    @patch.object(AudioSetup, 'get_valid_sampling_options' )
    @patch.object(ConfigurationManager, 'load' )
    def test_get_available_audio_options_should_include_recomended_options(self, mock_load, mock_get_valid_sampling_options):
        audio_options = { 
            "input" : [{'sample_rate' : 48000, 'depth': '16 bit' }], 
            "output": [{'sample_rate' : 48000, 'depth': '16 bit' }]
            }
        
        expected_in  = AudioSetting(48000,'16 bit', current = True)
        expected_in.set_recommended()
        expected_out = AudioSetting(48000,'16 bit', current = True)
        expected_out.set_recommended()
        

        expected = {
                    "inputs" : [expected_in], 
                    "outputs": [expected_out] 
                   }

        mock_get_valid_sampling_options.return_value = audio_options
        mock_load.return_value = self.DEFAULT_CONFIG
        capi = ConfigurationAPI(ConfigurationManager())
        capi.load_printer("Printer")
        
        actual = capi.get_available_audio_options()

        self.assertListContentsEqual(expected['inputs'],actual['inputs'])
        self.assertListContentsEqual(expected['outputs'],actual['outputs'])

 
    @patch.object(AudioSetup, 'get_valid_sampling_options' )
    @patch.object(ConfigurationManager, 'load' )
    def test_get_available_audio_options_should_add_recommend_flag_to_one_option(self, mock_load, mock_get_valid_sampling_options):
        audio_options = { 
            "input" : [{'sample_rate' : 48000, 'depth': '32 bit Floating Point' },{'sample_rate' : 44100, 'depth': '16 bit' }], 
            "output": [{'sample_rate' : 48000, 'depth': '16 bit' },{'sample_rate' : 44100, 'depth': '16 bit' } ]
            }

        mock_get_valid_sampling_options.return_value = audio_options
        mock_load.return_value = self.DEFAULT_CONFIG
        capi = ConfigurationAPI(ConfigurationManager())
        capi.load_printer("Printer")

        actual = capi.get_available_audio_options()

        expected_input = AudioSetting(44100,'16 bit', recommended = True)
        unexpected_input = AudioSetting(48000,'32 bit Floating Point')
        expected_output = AudioSetting(48000,'16 bit', recommended = True, current = True)
        unexpected_output = AudioSetting(44100,'16 bit')

        self.assertListContentsEqual([expected_input, unexpected_input],actual['inputs'])
        self.assertListContentsEqual([unexpected_output,expected_output],actual['outputs'])
    
    @patch.object(AudioSetup, 'get_valid_sampling_options' )
    @patch.object(ConfigurationManager, 'load' )
    def test_get_available_audio_options_is_sorted(self, mock_load, mock_get_valid_sampling_options):
        audio_options = { 
            "input" : [], 
            "output": [{'sample_rate' : 48000, 'depth': '32 bit Floating Point' },{'sample_rate' : 44100, 'depth': '16 bit' },{'sample_rate' : 48000, 'depth': '16 bit' },{'sample_rate' : 44100, 'depth': '24 bit' } ]
            }

        mock_get_valid_sampling_options.return_value = audio_options
        mock_load.return_value = self.DEFAULT_CONFIG
        capi = ConfigurationAPI(ConfigurationManager())
        capi.load_printer("Printer")

        actual = capi.get_available_audio_options()

        expected_ordered = [
            AudioSetting(44100, '16 bit'),
            AudioSetting(44100, '24 bit'),
            AudioSetting(48000, '16 bit', recommended = True, current = True),
            AudioSetting(48000, '32 bit Floating Point'),
        ] 
        self.assertListContentsEqual(expected_ordered,actual['outputs'])

    @patch.object(AudioSetup, 'get_valid_sampling_options' )
    @patch.object(ConfigurationManager, 'load' )
    def test_get_available_audio_options_sets_currently_selected(self, mock_load, mock_get_valid_sampling_options):
        audio_options = { 
            "input" : [{'sample_rate' : 48000, 'depth': '16 bit' },{'sample_rate' : 44100, 'depth': '16 bit' }], 
            "output": [{'sample_rate' : 48000, 'depth': '16 bit' },{'sample_rate' : 44100, 'depth': '16 bit' }]
            }

        mock_get_valid_sampling_options.return_value = audio_options
        config = self.DEFAULT_CONFIG.copy()
        config['input_bit_depth'] = '16 bit'
        config['input_sample_frequency'] = 44100
        config['output_bit_depth'] = '16 bit'
        config['output_sample_frequency'] = 44100

        mock_load.return_value = config

        capi = ConfigurationAPI(ConfigurationManager())
        capi.load_printer("Printer")

        actual = capi.get_available_audio_options()

        in1 = AudioSetting(44100,'16 bit', current = True)
        in2 = AudioSetting(48000,'16 bit', recommended = True)
        out1 = AudioSetting(44100,'16 bit', current = True)
        out2 = AudioSetting(48000,'16 bit', recommended = True)
        

        self.assertListContentsEqual([in1, in2],actual['inputs'])
        self.assertListContentsEqual([out1, out2],actual['outputs'])
    

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_audio_output_options_should_update_output_when_44100(self, mock_save, mock_load):
        config = self.DEFAULT_CONFIG.copy()
        mock_load.return_value = config
        capi = ConfigurationAPI(ConfigurationManager())
        expected = config.copy()
        expected['on_modulation_frequency'] = 11025
        expected['off_modulation_frequency'] = 2205
        expected['output_bit_depth'] = '16 bit'
        expected['output_sample_frequency'] =  44100

        capi.load_printer("Printer")
        
        actual = capi.set_audio_output_options(AudioSetting(44100, '16 bit'))

        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_audio_output_options_should_update_output_when_48000(self, mock_save, mock_load):
        printer_name = 'MegaPrint'
        config =  self.DEFAULT_CONFIG.copy()
        mock_load.return_value = config
        capi = ConfigurationAPI(ConfigurationManager())
        expected = config.copy()
        expected['on_modulation_frequency'] = 12000
        expected['off_modulation_frequency'] = 2000
        expected['output_bit_depth'] = '32 bit Floating Point'
        expected['output_sample_frequency'] =  48000

        capi.load_printer(printer_name)
        
        actual = capi.set_audio_output_options(AudioSetting(48000,'32 bit Floating Point'))

        mock_save.assert_called_with(expected)


    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_audio_input_options_should_update_when_44100(self, mock_save, mock_load):
        config =  self.DEFAULT_CONFIG.copy()
        mock_load.return_value = config
        capi = ConfigurationAPI(ConfigurationManager())
        expected = config.copy()
        expected['input_bit_depth'] = '16 bit'
        expected['input_sample_frequency'] =  44100

        capi.load_printer('Printer')
        
        actual = capi.set_audio_input_options(AudioSetting(44100,'16 bit'))

        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_audio_input_options_should_update_when_48000(self, mock_save, mock_load):
        config =  self.DEFAULT_CONFIG.copy()
        mock_load.return_value = config
        capi = ConfigurationAPI(ConfigurationManager())
        expected = config.copy()
        expected['input_bit_depth'] = '32 bit Floating Point'
        expected['input_sample_frequency'] =  48000

        capi.load_printer('Printer')
        
        actual = capi.set_audio_input_options(AudioSetting(48000,'32 bit Floating Point'))

        mock_save.assert_called_with(expected)



    # ------------------------------- Drip Setup --------------------------------------

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(DripBasedZAxis, 'start')
    def test_start_counting_drips_should_start_getting_drips(self, mock_start,mock_load,mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.DEFAULT_CONFIG
        configuration_API.load_printer('printer')

        configuration_API.start_counting_drips()

        mock_start.assert_called_with()

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(DripBasedZAxis, 'start')
    @patch('api.configuration_api.DripBasedZAxis')
    def test_start_counting_drips_should_pass_call_back_function(self, mock_DripBasedZAxis, mock_start,mock_load,mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.DEFAULT_CONFIG
        configuration_API.load_printer('printer')

        def callback(bla):
            pass

        configuration_API.start_counting_drips(drip_call_back = callback)


        mock_DripBasedZAxis.assert_called_with(
            1,
            sample_rate = self.DEFAULT_CONFIG['input_sample_frequency'], 
            bit_depth = self.DEFAULT_CONFIG['input_bit_depth'],
            drip_call_back = callback
            )

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(DripBasedZAxis, 'start')
    @patch.object(DripBasedZAxis, 'stop')
    def test_stop_counting_drips_should_stop_getting_drips(self, mock_stop,mock_start,mock_load,mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.DEFAULT_CONFIG
        configuration_API.load_printer('printer')
        configuration_API.start_counting_drips()

        configuration_API.stop_counting_drips()

        mock_stop.assert_called_with()
    
    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(DripBasedZAxis, 'start')
    @patch.object(DripBasedZAxis, 'current_z_location_mm')
    def test_get_drips_should_return_correct_number_of_drips(self, mock_current_z_location_mm,mock_start,mock_load,mock_save):
        
        fake_drip_counter = 77
        mock_current_z_location_mm.return_value = fake_drip_counter 

        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.DEFAULT_CONFIG
        configuration_API.load_printer('printer')

        configuration_API.start_counting_drips()
        result = configuration_API.get_drips()

        self.assertEquals(fake_drip_counter, result)

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(DripBasedZAxis, 'start')
    @patch.object(DripBasedZAxis, 'reset')
    def test_drip_calibration_should_call_reset_when_reset_requested(self, mock_reset,mock_start,mock_load,mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.DEFAULT_CONFIG
        configuration_API.load_printer('printer')

        configuration_API.start_counting_drips()
        configuration_API.reset_drips()

        mock_reset.assert_called_with(0)
        
    def test_set_target_height_should_work_for__positive_numbers(self):
        configuration_API = ConfigurationAPI(ConfigurationManager())

        configuration_API.set_target_height(10.0)
        configuration_API.set_target_height(10)

    def test_set_target_height_should_throw_when_0_or_below(self):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        
        with self.assertRaises(Exception):
            configuration_API.set_target_height(0.0)

    def test_set_target_height_should_throw_when_not_numeric(self):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        
        with self.assertRaises(Exception):
            configuration_API.set_target_height('a')

    def test_mark_drips_at_target_should_throw_when_target_not_specified(self):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        
        with self.assertRaises(Exception):
            configuration_API.mark_drips_at_target()

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(DripBasedZAxis, 'start')
    @patch.object(DripBasedZAxis, 'current_z_location_mm')
    def test_mark_drips_should_when_target_specified(self, mock_current_z_location_mm, mock_start,mock_load,mock_save):
        fake_drip_counter = 70
        target_height = 10.0
        expected_drips_per_mm = fake_drip_counter / target_height
        
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.DEFAULT_CONFIG.copy()
        configuration_API.load_printer('printer')
        mock_current_z_location_mm.return_value = fake_drip_counter
        
        configuration_API.start_counting_drips()
        configuration_API.set_target_height(target_height)
        configuration_API.mark_drips_at_target()

        self.assertEquals(expected_drips_per_mm, configuration_API.get_drips_per_mm())
        self.assertFalse(mock_save.called)

    @patch('api.configuration_api.DripBasedZAxis')
    @patch.object(ConfigurationManager, 'save' )
    @patch.object(ConfigurationManager, 'load' )
    def test_start_counting_drips_should_use_audio_input_settings(self, mock_load, mock_save, mock_DripBasedZAxis):
        mock_drip_based_zaxis = mock_DripBasedZAxis
        mock_load.return_value =  self.DEFAULT_CONFIG
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer('printer')

        configuration_API.start_counting_drips()

        mock_DripBasedZAxis.assert_called_with(1, sample_rate=48000, bit_depth='16 bit',drip_call_back = None)

    @patch.object(ConfigurationManager, 'load')
    def test_get_drips_per_mm_should_return_current_setting_if_unmarked(self, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.DEFAULT_CONFIG

        configuration_API.load_printer('Printer')

        actual = configuration_API.get_drips_per_mm()

        self.assertEquals(self.DEFAULT_CONFIG['drips_per_mm'], actual)

    # ----------------------------- General Setup --------------------------------------

    @patch.object(ConfigurationManager, 'load' )
    def test_get_max_lead_distance_mm_returns_max_lead_distance(self, mock_load):
        expected = 0.4
        config = self.DEFAULT_CONFIG.copy()
        config['max_lead_distance_mm'] = expected
        mock_load.return_value =  config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected,configuration_API.get_max_lead_distance_mm())

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_max_lead_distance_mm_sets_max_lead_distance_mm(self, mock_save, mock_load):
        expected = 0.4
        expected_config = self.DEFAULT_CONFIG.copy()
        expected_config['max_lead_distance_mm'] = expected
        mock_load.return_value =  self.DEFAULT_CONFIG.copy()
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_max_lead_distance_mm(expected)

        self.assertEquals(expected,configuration_API.get_max_lead_distance_mm())
        mock_save.assert_called_with(expected_config)

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_max_lead_distance_mm_should_go_boom_if_not_positive_float(self, mock_save, mock_load):
        mock_load.return_value =   {'name':'test' }
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.set_max_lead_distance_mm('a')
        with self.assertRaises(Exception):
            configuration_API.set_max_lead_distance_mm(-1.0)
        with self.assertRaises(Exception):
            configuration_API.set_max_lead_distance_mm({'a':'b'})
        with self.assertRaises(Exception):
            configuration_API.set_max_lead_distance_mm(0)
        with self.assertRaises(Exception):
            configuration_API.set_max_lead_distance_mm(1)


    @patch.object(ConfigurationManager, 'load' )
    def test_get_laser_thickness_mm_returns_thickness(self, mock_load):
        expected = 7.0
        config = self.DEFAULT_CONFIG.copy()
        config['laser_thickness_mm'] = expected
        mock_load.return_value =  config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected,configuration_API.get_laser_thickness_mm())

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_laser_thickness_mm_sets_thickness(self, mock_save, mock_load):
        expected_thickness = 7.0
        config =  self.DEFAULT_CONFIG.copy()
        expected = config.copy()
        expected['laser_thickness_mm'] = expected_thickness
        mock_load.return_value =  config.copy() 
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_laser_thickness_mm(expected_thickness)

        self.assertEquals(expected_thickness,configuration_API.get_laser_thickness_mm())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_laser_thickness_mm_should_go_boom_if_not_positive_float(self, mock_save, mock_load):
        mock_load.return_value =   {'name':'test' }
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.set_laser_thickness_mm('a')
        with self.assertRaises(Exception):
            configuration_API.set_laser_thickness_mm(-1.0)
        with self.assertRaises(Exception):
            configuration_API.set_laser_thickness_mm({'a':'b'})
        with self.assertRaises(Exception):
            configuration_API.set_laser_thickness_mm(0)
        with self.assertRaises(Exception):
            configuration_API.set_laser_thickness_mm(1)

    @patch.object(ConfigurationManager, 'load' )
    def test_sublayer_height_mm_returns_theight(self, mock_load):
        expected = 7.0
        mock_load.return_value =  { 'name':'name', 'sublayer_height_mm': expected }
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected,configuration_API.get_sublayer_height_mm())

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_sublayer_height_mm_returns_height(self, mock_save, mock_load):
        expected_height = 7.0
        config =  { 'name':'test' }
        expected = config.copy()
        expected['sublayer_height_mm'] = expected_height
        mock_load.return_value =  config.copy() 
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_sublayer_height_mm(expected_height)

        self.assertEquals(expected_height,configuration_API.get_sublayer_height_mm())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_sublayer_height_mm_should_go_boom_if_not_positive_float(self, mock_save, mock_load):
        mock_load.return_value =   {'name':'test' }
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.set_sublayer_height_mm('a')
        with self.assertRaises(Exception):
            configuration_API.set_sublayer_height_mm(-1.0)
        with self.assertRaises(Exception):
            configuration_API.set_sublayer_height_mm({'a':'b'})
        with self.assertRaises(Exception):
            configuration_API.set_sublayer_height_mm(0)
        with self.assertRaises(Exception):
            configuration_API.set_sublayer_height_mm(1)

    @patch.object(ConfigurationManager, 'load' )
    def test_get_serial_options_loads_correctly(self, mock_load):
        mock_load.return_value =  self.DEFAULT_CONFIG
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        actual_enabled = configuration_API.get_serial_enabled()
        actual_port = configuration_API.get_serial_port()
        actual_on = configuration_API.get_serial_on_command()
        actual_off = configuration_API.get_serial_off_command()

        self.assertEquals(self.DEFAULT_CONFIG['use_serial_zaxis'],actual_enabled)
        self.assertEquals(self.DEFAULT_CONFIG['serial_port'],actual_port)
        self.assertEquals(self.DEFAULT_CONFIG['serial_on'],actual_on)
        self.assertEquals(self.DEFAULT_CONFIG['serial_off'],actual_off)

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_get_serial_options_loads_correctly(self, mock_save, mock_load):
        expected_enabled = True
        expected_port = 'com54'
        expected_on = 'GOGOGO'
        expected_off = 'STOPSTOP'

        mock_load.return_value =  self.DEFAULT_CONFIG.copy()
        expected_config = self.DEFAULT_CONFIG.copy()
        expected_config['use_serial_zaxis'] = expected_enabled
        expected_config['serial_port']      = expected_port
        expected_config['serial_on']        = expected_on
        expected_config['serial_off']       = expected_off

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_serial_enabled(expected_enabled)
        configuration_API.set_serial_port(expected_port)
        configuration_API.set_serial_on_command(expected_on)
        configuration_API.set_serial_off_command(expected_off)

        mock_save.assert_called_with(expected_config)

#-----------------------------------------Cure Test Setup Tests -----------------------------------

    @patch.object(ConfigurationManager, 'load' )
    def test_get_cure_test_total_height_must_exceed_base_height(self, mock_load):
        mock_load.return_value = self.DEFAULT_CONFIG
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_cure_test(10,1,1,2)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1,1,1,2)


    @patch.object(ConfigurationManager, 'load' )
    def test_get_cure_test_final_speed_exceeds_start_speed(self, mock_load):
        mock_load.return_value = self.DEFAULT_CONFIG
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1,10,10,1)

        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1,10,1,1)

    @patch.object(ConfigurationManager, 'load' )
    def test_get_cure_test_values_must_be_positive_non_0_numbers_for_all_but_base(self, mock_load):
        mock_load.return_value = self.DEFAULT_CONFIG
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_cure_test('a',10,10,1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1,'a',10,1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1,10,'a',1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1,10,10,'a')
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1,10,10,1,'a')
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(-1,10,10,1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1,-10,10,1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1,10,-1,1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1,10,10,-1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1,10,10,1,-1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1,0,10,1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1,10,0,1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1,10,10,0)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1,10,10,1,0)

    @patch.object(ConfigurationManager, 'load' )
    def test_get_cure_test_returns_a_layer_generator(self, mock_load):
        mock_load.return_value = self.DEFAULT_CONFIG
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")
        
        cure_test = configuration_API.get_cure_test(0,1,1,2)
        cure_test.next()

    @patch.object(ConfigurationManager, 'load' )
    def test_get_speed_at_height_must_exceed_base_height(self, mock_load):
        mock_load.return_value = self.DEFAULT_CONFIG
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(10,1,1,2,1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1,1,1,2,1)

    @patch.object(ConfigurationManager, 'load' )
    def test_get_speed_at_height_must_have_height_between_total_and_base(self, mock_load):
        mock_load.return_value = self.DEFAULT_CONFIG
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(0,10,1,2,11)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(2,10,1,2,0)

    @patch.object(ConfigurationManager, 'load' )
    def test_get_speed_at_height_final_speed_exceeds_start_speed(self, mock_load):
        mock_load.return_value = self.DEFAULT_CONFIG
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1,10,10,1,1)

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1,10,1,1,1)

    @patch.object(ConfigurationManager, 'load' )
    def test_get_speed_at_height_values_must_be_positive_non_0_numbers_for_all_but_base(self, mock_load):
        mock_load.return_value = self.DEFAULT_CONFIG
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height('a',10,10,1,1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1,'a',10,1,1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1,10,'a',1,1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1,10,10,'a',1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1,10,10,1,'a',1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(-1,10,10,1,1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1,-10,10,1,1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1,10,-1,1,1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1,10,10,-1,1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1,10,10,1,-1,1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1,0,10,1,1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1,10,0,1,1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1,10,10,0,1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1,10,10,1,0,1)

    @patch.object(ConfigurationManager, 'load' )
    def test_get_speed_at_height_returns_a_correct_height(self, mock_load):
        mock_load.return_value = self.DEFAULT_CONFIG
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")
        
        speed = configuration_API.get_speed_at_height(0,1,10,20,0.5)
        self.assertEquals(15, speed)

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_speed(self, mock_save, mock_load):
        mock_load.return_value = self.DEFAULT_CONFIG.copy()
        expected_config = self.DEFAULT_CONFIG.copy()
        expected_config['draw_speed'] = 121.0
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")
        
        configuration_API.set_speed(121)
        
        mock_save.assert_called_with(expected_config)

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_speed_should_throw_exception_if_less_then_or_0(self, mock_save, mock_load):
        mock_load.return_value = self.DEFAULT_CONFIG.copy()
        expected_config = self.DEFAULT_CONFIG.copy()
        expected_config['draw_speed'] = 121.0
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")
        
        with self.assertRaises(Exception):
            configuration_API.set_speed(-1)
        with self.assertRaises(Exception):
            configuration_API.set_speed(0)


class AudioSettingsTest(unittest.TestCase, test_helpers.TestHelpers):
    def test_str_returns_human_readable_option(self):
        s = AudioSetting(48000,"16 bit")
        self.assertEquals("48000 Hz, 16 bit", str(s))

    def test_str_returns_human_readable_option_with_recommend_with_recommended(self):
        s = AudioSetting(48000,"16 bit")
        s.set_recommended()
        self.assertEquals("48000 Hz, 16 bit (Recommended)", str(s))

    def test_set_current_set_current_flag(self):
        s = AudioSetting(48000,"16 bit")
        s.set_current()
        self.assertTrue(s.current)

    def test_to_instances_with_same_settings_are_equal(self):
        a = AudioSetting(48000,'16 bit')
        b = AudioSetting(48000,'16 bit')
        self.assertEquals(a,b)

    def test_to_instances_with_diffrent_settings_are_equal(self):
        a = AudioSetting(48000,'16 bit')
        b = AudioSetting(44100,'16 bit')
        self.assertNotEquals(a,b)



if __name__ == '__main__':
    unittest.main()