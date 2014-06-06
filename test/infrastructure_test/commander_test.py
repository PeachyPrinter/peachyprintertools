import unittest
import sys
import os
from mock import patch, Mock
import time

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from infrastructure.commander import NullCommander, SerialCommander

class NullCommanderTests(unittest.TestCase):
    def test_sending_command_does_nothing(self):
        null_commander = NullCommander()
        null_commander.send_command("Explode")

@patch('infrastructure.commander.serial.Serial')
class SerialCommanderTests(unittest.TestCase):
    def test_sending_command_writes_to_serial(self, mock_Serial):
        expected_port = "COM1"
        expected_baud = 9600
        expected_message = 'Hi'
        mock_serial = mock_Serial.return_value

        serial_commander = SerialCommander(expected_port,expected_baud)
        serial_commander.send_command(expected_message)

        mock_Serial.assert_called_with(expected_port,expected_baud)
        mock_serial.write.assert_called_with(expected_message)

if __name__ == '__main__':
    unittest.main()
