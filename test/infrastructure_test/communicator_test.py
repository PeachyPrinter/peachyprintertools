import unittest
import sys
import os
import time
from mock import patch
import serial

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

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

    def test_register_handler_should_raise_exception_for_none_message_type(self, mock_serial):
        port, header, footer, escape = "na", '@', 'A', 'B'
        self.comm = SerialCommunicator(port, header, footer, escape)
        def handler(message):
            pass
        with self.assertRaises(Exception):
            self.comm.register_handler("ASD", handler)

    def test_register_handler_should_for_message_type(self, mock_serial):
        port, header, footer, escape = "na", '@', 'A', 'B'
        self.comm = SerialCommunicator(port, header, footer, escape)
        def handler(message):
            pass
        self.comm.register_handler(DripRecordedMessage, handler)

    def test_recieving_message_for_which_thier_is_a_handler(self, mock_serial):
        port, header, footer, escape = "na", '@', 'A', 'B'
        original_message = DripRecordedMessage(66)
        message_bytes = original_message.get_bytes()
        message_id = chr(original_message.TYPE_ID)
        payload = message_id + message_bytes
        escaped = ''
        for ch in payload:
            if ch in [header, footer, escape]:
                escaped += escape
                escaped += '%c' % ((~ord(ch) & 0xFF),)
            else:
                escaped += ch

        expected_data = list(header + escaped + footer)

        self.comm = SerialCommunicator(port, header, footer, escape)
        self.recieved = False

        def side_effect():
            if expected_data:
                return [expected_data.pop(0)]
            else:
                raise serial.SerialTimeoutException()

        def handler(message):
            self.recieved = message

        self.comm.register_handler(DripRecordedMessage, handler)
        mock_serial.Serial.return_value.read.side_effect = side_effect
        mock_serial.SerialTimeoutException = serial.SerialTimeoutException
        self.comm.start()
        time.sleep(0.1)
        self.comm.close()

        self.assertEquals(original_message, self.recieved)

    def test_recieving_message_for_which_thier_are_2_handlers(self, mock_serial):
        port, header, footer, escape = "na", '@', 'A', 'B'
        original_message = DripRecordedMessage(45)
        message_bytes = original_message.get_bytes()
        message_id = chr(original_message.TYPE_ID)
        expected_data = list(header + message_id + message_bytes + footer)

        self.comm = SerialCommunicator(port, header, footer, escape)
        recieved = []

        def side_effect():
            if expected_data:
                return expected_data.pop(0)
            else:
                raise serial.SerialTimeoutException()

        def handler1(message):
            recieved.append(message)
        def handler2(message):
            recieved.append(message)

        self.comm.register_handler(DripRecordedMessage, handler1)
        self.comm.register_handler(DripRecordedMessage, handler2)
        mock_serial.Serial.return_value.read.side_effect = side_effect
        mock_serial.SerialTimeoutException = serial.SerialTimeoutException
        self.comm.start()
        time.sleep(0.1)
        self.comm.close()

        self.assertEquals(original_message, recieved[0])
        self.assertEquals(original_message, recieved[1])

    def test_recieving_message_for_which_thier_are_no_handlers(self, mock_serial):
        port, header, footer, escape = "na", '@', 'A', 'B'
        original_message = DripRecordedMessage(45)
        message_bytes = original_message.get_bytes()
        message_id = chr(original_message.TYPE_ID)
        expected_data = list(header + message_id + message_bytes + footer)

        self.comm = SerialCommunicator(port, header, footer, escape)

        def side_effect():
            if expected_data:
                return expected_data.pop(0)
            else:
                raise serial.SerialTimeoutException()

        mock_serial.Serial.return_value.read.side_effect = side_effect
        mock_serial.SerialTimeoutException = serial.SerialTimeoutException
        self.comm.start()
        time.sleep(0.1)
        self.comm.close()


if __name__ == '__main__':
    unittest.main()
