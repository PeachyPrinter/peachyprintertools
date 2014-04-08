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
from infrastructure.audio import AudioSetup
from infrastructure.drip_based_zaxis import DripBasedZAxis
import pyaudio

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
        pass


    @patch.object(AudioSetup, 'get_valid_sampling_options' )
    @patch.object(ConfigurationManager, 'load' )
    def test_get_available_audio_options_should_get_list_of_data(self, mock_load, mock_get_valid_sampling_options):
        printer_name = u'MegaPrint'
        audio_options = { 
            "input" : [{'sample_rate' : 48000, 'depth': pyaudio.paInt16 }], 
            "output": [{'sample_rate' : 48000, 'depth': pyaudio.paInt16 }]
            }
        expected = {
                    "inputs" : { '48000, 16 bit' : {'sample_rate' : 48000, 'depth': pyaudio.paInt16 }}, 
                    "outputs": { '48000, 16 bit' : {'sample_rate' : 48000, 'depth': pyaudio.paInt16 }}
                   }

        mock_get_valid_sampling_options.return_value = audio_options
        mock_load.return_value = { u'name':printer_name }
        capi = ConfigurationAPI(ConfigurationManager())
        capi.load_printer(printer_name)
        
        actual = capi.get_available_audio_options()

        self.assertEqual(expected,actual)


    @patch.object(AudioSetup, 'get_valid_sampling_options' )
    @patch.object(ConfigurationManager, 'load' )
    def test_get_available_audio_options_should_get_list_of_data(self, mock_load, mock_get_valid_sampling_options):
        self.maxDiff = None
        printer_name = u'MegaPrint'
        audio_options = { 
            "input" : [{'sample_rate' : 48000, 'depth': pyaudio.paInt16 }], 
            "output": [{'sample_rate' : 48000, 'depth': pyaudio.paInt16 }]
            }
        expected = {
                    "inputs" : { '48000, 16 bit (Recommended)' : {'sample_rate' : 48000, 'depth': pyaudio.paInt16 }}, 
                    "outputs": { '48000, 16 bit (Recommended)' : {'sample_rate' : 48000, 'depth': pyaudio.paInt16 }}
                   }

        mock_get_valid_sampling_options.return_value = audio_options
        mock_load.return_value = { u'name':printer_name }
        capi = ConfigurationAPI(ConfigurationManager())
        capi.load_printer(printer_name)
        
        actual = capi.get_available_audio_options()

        self.assertEqual(expected,actual)

 
    @patch.object(AudioSetup, 'get_valid_sampling_options' )
    @patch.object(ConfigurationManager, 'load' )
    def test_get_available_audio_options_should_add_recommend_flag_to_one_option(self, mock_load, mock_get_valid_sampling_options):
        self.maxDiff = None
        printer_name = u'MegaPrint'
        audio_options = { 
            "input" : [{'sample_rate' : 48000, 'depth': pyaudio.paInt16 },{'sample_rate' : 44100, 'depth': pyaudio.paInt16 }], 
            "output": [{'sample_rate' : 48000, 'depth': pyaudio.paInt16 },{'sample_rate' : 44100, 'depth': pyaudio.paInt16 } ]
            }

        mock_get_valid_sampling_options.return_value = audio_options
        mock_load.return_value = { u'name':printer_name }
        capi = ConfigurationAPI(ConfigurationManager())
        capi.load_printer(printer_name)
        
        actual = capi.get_available_audio_options()

        self.assertTrue(actual['inputs'].has_key('48000, 16 bit (Recommended)'))
        self.assertTrue(actual['outputs'].has_key('48000, 16 bit (Recommended)'))
        self.assertFalse(actual['inputs'].has_key('44100, 16 bit (Recommended)'))
        self.assertFalse(actual['outputs'].has_key('44100, 16 bit (Recommended)'))

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_audio_output_options_should_update_output_when_44100(self, mock_save, mock_load):
        printer_name = u'MegaPrint'
        config =  { u'name':printer_name }
        mock_load.return_value = config
        capi = ConfigurationAPI(ConfigurationManager())
        expected = config.copy()
        expected[u'on_modulation_frequency'] = 11025
        expected[u'off_modulation_frequency'] = 3675
        expected[u'output_bit_depth'] = 8
        expected[u'output_sample_frequency'] =  44100

        capi.load_printer(printer_name)
        
        actual = capi.set_audio_output_options(44100,8)

        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_audio_output_options_should_update_output_when_48000(self, mock_save, mock_load):
        printer_name = u'MegaPrint'
        config =  { u'name':printer_name }
        mock_load.return_value = config
        capi = ConfigurationAPI(ConfigurationManager())
        expected = config.copy()
        expected[u'on_modulation_frequency'] = 12000
        expected[u'off_modulation_frequency'] = 8000
        expected[u'output_bit_depth'] = 1
        expected[u'output_sample_frequency'] =  48000

        capi.load_printer(printer_name)
        
        actual = capi.set_audio_output_options(48000,1)

        mock_save.assert_called_with(expected)


    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_audio_input_options_should_update_when_44100(self, mock_save, mock_load):
        printer_name = u'MegaPrint'
        config =  { u'name':printer_name }
        mock_load.return_value = config
        capi = ConfigurationAPI(ConfigurationManager())
        expected = config.copy()
        expected[u'input_bit_depth'] = 8
        expected[u'input_sample_frequency'] =  44100

        capi.load_printer(printer_name)
        
        actual = capi.set_audio_input_options(44100,8)

        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_audio_input_options_should_update_when_48000(self, mock_save, mock_load):
        printer_name = u'MegaPrint'
        config =  { u'name':printer_name }
        mock_load.return_value = config
        capi = ConfigurationAPI(ConfigurationManager())
        expected = config.copy()
        expected[u'input_bit_depth'] = 1
        expected[u'input_sample_frequency'] =  48000

        capi.load_printer(printer_name)
        
        actual = capi.set_audio_input_options(48000,1)

        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(DripBasedZAxis, 'start')
    def test_drip_calibration_should_start_getting_drips(self, mock_start,mock_load,mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = { u'name':'printer' }
        configuration_API.load_printer('printer')
        configuration_API.set_audio_input_options(48000,8)

        configuration_API.start_counting_drips()

        mock_start.assert_called_with()

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(DripBasedZAxis, 'start')
    @patch.object(DripBasedZAxis, 'stop')
    def test_drip_calibration_should_stop_getting_drips(self, mock_stop,mock_start,mock_load,mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = { u'name':'printer' }
        configuration_API.load_printer('printer')
        configuration_API.set_audio_input_options(48000,8)
        configuration_API.start_counting_drips()

        configuration_API.stop_counting_drips()

        mock_stop.assert_called_with()
    
    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(DripBasedZAxis, 'start')
    @patch.object(DripBasedZAxis, 'current_z_location_mm')
    def test_drip_calibration_should_be_able_to_get_drips(self, mock_current_z_location_mm,mock_start,mock_load,mock_save):
        
        fake_drip_counter = 77
        mock_current_z_location_mm.return_value = fake_drip_counter 

        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = { u'name':'printer' }
        configuration_API.load_printer('printer')
        configuration_API.set_audio_input_options(48000,8)

        configuration_API.start_counting_drips()
        result = configuration_API.get_drips()

        self.assertEquals(fake_drip_counter, result)

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(DripBasedZAxis, 'start')
    @patch.object(DripBasedZAxis, 'reset')
    def test_drip_calibration_should_call_reset_when_reset_requested(self, mock_reset,mock_start,mock_load,mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = { u'name':'printer' }
        configuration_API.load_printer('printer')
        configuration_API.set_audio_input_options(48000,8)

        configuration_API.start_counting_drips()
        configuration_API.reset_drips()

        mock_reset.assert_called_with(0)
        
    def test_drip_calibration_should_be_able_to_set_target_height_if_float(self):
        configuration_API = ConfigurationAPI(ConfigurationManager())

        configuration_API.set_target_height(10.0)

    def test_drip_calibration_should_be_able_to_set_target_height_if_int(self):
        configuration_API = ConfigurationAPI(ConfigurationManager())

        configuration_API.set_target_height(10)

    def test_drip_calibration_target_height_must_be_greater_than_0(self):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        
        with self.assertRaises(Exception):
            configuration_API.set_target_height(0.0)

    def test_drip_calibration_target_height_must_be_numeric(self):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        
        with self.assertRaises(Exception):
            configuration_API.set_target_height('a')

    def test_drip_calibration_should_not_be_able_to_mark_when_target_not_specified(self):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        
        with self.assertRaises(Exception):
            configuration_API.mark_drips_at_target()

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(DripBasedZAxis, 'start')
    @patch.object(DripBasedZAxis, 'current_z_location_mm')
    def test_drip_calibration_should_be_able_to_mark_when_target_specified(self, mock_current_z_location_mm, mock_start,mock_load,mock_save):
        fake_drip_counter = 70
        target_height = 10.0
        expected_drips_per_mm = fake_drip_counter / target_height
        
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = { u'name':'printer' }
        configuration_API.load_printer('printer')
        configuration_API.set_audio_input_options(48000,8)
        mock_current_z_location_mm.return_value = fake_drip_counter
        
        configuration_API.start_counting_drips()
        configuration_API.set_target_height(target_height)
        configuration_API.mark_drips_at_target()

        self.assertEquals(expected_drips_per_mm, configuration_API.get_drips_per_mm())
    
    @patch('api.configuration_api.DripBasedZAxis')
    @patch.object(ConfigurationManager, 'save' )
    @patch.object(ConfigurationManager, 'load' )
    def test_drip_calibration_should_use_audio_input_settings(self, mock_load, mock_save, mock_DripBasedZAxis):
        mock_drip_based_zaxis = mock_DripBasedZAxis
        mock_load.return_value =  { u'name':'name' }
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")
        configuration_API.set_audio_input_options(48000,8)

        configuration_API.start_counting_drips()

        mock_DripBasedZAxis.assert_called_with(1, sample_rate=48000, bit_depth=8)


if __name__ == '__main__':
    unittest.main()