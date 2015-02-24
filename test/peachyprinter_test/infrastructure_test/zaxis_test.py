import unittest
import os
import sys
import time
import logging
from mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from peachyprinter.infrastructure.zaxis import SerialDripZAxis
from peachyprinter.infrastructure.messages import DripRecordedMessage, SetDripCountMessage, MoveToDripCountMessage


class SerialDripZAxisTests(unittest.TestCase):

    def test_init_calls_registers_handler(self):
        mock_communicatior = MagicMock()
        sdza = SerialDripZAxis(mock_communicatior, 1.0, 0.0)
        mock_communicatior.register_handler.assert_called_with(DripRecordedMessage, sdza.drip_reported_handler)

    def test_init_sets_up_starting_height(self):
        mock_communicatior = MagicMock()
        starting_height = 10.0
        sdza = SerialDripZAxis(mock_communicatior, 1.0, starting_height)
        self.assertEqual(starting_height, sdza.current_z_location_mm())

    def test_init_resets_micro_drip_counter(self):
        mock_communicatior = MagicMock()
        starting_height = 10.0
        sdza = SerialDripZAxis(mock_communicatior, 1.0, starting_height)
        mock_communicatior.send.assert_called_with(SetDripCountMessage(0))

    def test_drip_recorded_handler_adds_drip(self):
        mock_communicatior = MagicMock()
        starting_height = 0.0
        drips_per_mm = 1.0
        sdza = SerialDripZAxis(mock_communicatior, drips_per_mm, starting_height)
        drip_message = DripRecordedMessage(1)

        sdza.drip_reported_handler(drip_message)

        self.assertEqual(1.0, sdza.current_z_location_mm())

    def test_drip_recorded_handler_adds_drips_if_missing_message(self):
        mock_communicatior = MagicMock()
        starting_height = 0.0
        drips_per_mm = 1.0
        sdza = SerialDripZAxis(mock_communicatior, drips_per_mm, starting_height)
        drip_message_1 = DripRecordedMessage(1)
        drip_message_2 = DripRecordedMessage(3)

        sdza.drip_reported_handler(drip_message_1)
        sdza.drip_reported_handler(drip_message_2)

        self.assertEqual(3.0, sdza.current_z_location_mm())

    def test_drip_recorded_handler_adds_correct_height_per_drip(self):
        mock_communicatior = MagicMock()
        starting_height = 0.0
        drips_per_mm = 2.5
        sdza = SerialDripZAxis(mock_communicatior, drips_per_mm, starting_height)
        drip_message = DripRecordedMessage(1)

        sdza.drip_reported_handler(drip_message)

        self.assertEqual(0.4, sdza.current_z_location_mm())

    def test_drip_recorded_handler_should_call_back_per_drip(self):
        mock_communicatior = MagicMock()
        starting_height = 0.0
        drips_per_mm = 1.0
        mock_call_back = MagicMock()
        expected_drips = 1
        expected_height = 1.0
        expected_average = 0.0

        sdza = SerialDripZAxis(mock_communicatior, drips_per_mm, starting_height, mock_call_back)
        drip_message = DripRecordedMessage(1)
        start = time.time()
        sdza.drip_reported_handler(drip_message)
        end = time.time()

        self.assertTrue(mock_call_back.called)
        self.assertEqual(expected_drips, mock_call_back.call_args_list[0][0][0])
        self.assertEqual(expected_height, mock_call_back.call_args_list[0][0][1])
        self.assertEqual(expected_average, mock_call_back.call_args_list[0][0][2])
        self.assertTrue(mock_call_back.call_args_list[0][0][3][0] >= start)
        self.assertTrue(mock_call_back.call_args_list[0][0][3][0] <= end)

    def test_drip_recorded_handler_should_adjust_history_for_missing_drips(self):
        mock_communicatior = MagicMock()
        starting_height = 0.0
        drips_per_mm = 1.0
        mock_call_back = MagicMock()

        sdza = SerialDripZAxis(mock_communicatior, drips_per_mm, starting_height, mock_call_back)
        drip_message_1 = DripRecordedMessage(1)
        drip_message_2 = DripRecordedMessage(10)

        sdza.drip_reported_handler(drip_message_1)
        sdza.drip_reported_handler(drip_message_2)
        self.assertEquals(10, len(mock_call_back.call_args_list[1][0][3]))

    def test_move_to_sends_drips(self):
        mock_communicatior = MagicMock()
        starting_height = 0.0
        drips_per_mm = 1.0
        mock_call_back = MagicMock()
        sdza = SerialDripZAxis(mock_communicatior, drips_per_mm, starting_height, mock_call_back)
        sdza.move_to(3.0)
        mock_communicatior.send.assert_called_with(MoveToDripCountMessage(3))

    def test_reset_removes_drips_count(self):
        mock_communicatior = MagicMock()
        starting_height = 0.0
        drips_per_mm = 2.5
        sdza = SerialDripZAxis(mock_communicatior, drips_per_mm, starting_height)
        drip_message = DripRecordedMessage(1)
        sdza.drip_reported_handler(drip_message)
        sdza.reset()
        actual_height = sdza.current_z_location_mm()

        self.assertEqual(0.0, actual_height)

    def test_reset_removes_drips_count_accounting_for_hardware(self):
        mock_communicatior = MagicMock()
        starting_height = 0.0
        drips_per_mm = 1.0
        sdza = SerialDripZAxis(mock_communicatior, drips_per_mm, starting_height)
        drip_message_1 = DripRecordedMessage(1)
        drip_message_2 = DripRecordedMessage(2)
        drip_message_3 = DripRecordedMessage(1)
        sdza.drip_reported_handler(drip_message_1)
        self.assertEqual(1.0, sdza.current_z_location_mm())
        sdza.drip_reported_handler(drip_message_2)
        self.assertEqual(2.0, sdza.current_z_location_mm())

        sdza.reset()
        self.assertEqual(0.0, sdza.current_z_location_mm())
        self.assertEqual(2, mock_communicatior.send.call_count)
        mock_communicatior.send.assert_called_with(SetDripCountMessage(0))

        sdza.drip_reported_handler(drip_message_3)
        self.assertEqual(1.0, sdza.current_z_location_mm())

    def test_set_call_back_should(self):
        mock_communicatior = MagicMock()
        starting_height = 0.0
        drips_per_mm = 1.0
        mock_call_back = MagicMock()
        expected_drips = 1
        expected_height = 1.0
        expected_average = 0.0

        sdza = SerialDripZAxis(mock_communicatior, drips_per_mm, starting_height, None)
        sdza.set_call_back(mock_call_back)
        drip_message = DripRecordedMessage(1)
        start = time.time()
        sdza.drip_reported_handler(drip_message)
        end = time.time()

        self.assertTrue(mock_call_back.called)
        self.assertEqual(expected_drips, mock_call_back.call_args_list[0][0][0])
        self.assertEqual(expected_height, mock_call_back.call_args_list[0][0][1])
        self.assertEqual(expected_average, mock_call_back.call_args_list[0][0][2])
        self.assertTrue(mock_call_back.call_args_list[0][0][3][0] >= start)
        self.assertTrue(mock_call_back.call_args_list[0][0][3][0] <= end)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()
