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



if __name__ == '__main__':
    unittest.main()