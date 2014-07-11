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
from infrastructure.drip_based_zaxis import AudioDripZAxis
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
        name = "Spam"
        config = self.default_config
        config.name = name
        mock_new.return_value = config
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

#     @patch.object(ConfigurationManager, 'load' )
#     def test_cannot_add_printer_that_already_exists(self, mock_load):
#         pass
    
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
        mock_load.return_value = self.default_config
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
        mock_load.return_value = self.default_config
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
        mock_load.return_value = self.default_config
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
        mock_load.return_value = self.default_config
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
        config = self.default_config
        config.audio.input.bit_depth = '16 bit'
        config.audio.input.sample_rate = 44100
        config.audio.output.bit_depth = '16 bit'
        config.audio.output.sample_rate = 44100

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
        mock_load.return_value = self.default_config
        capi = ConfigurationAPI(ConfigurationManager())
        expected = self.default_config
        expected.audio.output.modulation_on_frequency = 11025
        expected.audio.output.modulation_off_frequency = 2205
        expected.audio.output.bit_depth = '16 bit'
        expected.audio.output.sample_rate =  44100

        capi.load_printer("Printer")
        
        actual = capi.set_audio_output_options(AudioSetting(44100, '16 bit'))
        self.assertConfigurationEqual(expected, mock_save.mock_calls[0][1][0])

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_audio_output_options_should_update_output_when_48000(self, mock_save, mock_load):
        printer_name = 'MegaPrint'
        config =  self.default_config
        mock_load.return_value = config
        capi = ConfigurationAPI(ConfigurationManager())
        expected = self.default_config
        expected.audio.output.modulation_on_frequency = 12000
        expected.audio.output.modulation_off_frequency = 2000
        expected.audio.output.bit_depth = '32 bit Floating Point'
        expected.audio.output.sample_rate =  48000

        capi.load_printer(printer_name)
        
        actual = capi.set_audio_output_options(AudioSetting(48000,'32 bit Floating Point'))

        self.assertConfigurationEqual(expected, mock_save.mock_calls[0][1][0])


    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_audio_input_options_should_update_when_44100(self, mock_save, mock_load):
        config =  self.default_config
        mock_load.return_value = config
        capi = ConfigurationAPI(ConfigurationManager())
        expected = self.default_config
        expected.audio.input.bit_depth = '16 bit'
        expected.audio.input.sample_rate =  44100

        capi.load_printer('Printer')
        
        actual = capi.set_audio_input_options(AudioSetting(44100,'16 bit'))

        self.assertConfigurationEqual(expected, mock_save.mock_calls[0][1][0])

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_audio_input_options_should_update_when_48000(self, mock_save, mock_load):
        config =  self.default_config
        mock_load.return_value = config
        capi = ConfigurationAPI(ConfigurationManager())
        expected = self.default_config
        expected.audio.input.bit_depth = '32 bit Floating Point'
        expected.audio.input.sample_rate =  48000

        capi.load_printer('Printer')
        
        actual = capi.set_audio_input_options(AudioSetting(48000,'32 bit Floating Point'))

        self.assertConfigurationEqual(expected, mock_save.mock_calls[0][1][0])



    # ------------------------------- Drip Setup --------------------------------------

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(AudioDripZAxis, 'start')
    def test_start_counting_drips_should_start_getting_drips(self, mock_start,mock_load,mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer('printer')

        configuration_API.start_counting_drips()

        mock_start.assert_called_with()

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(AudioDripZAxis, 'start')
    @patch('api.configuration_api.AudioDripZAxis')
    @patch('api.configuration_api.NullCommander')
    def test_start_counting_drips_should_pass_call_back_function(self, mock_NullCommander, mock_AudioDripZAxis, mock_start,mock_load,mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer('printer')

        def callback(bla):
            pass

        configuration_API.start_counting_drips(drip_call_back = callback)

        mock_AudioDripZAxis.assert_called_with(
            1,
            self.default_config.audio.input.sample_rate, 
            self.default_config.audio.input.bit_depth,
            mock_NullCommander.return_value,
            '','',
            drip_call_back = callback
            )

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(AudioDripZAxis, 'start')
    @patch.object(AudioDripZAxis, 'stop')
    def test_stop_counting_drips_should_stop_getting_drips(self, mock_stop,mock_start,mock_load,mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer('printer')
        configuration_API.start_counting_drips()

        configuration_API.stop_counting_drips()

        mock_stop.assert_called_with()
    
    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(AudioDripZAxis, 'start')
    @patch.object(AudioDripZAxis, 'reset')
    def test_drip_calibration_should_call_reset_when_reset_requested(self, mock_reset,mock_start,mock_load,mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer('printer')

        configuration_API.start_counting_drips()
        configuration_API.reset_drips()

        mock_reset.assert_called_with()

    @patch('api.configuration_api.AudioDripZAxis')
    @patch.object(ConfigurationManager, 'save' )
    @patch.object(ConfigurationManager, 'load' )
    @patch('api.configuration_api.NullCommander')
    def test_start_counting_drips_should_use_audio_input_settings(self, mock_NullCommander, mock_load, mock_save, mock_AudioDripZAxis):
        mock_drip_based_zaxis = mock_AudioDripZAxis
        mock_load.return_value =  self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer('printer')
        expected_sample_rate = self.default_config.audio.input.sample_rate

        configuration_API.start_counting_drips()

        mock_AudioDripZAxis.assert_called_with(
            1, 
            expected_sample_rate, 
            self.default_config.audio.input.bit_depth,
            mock_NullCommander.return_value,
            '','',
            drip_call_back = None
        )

    @patch.object(ConfigurationManager, 'load')
    def test_get_drips_per_mm_should_return_current_setting(self, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config

        configuration_API.load_printer('Printer')

        actual = configuration_API.get_drips_per_mm()

        self.assertEquals(self.default_config.dripper.drips_per_mm, actual)

    @patch.object(ConfigurationManager, 'load')
    @patch('api.configuration_api.AudioDripZAxis')
    def test_set_drips_per_mm_should_overwrite_current_setting_and_update_zaxis(self, mock_AudioDripZAxis , mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        mock_audiodripzaxis = mock_AudioDripZAxis.return_value
        expected = 6534.0

        configuration_API.load_printer('Printer')
        configuration_API.start_counting_drips()
        configuration_API.set_drips_per_mm(expected)
        configuration_API.stop_counting_drips()

        mock_audiodripzaxis.set_drips_per_mm.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    def test_get_dripper_type_should_return_current_type(self, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer('Printer')

        actual = configuration_API.get_dripper_type()

        self.assertEquals(self.default_config.dripper.dripper_type, actual)

    @patch.object(ConfigurationManager, 'load')
    def test_set_dripper_type_should_return_current_type(self, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer('Printer')
        expected = 'emulated'
        configuration_API.set_dripper_type(expected)
        actual = configuration_API.get_dripper_type()

        self.assertEquals(expected, actual)

    @patch.object(ConfigurationManager, 'load')
    def test_get_emulated_drips_per_second_should_return(self, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer('Printer')

        actual = configuration_API.get_emulated_drips_per_second()

        self.assertEquals(self.default_config.dripper.emulated_drips_per_second, actual)

    @patch.object(ConfigurationManager, 'load')
    def test_set_emulated_drips_per_second_should_return(self, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer('Printer')
        expected = 302.0
        configuration_API.set_emulated_drips_per_second(expected)
        actual = configuration_API.get_emulated_drips_per_second()

        self.assertEquals(expected, actual)

    @patch.object(ConfigurationManager, 'load')
    @patch('infrastructure.commander.SerialCommander')
    @patch('api.configuration_api.AudioDripZAxis')
    def test_send_dripper_on_command_should_raise_exceptions_if_serial_not_configured(self, mock_Zaxis, mock_SerialCommander, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.serial.on = False
        mock_load.return_value = config

        configuration_API.load_printer('Printer')
        configuration_API.start_counting_drips()
        with self.assertRaises(Exception):
            configuration_API.send_dripper_on_command()

        self.assertEquals(0, mock_SerialCommander.call_count)

    @patch.object(ConfigurationManager, 'load')
    @patch('api.configuration_api.SerialCommander')
    @patch('api.configuration_api.AudioDripZAxis')
    def test_send_dripper_on_command_should(self, mock_Zaxis, mock_SerialCommander, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.serial.on = True
        config.serial.port = "COM1"
        config.serial.on_command = "1"
        mock_load.return_value = config
        mock_serial_commander = mock_SerialCommander.return_value

        configuration_API.load_printer('Printer')
        configuration_API.start_counting_drips()
        configuration_API.send_dripper_on_command()

        mock_SerialCommander.assert_called_with("COM1")
        mock_serial_commander.send_command.assert_called_with("1")


    @patch.object(ConfigurationManager, 'load')
    @patch('infrastructure.commander.SerialCommander')
    @patch('api.configuration_api.AudioDripZAxis')
    def test_send_dripper_off_command_should_raise_exceptions_if_serial_not_configured(self, mock_Zaxis, mock_SerialCommander, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.serial.on = False
        mock_load.return_value = config

        configuration_API.load_printer('Printer')
        configuration_API.start_counting_drips()
        with self.assertRaises(Exception):
            configuration_API.send_dripper_off_command()

        self.assertEquals(0, mock_SerialCommander.call_count)

    @patch.object(ConfigurationManager, 'load')
    @patch('api.configuration_api.SerialCommander')
    @patch('api.configuration_api.AudioDripZAxis')
    def test_send_dripper_off_command_should(self, mock_Zaxis, mock_SerialCommander, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.serial.on = True
        config.serial.port = "COM1"
        config.serial.off_command = "0"
        mock_load.return_value = config
        mock_serial_commander = mock_SerialCommander.return_value

        configuration_API.load_printer('Printer')
        configuration_API.start_counting_drips()
        configuration_API.send_dripper_off_command()

        mock_SerialCommander.assert_called_with("COM1")
        mock_serial_commander.send_command.assert_called_with("0")

    @patch.object(ConfigurationManager, 'load')
    @patch('api.configuration_api.SerialCommander')
    @patch('api.configuration_api.AudioDripZAxis')
    def test_stop_counting_drips_should_stop_serial(self, mock_Zaxis, mock_SerialCommander, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.serial.on = True
        config.serial.port = "COM1"
        config.serial.off_command = "0"
        mock_load.return_value = config
        mock_serial_commander = mock_SerialCommander.return_value

        configuration_API.load_printer('Printer')
        configuration_API.start_counting_drips()
        configuration_API.stop_counting_drips()

        mock_SerialCommander.assert_called_with("COM1")
        mock_serial_commander.close.assert_called_with()

    # ----------------------------- General Setup --------------------------------------

    @patch.object(ConfigurationManager, 'load' )
    def test_get_max_lead_distance_mm_returns_max_lead_distance(self, mock_load):
        expected = 0.4
        config = self.default_config
        config.dripper.max_lead_distance_mm = expected
        mock_load.return_value =  config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected,configuration_API.get_max_lead_distance_mm())

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_max_lead_distance_mm_sets_max_lead_distance_mm(self, mock_save, mock_load):
        expected = 0.4
        expected_config = self.default_config
        expected_config.dripper.max_lead_distance_mm = expected
        mock_load.return_value =  self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_max_lead_distance_mm(expected)

        self.assertEquals(expected,configuration_API.get_max_lead_distance_mm())
        self.assertConfigurationEqual(expected_config, mock_save.mock_calls[0][1][0])

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
        config = self.default_config
        config.options.laser_thickness_mm = expected
        mock_load.return_value =  config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected,configuration_API.get_laser_thickness_mm())

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_laser_thickness_mm_sets_thickness(self, mock_save, mock_load):
        expected_thickness = 7.0
        config =  self.default_config
        expected = config
        expected.options.laser_thickness_mm = expected_thickness
        mock_load.return_value =  config 
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_laser_thickness_mm(expected_thickness)

        self.assertEquals(expected_thickness,configuration_API.get_laser_thickness_mm())
        mock_save.assert_called_with(expected)

    patch.object(ConfigurationManager, 'load' )


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
    def test_get_scaling_factor_returns_thickness(self, mock_load):
        expected = 7.0
        config = self.default_config
        config.options.scaling_factor = expected
        mock_load.return_value =  config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected,configuration_API.get_scaling_factor())

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_scaling_factor_sets_scaling_factor(self, mock_save, mock_load):
        expected_scale = 7.0
        config =  self.default_config
        expected = config
        expected.options.scaling_factor = expected_scale
        mock_load.return_value =  config 
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_scaling_factor(expected_scale)

        self.assertEquals(expected_scale,configuration_API.get_scaling_factor())
        mock_save.assert_called_with(expected)


    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_scaling_factor_should_go_boom_if_not_positive_float(self, mock_save, mock_load):
        mock_load.return_value =   {'name':'test' }
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.set_scaling_factor('a')
        with self.assertRaises(Exception):
            configuration_API.set_scaling_factor(-1.0)
        with self.assertRaises(Exception):
            configuration_API.set_scaling_factor({'a':'b'})
        with self.assertRaises(Exception):
            configuration_API.set_scaling_factor(0)
        with self.assertRaises(Exception):
            configuration_API.set_scaling_factor(1)

    @patch.object(ConfigurationManager, 'load' )
    def test_sublayer_height_mm_returns_theight(self, mock_load):
        expected = 7.0
        expected_config = self.default_config
        expected_config.options.sublayer_height_mm = expected
        mock_load.return_value =  expected_config

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected,configuration_API.get_sublayer_height_mm())

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_sublayer_height_mm_returns_height(self, mock_save, mock_load):
        expected_height = 7.0
        config =  self.default_config
        expected = config
        expected.options.sublayer_height_mm = expected_height
        mock_load.return_value =  config 
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_sublayer_height_mm(expected_height)

        self.assertEquals(expected_height,configuration_API.get_sublayer_height_mm())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_sublayer_height_mm_should_go_boom_if_not_positive_float(self, mock_save, mock_load):
        mock_load.return_value =   self.default_config
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
        mock_load.return_value =  self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        actual_enabled = configuration_API.get_serial_enabled()
        actual_port = configuration_API.get_serial_port()
        actual_on = configuration_API.get_serial_on_command()
        actual_off = configuration_API.get_serial_off_command()

        self.assertEquals(self.default_config.serial.on, actual_enabled)
        self.assertEquals(self.default_config.serial.port, actual_port)
        self.assertEquals(self.default_config.serial.on_command, actual_on)
        self.assertEquals(self.default_config.serial.off_command, actual_off)

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_get_serial_options_loads_correctly(self, mock_save, mock_load):
        expected_enabled = True
        expected_port = 'com54'
        expected_on = 'GOGOGO'
        expected_off = 'STOPSTOP'

        mock_load.return_value =  self.default_config
        expected = self.default_config
        expected.serial.on = expected_enabled
        expected.serial.port      = expected_port
        expected.serial.on_command        = expected_on
        expected.serial.off_command       = expected_off

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_serial_enabled(expected_enabled)
        configuration_API.set_serial_port(expected_port)
        configuration_API.set_serial_on_command(expected_on)
        configuration_API.set_serial_off_command(expected_off)

        self.assertEquals( expected_enabled ,configuration_API.get_serial_enabled())
        self.assertEquals( expected_port ,configuration_API.get_serial_port())
        self.assertEquals( expected_on ,configuration_API.get_serial_on_command())
        self.assertEquals( expected_off ,configuration_API.get_serial_off_command())

        self.assertConfigurationEqual(expected, mock_save.mock_calls[0][1][0])

#-----------------------------------------Cure Test Setup Tests -----------------------------------

    @patch.object(ConfigurationManager, 'load' )
    def test_get_cure_test_total_height_must_exceed_base_height(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_cure_test(10,1,1,2)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1,1,1,2)


    @patch.object(ConfigurationManager, 'load' )
    def test_get_cure_test_final_speed_exceeds_start_speed(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1,10,10,1)

        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1,10,1,1)

    @patch.object(ConfigurationManager, 'load' )
    def test_get_cure_test_values_must_be_positive_non_0_numbers_for_all_but_base(self, mock_load):
        mock_load.return_value = self.default_config
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
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")
        
        cure_test = configuration_API.get_cure_test(0,1,1,2)
        cure_test.next()

    @patch.object(ConfigurationManager, 'load' )
    def test_get_speed_at_height_must_exceed_base_height(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(10,1,1,2,1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1,1,1,2,1)

    @patch.object(ConfigurationManager, 'load' )
    def test_get_speed_at_height_must_have_height_between_total_and_base(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(0,10,1,2,11)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(2,10,1,2,0)

    @patch.object(ConfigurationManager, 'load' )
    def test_get_speed_at_height_final_speed_exceeds_start_speed(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1,10,10,1,1)

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1,10,1,1,1)

    @patch.object(ConfigurationManager, 'load' )
    def test_get_speed_at_height_values_must_be_positive_non_0_numbers_for_all_but_base(self, mock_load):
        mock_load.return_value = self.default_config
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
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")
        
        speed = configuration_API.get_speed_at_height(0,1,10,20,0.5)
        self.assertEquals(15, speed)

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_speed(self, mock_save, mock_load):
        mock_load.return_value = self.default_config
        expected = self.default_config
        expected.options.draw_speed = 121.0
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")
        
        configuration_API.set_speed(121)
        
        self.assertConfigurationEqual(expected, mock_save.mock_calls[0][1][0])

    @patch.object(ConfigurationManager, 'load' )
    @patch.object(ConfigurationManager, 'save' )
    def test_set_speed_should_throw_exception_if_less_then_or_0(self, mock_save, mock_load):
        mock_load.return_value = self.default_config
        expected_config = self.default_config
        expected_config.options.draw_speed = 121.0
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