import unittest
import sys
import os
from mock import patch
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from peachyprinter.infrastructure.communicator import UsbPacketCommunicator


#TODO this really needs to be actually tested

@patch('peachyprinter.infrastructure.communicator.PeachyUSB')
class UsbPacketCommunicatorTest(unittest.TestCase):


    def test_init_doesnt_raise_exception(self, mock_PeachyUSB):
        UsbPacketCommunicator(50)



if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()