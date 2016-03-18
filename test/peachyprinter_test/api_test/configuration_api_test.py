import unittest
import os
import sys

from mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from peachyprinter.api.configuration_api import ConfigurationAPI
from peachyprinter.domain.configuration_manager import ConfigurationManager
from peachyprinter.infrastructure.zaxis import SerialDripZAxis
from peachyprinter.infrastructure.communicator import UsbPacketCommunicator
import test_helpers


class InfoMixInTest(object):

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_get_and_set_info(self, mock_save, mock_load):
        expected_info_version_number = "TBD"
        expected_info_serial_number = "sn1"
        expected_info_hardware_version_number = "hw1"
        expected_info_firmware_version_number = "sw1"
        expected_info_firmware_data_rate = 0
        expected_info_print_queue_length = 500
        expected_info_calibration_queue_length = 50

        expected_config = self.default_config

        expected_config.circut.version_number             = expected_info_version_number
        expected_config.circut.serial_number              = expected_info_serial_number
        expected_config.circut.hardware_version_number    = expected_info_hardware_version_number
        expected_config.circut.firmware_version_number    = expected_info_firmware_version_number
        expected_config.circut.firmware_data_rate         = expected_info_firmware_data_rate
        expected_config.circut.print_queue_length         = expected_info_print_queue_length
        expected_config.circut.calibration_queue_length   = expected_info_calibration_queue_length

        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        configuration_API.set_info_print_queue_length(expected_info_print_queue_length)
        configuration_API.set_info_calibration_queue_length(expected_info_calibration_queue_length)

        configuration_API.save()

        self.assertConfigurationEqual(expected_config, mock_save.mock_calls[0][1][0])

        self.assertEquals(expected_info_version_number,              configuration_API.get_info_version_number())
        self.assertEquals(expected_info_serial_number,               configuration_API.get_info_serial_number())
        self.assertEquals(expected_info_hardware_version_number,     configuration_API.get_info_hardware_version_number())
        self.assertEquals(expected_info_firmware_version_number,     configuration_API.get_info_firmware_version_number())
        self.assertEquals(expected_info_firmware_data_rate,          configuration_API.get_info_firmware_data_rate())
        self.assertEquals(expected_info_print_queue_length,          configuration_API.get_info_print_queue_length())
        self.assertEquals(expected_info_calibration_queue_length,    configuration_API.get_info_calibration_queue_length())

class DripperSetupMixInTest(object):

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch('peachyprinter.api.configuration_api.UsbPacketCommunicator')
    def test_start_counting_drips_should_start_getting_drips(self, mock_UsbPacketCommunicator,  mock_load, mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer()

        configuration_API.start_counting_drips()

        mock_UsbPacketCommunicator.return_value.start.assert_called_with()

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch('peachyprinter.api.configuration_api.SerialDripZAxis')
    @patch('peachyprinter.api.configuration_api.UsbPacketCommunicator')
    def test_start_counting_drips_should_start_getting_drips_for_microcontroller(self, mock_UsbPacketCommunicator, mock_SerialDripZaxis, mock_load, mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.dripper.dripper_type ='microcontroller'
        mock_load.return_value = config
        configuration_API.load_printer()
        callback = MagicMock()
        configuration_API.start_counting_drips(callback)

        mock_UsbPacketCommunicator.assert_called_with(config.circut.calibration_queue_length)
        mock_UsbPacketCommunicator.return_value.start.assert_called_with()
        mock_SerialDripZaxis.assert_called_with(mock_UsbPacketCommunicator.return_value, 1, 0, drip_call_back=callback)

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(SerialDripZAxis, 'start')
    @patch('peachyprinter.api.configuration_api.UsbPacketCommunicator')
    @patch('peachyprinter.api.configuration_api.SerialDripZAxis')
    def test_start_counting_drips_should_pass_call_back_function(self, mock_SerialDripZAxis, mock_UsbPacketCommunicator, mock_start, mock_load, mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer()

        def callback(bla):
            pass

        configuration_API.start_counting_drips(drip_call_back=callback)

        mock_SerialDripZAxis.assert_called_with(
            mock_UsbPacketCommunicator.return_value,
            1,
            0.0,
            drip_call_back=callback
            )

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch('peachyprinter.api.configuration_api.SerialDripZAxis')
    @patch('peachyprinter.api.configuration_api.UsbPacketCommunicator')
    def test_stop_counting_drips_should_stop_getting_drips_for_micro(self, mock_UsbPacketCommunicator, mock_SerialDripZaxis, mock_load, mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.dripper.dripper_type ='microcontroller'
        mock_load.return_value = config
        configuration_API.load_printer()
        callback = MagicMock()
        configuration_API.start_counting_drips(callback)

        configuration_API.stop_counting_drips()

        mock_UsbPacketCommunicator.return_value.close.assert_called_with()

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(SerialDripZAxis, 'start')
    @patch('peachyprinter.api.configuration_api.UsbPacketCommunicator')
    @patch.object(SerialDripZAxis, 'close')
    def test_stop_counting_drips_should_stop_getting_drips(self, mock_close, mock_UsbPacketCommunicator, mock_start, mock_load, mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer()
        configuration_API.start_counting_drips()

        configuration_API.stop_counting_drips()

        mock_close.assert_called_with()

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(SerialDripZAxis, 'start')
    @patch('peachyprinter.api.configuration_api.UsbPacketCommunicator')
    @patch.object(SerialDripZAxis, 'reset')
    def test_drip_calibration_should_call_reset_when_reset_requested(self, mock_reset, mock_UsbPacketCommunicator, mock_start, mock_load, mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer()

        configuration_API.start_counting_drips()
        configuration_API.reset_drips()

        mock_reset.assert_called_with()

    @patch.object(ConfigurationManager, 'load')
    def test_get_dripper_drips_per_mm_should_return_current_setting(self, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config

        configuration_API.load_printer()

        actual = configuration_API.get_dripper_drips_per_mm()

        self.assertEquals(self.default_config.dripper.drips_per_mm, actual)

    @patch.object(ConfigurationManager, 'load')
    @patch('peachyprinter.api.configuration_api.SerialDripZAxis')
    @patch('peachyprinter.api.configuration_api.UsbPacketCommunicator')
    @patch.object(ConfigurationManager, 'save')
    def test_set_dripper_drips_per_mm_should_overwrite_current_setting_and_update_zaxis(self, mock_save, mock_UsbPacketCommunicator, mock_SerialDripZAxis, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        mock_SerialDripZAxis = mock_SerialDripZAxis.return_value
        expected = 6534.0

        configuration_API.load_printer()
        configuration_API.start_counting_drips()
        configuration_API.set_dripper_drips_per_mm(expected)
        configuration_API.stop_counting_drips()

        mock_SerialDripZAxis.set_drips_per_mm.assert_called_with(expected)
        mock_save.assert_called()

    @patch.object(ConfigurationManager, 'load')
    def test_get_dripper_type_should_return_current_type(self, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer()

        actual = configuration_API.get_dripper_type()

        self.assertEquals(self.default_config.dripper.dripper_type, actual)

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_dripper_type_should_return_current_type(self, mock_save, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer()
        expected = 'emulated'
        configuration_API.set_dripper_type(expected)
        actual = configuration_API.get_dripper_type()

        self.assertEquals(expected, actual)
        mock_save.assert_called()

    @patch.object(ConfigurationManager, 'load')
    def test_get_dripper_delay_should_return_current_delay(self, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer()

        actual = configuration_API.get_dripper_photo_zaxis_delay()

        self.assertEquals(self.default_config.dripper.photo_zaxis_delay, actual)

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_dripper_delay_should_set_current_delay(self, mock_save, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer()
        expected = 2.0
        configuration_API.set_dripper_photo_zaxis_delay(expected)
        actual = configuration_API.get_dripper_photo_zaxis_delay()

        self.assertEquals(expected, actual)
        mock_save.assert_called
    @patch.object(ConfigurationManager, 'load')
    def test_get_dripper_emulated_drips_per_second_should_return(self, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer()

        actual = configuration_API.get_dripper_emulated_drips_per_second()

        self.assertEquals(self.default_config.dripper.emulated_drips_per_second, actual)

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_dripper_emulated_drips_per_second_should_return(self, mock_save, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer()
        expected = 302.0
        configuration_API.set_dripper_emulated_drips_per_second(expected)
        actual = configuration_API.get_dripper_emulated_drips_per_second() 

        self.assertEquals(expected, actual)
        mock_save.assert_called()

    @patch.object(ConfigurationManager, 'load')
    @patch('peachyprinter.infrastructure.commander.SerialCommander')
    @patch('peachyprinter.api.configuration_api.SerialDripZAxis')
    @patch('peachyprinter.api.configuration_api.UsbPacketCommunicator')
    def test_send_dripper_on_command_should_raise_exceptions_if_serial_not_configured(self, mock_UsbPacketCommunicator, mock_Zaxis, mock_SerialCommander, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.serial.on = False
        mock_load.return_value = config

        configuration_API.load_printer()
        configuration_API.start_counting_drips()
        with self.assertRaises(Exception):
            configuration_API.send_dripper_on_command()

        self.assertEquals(0, mock_SerialCommander.call_count)

    @patch.object(ConfigurationManager, 'load')
    @patch('peachyprinter.api.configuration_api.SerialCommander')
    @patch('peachyprinter.api.configuration_api.SerialDripZAxis')
    @patch('peachyprinter.api.configuration_api.UsbPacketCommunicator')
    def test_send_dripper_on_command_should(self, mock_UsbPacketCommunicator, mock_Zaxis, mock_SerialCommander, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.serial.on = True
        config.serial.port = "COM1"
        config.serial.on_command = "1"
        mock_load.return_value = config
        mock_serial_commander = mock_SerialCommander.return_value

        configuration_API.load_printer()
        configuration_API.start_counting_drips()
        configuration_API.send_dripper_on_command()

        mock_SerialCommander.assert_called_with("COM1")
        mock_serial_commander.send_command.assert_called_with("1")

    @patch.object(ConfigurationManager, 'load')
    @patch('peachyprinter.infrastructure.commander.SerialCommander')
    @patch('peachyprinter.api.configuration_api.SerialDripZAxis')
    @patch('peachyprinter.api.configuration_api.UsbPacketCommunicator')
    def test_send_dripper_off_command_should_raise_exceptions_if_serial_not_configured(self, mock_UsbPacketCommunicator, mock_Zaxis, mock_SerialCommander, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.serial.on = False
        mock_load.return_value = config

        configuration_API.load_printer()
        configuration_API.start_counting_drips()
        with self.assertRaises(Exception):
            configuration_API.send_dripper_off_command()

        self.assertEquals(0, mock_SerialCommander.call_count)

    @patch.object(ConfigurationManager, 'load')
    @patch('peachyprinter.api.configuration_api.SerialCommander')
    @patch('peachyprinter.api.configuration_api.SerialDripZAxis')
    @patch('peachyprinter.api.configuration_api.UsbPacketCommunicator')
    def test_send_dripper_off_command_should(self, mock_UsbPacketCommunicator, mock_Zaxis, mock_SerialCommander, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.serial.on = True
        config.serial.port = "COM1"
        config.serial.off_command = "0"
        mock_load.return_value = config
        mock_serial_commander = mock_SerialCommander.return_value

        configuration_API.load_printer()
        configuration_API.start_counting_drips()
        configuration_API.send_dripper_off_command()

        mock_SerialCommander.assert_called_with("COM1")
        mock_serial_commander.send_command.assert_called_with("0")

    @patch.object(ConfigurationManager, 'load')
    @patch('peachyprinter.api.configuration_api.SerialCommander')
    @patch('peachyprinter.api.configuration_api.SerialDripZAxis')
    @patch('peachyprinter.api.configuration_api.UsbPacketCommunicator')
    def test_stop_counting_drips_should_stop_serial(self, mock_UsbPacketCommunicator, mock_Zaxis, mock_SerialCommander, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.serial.on = True
        config.serial.port = "COM1"
        config.serial.off_command = "0"
        mock_load.return_value = config
        mock_serial_commander = mock_SerialCommander.return_value

        configuration_API.load_printer()
        configuration_API.start_counting_drips()
        configuration_API.stop_counting_drips()

        mock_SerialCommander.assert_called_with("COM1")
        mock_serial_commander.close.assert_called_with()


class CureTestSetupMixInTest(object):

    @patch.object(ConfigurationManager, 'load')
    def test_get_cure_test_total_height_must_exceed_base_height(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        with self.assertRaises(Exception):
            configuration_API.get_cure_test(10, 1, 1, 2)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 1, 1, 2)

    @patch.object(ConfigurationManager, 'load')
    def test_get_cure_test_final_speed_exceeds_start_speed(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 10, 1)

        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 1, 1)

    @patch.object(ConfigurationManager, 'load')
    def test_get_cure_test_values_must_be_positive_non_0_numbers_for_all_but_base(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        with self.assertRaises(Exception):
            configuration_API.get_cure_test('a', 10, 10, 1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 'a', 10, 1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 'a', 1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 10, 'a')
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 10, 1, 'a')
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(-1, 10, 10, 1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, -10, 10, 1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, -1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 10, -1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 10, 1, -1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 0, 10, 1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 0, 1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 10, 0)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 10, 1, 0)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 10, 11, base_speed=0)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 10, 11, base_speed=-1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 10, 11, base_speed='a')

    @patch.object(ConfigurationManager, 'load')
    def test_get_cure_test_returns_a_layer_generator(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        cure_test = configuration_API.get_cure_test(0, 1, 1, 2, 3)
        cure_test.next()

    @patch.object(ConfigurationManager, 'load')
    def test_get_speed_at_height_must_exceed_base_height(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(10, 1, 1, 2, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 1, 1, 2, 1)

    @patch.object(ConfigurationManager, 'load')
    def test_get_speed_at_height_must_have_height_between_total_and_base(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(0, 10, 1, 2, 11)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(2, 10, 1, 2, 0)

    @patch.object(ConfigurationManager, 'load')
    def test_get_speed_at_height_final_speed_exceeds_start_speed(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 10, 1, 1)

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 1, 1, 1)

    @patch.object(ConfigurationManager, 'load')
    def test_get_speed_at_height_values_must_be_positive_non_0_numbers_for_all_but_base(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height('a', 10, 10, 1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 'a', 10, 1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 'a', 1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 10, 'a', 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 10, 1, 'a', 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(-1, 10, 10, 1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, -10, 10, 1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, -1, 1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 10, -1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 10, 1, -1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 0, 10, 1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 0, 1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 10, 0, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 10, 1, 0, 1)

    @patch.object(ConfigurationManager, 'load')
    def test_get_speed_at_height_returns_a_correct_height(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        speed = configuration_API.get_speed_at_height(0, 1, 10, 20, 0.5)
        self.assertEquals(15, speed)

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_cure_rate_draw_speed_should_throw_exception_if_less_then_or_0(self, mock_save, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        with self.assertRaises(Exception):
            configuration_API.set_cure_rate_draw_speed(-1)
        with self.assertRaises(Exception):
            configuration_API.set_cure_rate_draw_speed(0)

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_cure_rate_move_speed_should_throw_exception_if_less_then_or_0(self, mock_save, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        with self.assertRaises(Exception):
            configuration_API.set_cure_rate_move_speed(-1)
        with self.assertRaises(Exception):
            configuration_API.set_cure_rate_move_speed(0)

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_cure_rate_draw_speed_should_set(self, mock_save, mock_load):
        mock_load.return_value = self.default_config
        expected_speed = 121.0
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()
        configuration_API.set_cure_rate_draw_speed(121.0)
        self.assertEquals(expected_speed, configuration_API.get_cure_rate_draw_speed())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_cure_rate_move_speed_should_set(self, mock_save, mock_load):
        mock_load.return_value = self.default_config
        expected_speed = 121.0
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()
        configuration_API.set_cure_rate_move_speed(121.0)
        self.assertEquals(expected_speed, configuration_API.get_cure_rate_move_speed())

    @patch.object(ConfigurationManager, 'load')
    def test_get_layer_settings(self, mock_load):
        config = self.default_config
        config.options.use_shufflelayers = True
        config.options.use_sublayers = True
        config.options.use_overlap = True

        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        self.assertTrue(configuration_API.get_options_use_shufflelayers())
        self.assertTrue(configuration_API.get_options_use_sublayers())
        self.assertTrue(configuration_API.get_options_use_overlap())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_layer_settings(self, mock_save, mock_load):
        mock_load.return_value = self.default_config
        expected = self.default_config
        expected.options.use_shufflelayers = False
        expected.options.use_sublayers = False
        expected.options.use_overlap = False

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        configuration_API.set_options_use_shufflelayers(False)
        configuration_API.set_options_use_sublayers(False)
        configuration_API.set_options_use_overlap(False)

        self.assertConfigurationEqual(expected, mock_save.mock_calls[0][1][0])

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_get_and_set_cure_test_details(self, mock_save, mock_load):
        expected_base_height = 3.0
        expected_total_height = 33.0
        expected_start_speed = 10.0
        expected_finish_speed = 100.0
        expected_draw_speed = 75.0
        expected_use_draw_speed = False
        expected_override_laser_power = True
        expected_override_laser_power_amount = 0.05

        expected_config = self.default_config

        expected_config.cure_rate.base_height = expected_base_height
        expected_config.cure_rate.total_height = expected_total_height
        expected_config.cure_rate.start_speed = expected_start_speed
        expected_config.cure_rate.finish_speed = expected_finish_speed
        expected_config.cure_rate.draw_speed = expected_draw_speed
        expected_config.cure_rate.use_draw_speed = expected_use_draw_speed
        expected_config.cure_rate.override_laser_power = expected_override_laser_power
        expected_config.cure_rate.override_laser_power_amount = expected_override_laser_power_amount

        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        configuration_API.set_cure_rate_base_height(expected_base_height)
        configuration_API.set_cure_rate_total_height(expected_total_height)
        configuration_API.set_cure_rate_start_speed(expected_start_speed)
        configuration_API.set_cure_rate_finish_speed(expected_finish_speed)
        configuration_API.set_cure_rate_draw_speed(expected_draw_speed)
        configuration_API.set_cure_rate_use_draw_speed(expected_use_draw_speed)
        configuration_API.set_cure_rate_override_laser_power(expected_override_laser_power)
        configuration_API.set_cure_rate_override_laser_power_amount(expected_override_laser_power_amount)

        configuration_API.save()

        self.assertConfigurationEqual(expected_config, mock_save.mock_calls[0][1][0])

        self.assertEquals(expected_base_height,                     configuration_API.get_cure_rate_base_height())
        self.assertEquals(expected_total_height,                    configuration_API.get_cure_rate_total_height())
        self.assertEquals(expected_start_speed,                     configuration_API.get_cure_rate_start_speed())
        self.assertEquals(expected_finish_speed,                    configuration_API.get_cure_rate_finish_speed())
        self.assertEquals(expected_draw_speed,                      configuration_API.get_cure_rate_draw_speed())
        self.assertEquals(expected_use_draw_speed,                  configuration_API.get_cure_rate_use_draw_speed())
        self.assertEquals(expected_override_laser_power,            configuration_API.get_override_laser_power())
        self.assertEquals(expected_override_laser_power_amount,     configuration_API.get_override_laser_power_amount())

    @patch.object(ConfigurationManager, 'load')
    def test_get_and_set_laser_amount_fails_if_out_of_range(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        with self.assertRaises(Exception):
            configuration_API.set_cure_rate_override_laser_power_amount(-0.1)
        with self.assertRaises(Exception):
            configuration_API.set_cure_rate_override_laser_power_amount(-1.0)
        with self.assertRaises(Exception):
            configuration_API.set_cure_rate_override_laser_power_amount(1.1)

        configuration_API.set_cure_rate_override_laser_power_amount(0.0)
        # configuration_API.set_cure_rate_override_laser_power_amount(0.5)
        # configuration_API.set_cure_rate_override_laser_power_amount(1.0)
        #TODO FIX THIS AGAIN


class OptionsSetupMixInTest(object):

    @patch.object(ConfigurationManager, 'load')
    def test_get_wait_after_move_milliseconds_returns_wait_after_move_milliseconds(self, mock_load):
        expected = 7
        config = self.default_config
        config.options.wait_after_move_milliseconds = expected
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        self.assertEquals(expected, configuration_API.get_options_wait_after_move_milliseconds())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_wait_after_move_milliseconds_sets_wait_after_move_milliseconds(self, mock_save, mock_load):
        expected_milliseconds = 7
        config = self.default_config
        expected = config
        expected.options.wait_after_move_milliseconds = expected_milliseconds
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        configuration_API.set_options_wait_after_move_milliseconds(expected_milliseconds)

        self.assertEquals(expected_milliseconds, configuration_API.get_options_wait_after_move_milliseconds())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    def test_get_pre_layer_delay_returns_delay(self, mock_load):
        expected = 7.0
        config = self.default_config
        config.options.pre_layer_delay = expected
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        self.assertEquals(expected, configuration_API.get_options_pre_layer_delay())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_pre_layer_delay_sets_pre_layer_delay(self, mock_save, mock_load):
        expected_scale = 7.0
        config = self.default_config
        expected = config
        expected.options.pre_layer_delay = expected_scale
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        configuration_API.set_options_pre_layer_delay(expected_scale)

        self.assertEquals(expected_scale, configuration_API.get_options_pre_layer_delay())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    def test_get_max_lead_distance_mm_returns_max_lead_distance(self, mock_load):
        expected = 0.4
        config = self.default_config
        config.dripper.max_lead_distance_mm = expected
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        self.assertEquals(expected, configuration_API.get_options_max_lead_distance_mm())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_max_lead_distance_mm_sets_max_lead_distance_mm(self, mock_save, mock_load):
        expected = 0.4
        expected_config = self.default_config
        expected_config.dripper.max_lead_distance_mm = expected
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        configuration_API.set_options_max_lead_distance_mm(expected)

        self.assertEquals(expected, configuration_API.get_options_max_lead_distance_mm())
        self.assertConfigurationEqual(expected_config, mock_save.mock_calls[0][1][0])

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_max_lead_distance_mm_sets_max_lead_distance_mm_when_0(self, mock_save, mock_load):
        expected = 0.0
        expected_config = self.default_config
        expected_config.dripper.max_lead_distance_mm = expected
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        configuration_API.set_options_max_lead_distance_mm(expected)

        self.assertEquals(expected, configuration_API.get_options_max_lead_distance_mm())
        self.assertConfigurationEqual(expected_config, mock_save.mock_calls[0][1][0])

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_max_lead_distance_mm_should_go_boom_if_not_positive_float(self, mock_save, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        with self.assertRaises(Exception):
            configuration_API.set_options_max_lead_distance_mm('a')
        with self.assertRaises(Exception):
            configuration_API.set_options_max_lead_distance_mm(-1.0)
        with self.assertRaises(Exception):
            configuration_API.set_options_max_lead_distance_mm({'a': 'b'})
        with self.assertRaises(Exception):
            configuration_API.set_options_max_lead_distance_mm(0)
        with self.assertRaises(Exception):
            configuration_API.set_options_max_lead_distance_mm(1)

    @patch.object(ConfigurationManager, 'load')
    def test_get_laser_thickness_mm_returns_thickness(self, mock_load):
        expected = 7.0
        config = self.default_config
        config.options.laser_thickness_mm = expected
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        self.assertEquals(expected, configuration_API.get_options_laser_thickness_mm())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_laser_thickness_mm_sets_thickness(self, mock_save, mock_load):
        expected_thickness = 7.0
        config = self.default_config
        expected = config
        expected.options.laser_thickness_mm = expected_thickness
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        configuration_API.set_options_laser_thickness_mm(expected_thickness)

        self.assertEquals(expected_thickness, configuration_API.get_options_laser_thickness_mm())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_laser_thickness_mm_should_go_boom_if_not_positive_float(self, mock_save, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        with self.assertRaises(Exception):
            configuration_API.set_options_laser_thickness_mm('a')
        with self.assertRaises(Exception):
            configuration_API.set_options_laser_thickness_mm(-1.0)
        with self.assertRaises(Exception):
            configuration_API.set_options_laser_thickness_mm({'a': 'b'})
        with self.assertRaises(Exception):
            configuration_API.set_options_laser_thickness_mm(0)
        with self.assertRaises(Exception):
            configuration_API.set_options_laser_thickness_mm(1)

    @patch.object(ConfigurationManager, 'load')
    def test_get_scaling_factor_returns_thickness(self, mock_load):
        expected = 7.0
        config = self.default_config
        config.options.scaling_factor = expected
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        self.assertEquals(expected, configuration_API.get_options_scaling_factor())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_scaling_factor_sets_scaling_factor(self, mock_save, mock_load):
        expected_scale = 7.0
        config = self.default_config
        expected = config
        expected.options.scaling_factor = expected_scale
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        configuration_API.set_options_scaling_factor(expected_scale)

        self.assertEquals(expected_scale, configuration_API.get_options_scaling_factor())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_scaling_factor_should_go_boom_if_not_positive_float(self, mock_save, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        with self.assertRaises(Exception):
            configuration_API.set_options_scaling_factor('a')
        with self.assertRaises(Exception):
            configuration_API.set_options_scaling_factor(-1.0)
        with self.assertRaises(Exception):
            configuration_API.set_options_scaling_factor({'a': 'b'})
        with self.assertRaises(Exception):
            configuration_API.set_options_scaling_factor(0)
        with self.assertRaises(Exception):
            configuration_API.set_options_scaling_factor(1)

    @patch.object(ConfigurationManager, 'load')
    def test_sublayer_height_mm_returns_theight(self, mock_load):
        expected = 7.0
        expected_config = self.default_config
        expected_config.options.sublayer_height_mm = expected
        mock_load.return_value = expected_config

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        self.assertEquals(expected, configuration_API.get_options_sublayer_height_mm())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_sublayer_height_mm_returns_height(self, mock_save, mock_load):
        expected_height = 7.0
        config = self.default_config
        expected = config
        expected.options.sublayer_height_mm = expected_height
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        configuration_API.set_options_sublayer_height_mm(expected_height)

        self.assertEquals(expected_height, configuration_API.get_options_sublayer_height_mm())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_sublayer_height_mm_should_go_boom_if_not_positive_float(self, mock_save, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        with self.assertRaises(Exception):
            configuration_API.set_options_sublayer_height_mm('a')
        with self.assertRaises(Exception):
            configuration_API.set_options_sublayer_height_mm(-1.0)
        with self.assertRaises(Exception):
            configuration_API.set_options_sublayer_height_mm({'a': 'b'})
        with self.assertRaises(Exception):
            configuration_API.set_options_sublayer_height_mm(0)
        with self.assertRaises(Exception):
            configuration_API.set_options_sublayer_height_mm(1)

    @patch.object(ConfigurationManager, 'load')
    def test_get_slew_delay_returns_the_amount(self, mock_load):
        expected = 3
        expected_config = self.default_config
        expected_config.options.slew_delay = expected
        mock_load.return_value = expected_config

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        self.assertEquals(expected, configuration_API.get_options_slew_delay())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_slew_delay_returns_amount(self, mock_save, mock_load):
        slew_delay = 7
        config = self.default_config
        expected = config
        expected.options.slew_delay = slew_delay
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        configuration_API.set_options_slew_delay(slew_delay)

        self.assertEquals(slew_delay, configuration_API.get_options_slew_delay())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    def test_get_post_fire_delay_returns_the_amount(self, mock_load):
        expected = 3
        expected_config = self.default_config
        expected_config.options.post_fire_delay = expected
        mock_load.return_value = expected_config

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        self.assertEquals(expected, configuration_API.get_options_post_fire_delay())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_post_fire_delay_returns_amount(self, mock_save, mock_load):
        post_fire_delay = 7
        config = self.default_config
        expected = config
        expected.options.post_fire_delay = post_fire_delay
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        configuration_API.set_options_post_fire_delay(post_fire_delay)

        self.assertEquals(post_fire_delay, configuration_API.get_options_post_fire_delay())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    def test_get_shuffle_amount_returns_the_amount(self, mock_load):
        expected = 0.1
        expected_config = self.default_config
        expected_config.options.shuffle_layers_amount = expected
        mock_load.return_value = expected_config

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        self.assertEquals(expected, configuration_API.get_options_shuffle_layers_amount())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_shuffle_layers_amount_returns_amount(self, mock_save, mock_load):
        shuffle_layers_amount = 7.0
        config = self.default_config
        expected = config
        expected.options.shuffle_layers_amount = shuffle_layers_amount
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        configuration_API.set_options_shuffle_layers_amount(shuffle_layers_amount)

        self.assertEquals(shuffle_layers_amount, configuration_API.get_options_shuffle_layers_amount())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    def test_get_overlap_amount_mm_returns_the_overlap(self, mock_load):
        expected = 7.0
        expected_config = self.default_config
        expected_config.options.overlap_amount = expected
        mock_load.return_value = expected_config

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        self.assertEquals(expected, configuration_API.get_options_overlap_amount_mm())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_overlap_amount_mm_returns_height(self, mock_save, mock_load):
        overlap_amount = 7.0
        config = self.default_config
        expected = config
        expected.options.overlap_amount = overlap_amount
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        configuration_API.set_options_overlap_amount_mm(overlap_amount)

        self.assertEquals(overlap_amount, configuration_API.get_options_overlap_amount_mm())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    def test_get_print_queue_delay_returns_the_delay(self, mock_load):
        expected = 7.0
        expected_config = self.default_config
        expected_config.options.print_queue_delay = expected
        mock_load.return_value = expected_config

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        self.assertEquals(expected, configuration_API.get_options_print_queue_delay())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_print_queue_delay_returns_delay(self, mock_save, mock_load):
        print_queue_delay = 7.0
        config = self.default_config
        expected = config
        expected.options.print_queue_delay = print_queue_delay
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        configuration_API.set_options_print_queue_delay(print_queue_delay)

        self.assertEquals(print_queue_delay, configuration_API.get_options_print_queue_delay())
        mock_save.assert_called_with(expected)


class EmailSetupMixInTest(object):

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_get_and_set_email_details(self, mock_save, mock_load):
        expected_on = True
        expected_port = 33
        expected_host = "some.host"
        expected_sender = "sender@email.com"
        expected_recipient = "recipient@email.com"
        expected_username = "sender"
        expected_password = "pa55word"

        expected_config = self.default_config

        expected_config.email.on = expected_on
        expected_config.email.port = expected_port
        expected_config.email.host = expected_host
        expected_config.email.sender = expected_sender
        expected_config.email.recipient = expected_recipient
        expected_config.email.username = expected_username
        expected_config.email.password = expected_password

        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        configuration_API.set_email_on(expected_on)
        configuration_API.set_email_port(expected_port)
        configuration_API.set_email_host(expected_host)
        configuration_API.set_email_sender(expected_sender)
        configuration_API.set_email_recipient(expected_recipient)
        configuration_API.set_email_username(expected_username)
        configuration_API.set_email_password(expected_password)

        configuration_API.save()

        self.assertConfigurationEqual(expected_config, mock_save.mock_calls[0][1][0])

        self.assertEquals(expected_on, configuration_API.get_email_on())
        self.assertEquals(expected_port, configuration_API.get_email_port())
        self.assertEquals(expected_host, configuration_API.get_email_host())
        self.assertEquals(expected_sender, configuration_API.get_email_sender())
        self.assertEquals(expected_recipient, configuration_API.get_email_recipient())
        self.assertEquals(expected_username, configuration_API.get_email_username())
        self.assertEquals(expected_password, configuration_API.get_email_password())


class SerialSetupMixInTest(object):

    @patch.object(ConfigurationManager, 'load')
    def test_get_serial_options_loads_correctly(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        actual_enabled = configuration_API.get_serial_enabled()
        actual_port = configuration_API.get_serial_port()
        actual_on = configuration_API.get_serial_on_command()
        actual_off = configuration_API.get_serial_off_command()
        actual_layer_start = configuration_API.get_serial_layer_started_command()
        actual_layer_ended = configuration_API.get_serial_layer_ended_command()

        self.assertEquals(self.default_config.serial.on, actual_enabled)
        self.assertEquals(self.default_config.serial.port, actual_port)
        self.assertEquals(self.default_config.serial.on_command, actual_on)
        self.assertEquals(self.default_config.serial.off_command, actual_off)
        self.assertEquals(self.default_config.serial.layer_started, actual_layer_start)
        self.assertEquals(self.default_config.serial.layer_ended, actual_layer_ended)

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_serial_options_loads_correctly(self, mock_save, mock_load):
        expected_enabled = True
        expected_port = 'com54'
        expected_on = 'GOGOGO'
        expected_off = 'STOPSTOP'
        expected_layer_start = 'S'
        expected_layer_end = 'E'
        expected_print_end = 'Z'

        mock_load.return_value = self.default_config
        expected = self.default_config
        expected.serial.on                = expected_enabled
        expected.serial.port              = expected_port
        expected.serial.on_command        = expected_on
        expected.serial.off_command       = expected_off
        expected.serial.layer_started     = expected_layer_start
        expected.serial.layer_ended       = expected_layer_end
        expected.serial.print_ended       = expected_print_end

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer()

        configuration_API.set_serial_enabled(expected_enabled)
        configuration_API.set_serial_port(expected_port)
        configuration_API.set_serial_on_command(expected_on)
        configuration_API.set_serial_off_command(expected_off)
        configuration_API.set_serial_layer_started_command(expected_layer_start)
        configuration_API.set_serial_layer_ended_command(expected_layer_end)
        configuration_API.set_serial_print_ended_command(expected_print_end)

        self.assertEquals(expected_enabled, configuration_API.get_serial_enabled())
        self.assertEquals(expected_port, configuration_API.get_serial_port())
        self.assertEquals(expected_on, configuration_API.get_serial_on_command())
        self.assertEquals(expected_off, configuration_API.get_serial_off_command())
        self.assertEquals(expected_layer_start, configuration_API.get_serial_layer_started_command())
        self.assertEquals(expected_layer_end, configuration_API.get_serial_layer_ended_command())
        self.assertEquals(expected_print_end, configuration_API.get_serial_print_ended_command())

        self.assertConfigurationEqual(expected, mock_save.mock_calls[0][1][0])


class ConfigurationAPITest(
        unittest.TestCase,
        test_helpers.TestHelpers,
        InfoMixInTest,
        DripperSetupMixInTest,
        CureTestSetupMixInTest,
        OptionsSetupMixInTest,
        EmailSetupMixInTest,
        SerialSetupMixInTest,
        ):


    @patch.object(ConfigurationManager, 'load')
    def test_current_printer_returns_printer_name(self, mock_load):
        capi = ConfigurationAPI(ConfigurationManager())
        name = "Spam"
        config = self.default_config
        config.name = name
        mock_load.return_value = config

        capi.load_printer()
        actual = capi.current_printer()

        self.assertEqual('Spam', actual)

    @patch.object(ConfigurationManager, 'load')
    def test_load_printer_calls_load(self, mock_load):
        mock_load.return_value = self.default_config
        capi = ConfigurationAPI(ConfigurationManager())

        capi.load_printer()

        mock_load.assert_called_with()

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_get_current_config_loads(self, mock_save, mock_load):
        mock_load.return_value = self.default_config
        capi1 = ConfigurationAPI(ConfigurationManager())

        capi1.get_current_config()

        mock_load.assert_called_with()

    @patch.object(ConfigurationManager, 'reset')
    def test_reset_printer_calls_reset(self, mock_reset):
        mock_reset.return_value = self.default_config
        capi = ConfigurationAPI(ConfigurationManager())

        capi.reset_printer()

        mock_reset.assert_called_with()

if __name__ == '__main__':
    unittest.main()
