import unittest
import sys
import os
from mock import patch, Mock
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from peachyprinter.infrastructure.commander import NullCommander, SerialCommander

class NullCommanderTests(unittest.TestCase):
    def test_sending_command_does_nothing(self):
        null_commander = NullCommander()
        null_commander.send_command("Explode")

@patch('infrastructure.commander.serial.Serial')
class SerialCommanderTests(unittest.TestCase):

    def test_waits_for_ok_on_init(self, mock_Serial):
        expected_port = "COM1"
        expected_baud = 19200
        expected_message = 'D'
        mock_serial = mock_Serial.return_value
        mock_serial.readline.return_value = "OK\n"

        SerialCommander(expected_port,expected_baud)

        mock_Serial.assert_called_with(expected_port,expected_baud,timeout = 1, writeTimeout = 1, interCharTimeout=1 )
        mock_serial.write.assert_called_with(expected_message)

    def test_rasies_Exceptions_if_no_ok_on_init(self, mock_Serial):
        expected_port = "COM1"
        expected_baud = 19200
        expected_message = 'D'
        mock_serial = mock_Serial.return_value
        mock_serial.readline.return_value = "ERR\n"

        with self.assertRaises(Exception):
            SerialCommander(expected_port,expected_baud, connection_timeout = 0.1)

        mock_Serial.assert_called_with(expected_port,expected_baud,timeout = 1, writeTimeout = 1, interCharTimeout=1)
        mock_serial.write.assert_called_with(expected_message)
    
    def test_sending_command_writes_to_serial(self, mock_Serial):
        expected_port = "COM1"
        expected_baud = 9600
        expected_message = 'Hi'
        mock_serial = mock_Serial.return_value
        mock_serial.readline.return_value = 'OK\n'

        serial_commander = SerialCommander(expected_port,expected_baud)
        serial_commander.send_command(expected_message)

        mock_Serial.assert_called_with(expected_port,expected_baud,timeout = 1, writeTimeout = 1, interCharTimeout=1)
        self.assertEquals(expected_message, mock_serial.write.mock_calls[1][1][0].rstrip())

if __name__ == '__main__':
    unittest.main()
