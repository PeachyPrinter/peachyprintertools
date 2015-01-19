import unittest
import numpy
import math
import sys
import os
from mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from test_helpers import TestHelpers
from infrastructure.micro_disseminator import MicroDisseminator
from domain.laser_control import LaserControl

class MicroDisseminatorTests(unittest.TestCase, TestHelpers):
    def test_samples_per_second_is_data_rate(self):
        expected_samples_per_second = 8000
        micro_disseminator = MicroDisseminator(LaserControl(), MagicMock(), expected_samples_per_second)
        self.assertEquals(expected_samples_per_second, micro_disseminator.samples_per_second)

    def test_next_layer_does_nothing(self):
        micro_disseminator = MicroDisseminator(LaserControl(), MagicMock(), 8000)
        micro_disseminator.next_layer(7.7)

    def test_process_should_call_communicator_with_correct_command(self):
        pass


if __name__ == '__main__':
    unittest.main()