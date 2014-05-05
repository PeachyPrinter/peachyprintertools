import unittest
import sys
import os
from mock import patch, Mock
import time

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from test_helpers import TestHelpers

from infrastructure.zaxis_control import SerialZAxisControl


class SerialZAxisControlTests(unittest.TestCase):

    @patch('infrastructure.zaxis_control.serial.Serial')
    def test_init_opens_connection_on_port_specified(self, mock_Serial):
        port = "port"
        default_baud = 9600
        mock_serial = mock_Serial.return_value

        control = SerialZAxisControl(port)

        mock_Serial.assert_called_with(port, default_baud)
        self.assertTrue(mock_serial.open.called)

    @patch('infrastructure.zaxis_control.serial.Serial')
    def test_close_closes_connection(self, mock_Serial):
        port = "port"
        mock_serial = mock_Serial.return_value
        control = SerialZAxisControl(port)
        control.close()

        self.assertTrue(mock_serial.close.called)

    @patch('infrastructure.zaxis_control.serial.Serial')
    def test_move_up_writes_on_command(self, mock_Serial):
        on = 'on'
        mock_serial = mock_Serial.return_value
        control = SerialZAxisControl('port', on_command=on)
        control.move_up()

        mock_serial.write.assert_called_with('on')

    @patch('infrastructure.zaxis_control.serial.Serial')
    def test_move_up_writes_on_command_once_if_called_in_close_succession(self, mock_Serial):
        mock_serial = mock_Serial.return_value
        control = SerialZAxisControl('port')
        control.move_up()
        control.move_up()

        self.assertEquals(1,mock_serial.write.call_count)

    @patch('infrastructure.zaxis_control.serial.Serial')
    def test_move_up_writes_on_command_twice_if_called_after_repeat_delay(self, mock_Serial):
        mock_serial = mock_Serial.return_value
        control = SerialZAxisControl('port', repeat_delay_ms = 0.01)
        control.move_up()
        time.sleep(0.1)
        control.move_up()

        self.assertEquals(2,mock_serial.write.call_count)

    @patch('infrastructure.zaxis_control.serial.Serial')
    def test_stop_writes_off_command(self, mock_Serial):
        off = 'off'
        mock_serial = mock_Serial.return_value
        control = SerialZAxisControl('port', off_command=off)
        control.stop()

        mock_serial.write.assert_called_with('off')

    @patch('infrastructure.zaxis_control.serial.Serial')
    def test_stop_writes_on_command_once_if_called_in_close_succession(self, mock_Serial):
        mock_serial = mock_Serial.return_value
        control = SerialZAxisControl('port')
        control.stop()
        control.stop()

        self.assertEquals(1,mock_serial.write.call_count)

    @patch('infrastructure.zaxis_control.serial.Serial')
    def test_stop_writes_on_command_twice_if_called_after_repeat_delay(self, mock_Serial):
        mock_serial = mock_Serial.return_value
        control = SerialZAxisControl('port',  repeat_delay_ms = 0.01)
        control.stop()
        time.sleep(0.1)
        control.stop()

        self.assertEquals(2,mock_serial.write.call_count)

if __name__ == '__main__':
    unittest.main()
