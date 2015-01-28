import unittest
import sys
import os
import time
from mock import MagicMock, call, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from test_helpers import TestHelpers
from infrastructure.communicator import SerialCommunicator
from infrastructure.messages import DripRecordedMessage

@patch('infrastructure.communicator.serial')
class SerialCommunicatorTests(unittest.TestCase):
    def setUp(self):
        self.comm = None

    def tearDown(self):
        if self.comm:
            if self.comm.is_alive():
                print("#" * 40)
                print("Class was not shutdown. Forcing shutdown.")
                print("#" * 40)
                self.comm.close()

    def test_start_close_start_and_stop(self, mock_serial):
        self.comm = SerialCommunicator("na", '@', 'A', 'B')
        self.comm.start()
        time.sleep(0.1)
        self.comm.close()
        self.assertFalse(self.comm.is_alive())

    def test_start_should_create_a_connection(self, mock_serial):
        port, header, footer, escape = "na", '@', 'A', 'B'
        self.comm = SerialCommunicator(port, header, footer, escape)

        self.comm.start()
        time.sleep(0.1)
        self.comm.close()

        mock_serial.Serial.assert_called_with(port)
        mock_serial.Serial.return_value.close.assert_called_with()

    def test_send_rasies_exception_if_serial_connection_is_not_established(self, mock_serial):
        self.comm = SerialCommunicator("na", '@', 'A', 'B')
        with self.assertRaises(Exception):
            self.comm.send(DripRecordedMessage(45))

    def test_send_rasies_exception_if_serial_connection_shutdown(self, mock_serial):
        self.comm = SerialCommunicator("na", '@', 'A', 'B')

        self.comm.start()
        time.sleep(0.1)
        self.comm.close()

        with self.assertRaises(Exception):
            self.comm.send(DripRecordedMessage(45))

    def test_send_encoded_an_message_with_header_id_payload_and_footer(self, mock_serial):
        port, header, footer, escape = "na", '@', 'A', 'B'
        self.comm = SerialCommunicator(port, header, footer, escape)
        self.comm.start()

        message = DripRecordedMessage(45)
        message_bytes = message.get_bytes()
        message_id = chr(message.TYPE_ID)
        expected_data = header + message_id + message_bytes + footer

        self.comm.send(message)

        self.comm.close()
        mock_serial.Serial.return_value.write.assert_called_with(expected_data)

    def test_send_should_escape_message(self, mock_serial):
        port, header, footer, escape = "na", '@', 'A', 'B'
        self.comm = SerialCommunicator(port, header, footer, escape)
        self.comm.start()

        message = DripRecordedMessage(66)
        message_bytes = message.get_bytes()
        message_id = chr(message.TYPE_ID)
        expected_data = header + message_id + message_bytes + chr(189) + footer

        self.comm.send(message)

        self.comm.close()
        mock_serial.Serial.return_value.write.assert_called_with(expected_data)


if __name__ == '__main__':
    unittest.main()
