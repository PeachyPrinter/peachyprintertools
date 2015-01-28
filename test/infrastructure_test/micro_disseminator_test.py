import unittest
import numpy
import math
import sys
import os
from mock import MagicMock, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from test_helpers import TestHelpers
from infrastructure.micro_disseminator import MicroDisseminator
from domain.laser_control import LaserControl
from infrastructure.messages import MoveMessage


class MicroDisseminatorTests(unittest.TestCase, TestHelpers):
    def setUp(self):
        self.mock_comm = MagicMock()
        self.laser_control = LaserControl()

    def test_samples_per_second_is_data_rate(self):
        expected_samples_per_second = 8000
        micro_disseminator = MicroDisseminator(LaserControl(), MagicMock(), expected_samples_per_second)
        self.assertEquals(expected_samples_per_second, micro_disseminator.samples_per_second)

    def test_next_layer_does_nothing(self):
        micro_disseminator = MicroDisseminator(LaserControl(), MagicMock(), 8000)
        micro_disseminator.next_layer(7.7)

    def test_process_should_call_com_with_move_when_laser_off(self):
        self.laser_control.set_laser_off()
        sample_data_chunk = numpy.array([(0, 0)])
        micro_disseminator = MicroDisseminator(self.laser_control, self.mock_comm, 8000)
        micro_disseminator.process(sample_data_chunk)
        self.mock_comm.send.assert_called_with(MoveMessage(0, 0, 0))

    def test_process_should_call_com_with_move_when_laser_on(self):
        self.laser_control.set_laser_on()
        sample_data_chunk = numpy.array([(0, 0)])
        micro_disseminator = MicroDisseminator(self.laser_control, self.mock_comm, 8000)
        micro_disseminator.process(sample_data_chunk)
        self.mock_comm.send.assert_called_with(MoveMessage(0, 0, 255))

    def test_process_should_adjust_laser_power(self):
        self.laser_control = LaserControl(0.5)
        self.laser_control.set_laser_on()
        sample_data_chunk = numpy.array([(0, 0)])
        micro_disseminator = MicroDisseminator(self.laser_control, self.mock_comm, 8000)
        micro_disseminator.process(sample_data_chunk)
        self.mock_comm.send.assert_called_with(MoveMessage(0, 0, 127))

    def test_process_should_call_com_with_correct_posisitions(self):
        self.laser_control.set_laser_on()
        sample_data_chunk = numpy.array([(1, 1)])
        micro_disseminator = MicroDisseminator(self.laser_control, self.mock_comm, 8000)
        micro_disseminator.process(sample_data_chunk)
        self.mock_comm.send.assert_called_with(MoveMessage(65535, 65535, 255))

    def test_process_should_handle_empty_lists(self):
        self.laser_control.set_laser_on()
        sample_data_chunk = numpy.array([])
        micro_disseminator = MicroDisseminator(self.laser_control, self.mock_comm, 8000)
        micro_disseminator.process(sample_data_chunk)
        self.assertEqual(0, self.mock_comm.send.call_count)

    def test_process_should_call_com_each_element_in_list(self):
        self.laser_control.set_laser_on()
        sample_data_chunk = numpy.array([(0.0, 1.0), (0.5, 0.0), (1.0, 0.5)])
        micro_disseminator = MicroDisseminator(self.laser_control, self.mock_comm, 8000)
        micro_disseminator.process(sample_data_chunk)
        self.mock_comm.send.assert_has_calls([
            call(MoveMessage(0,     65535, 255)),
            call(MoveMessage(32767, 0,     255)),
            call(MoveMessage(65535, 32767, 255)),
            ])

    def test_close_calls_close_on_communicator(self):
        micro_disseminator = MicroDisseminator(self.laser_control, self.mock_comm, 8000)
        micro_disseminator.close()
        self.mock_comm.close.assert_called_with()


if __name__ == '__main__':
    unittest.main()
