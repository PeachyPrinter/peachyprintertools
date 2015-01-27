import unittest
import sys
import os
from mock import MagicMock, call, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from test_helpers import TestHelpers
from infrastructure.communicator import SerialCommunicator

@patch('infrastructure.communicator.serial')
class SerialCommunicatorTests(unittest.TestCase):
    def test_send_raises_excpetion_when_no_connection(self, mock_serial):
        pass


if __name__ == '__main__':
    unittest.main()
