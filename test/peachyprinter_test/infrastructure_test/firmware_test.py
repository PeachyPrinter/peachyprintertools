import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from peachyprinter.infrastructure.firmware import FirmwareUpdate
from peachyprinter.infrastructure.messages import EnterBootloaderMessage
from mock import patch

class FirmwareUpdateTest(unittest.TestCase):

    @patch('peachyprinter.infrastructure.firmware.UsbPacketCommunicator')
    def test_start_creates_a_usb_communicator_and_sends_enter_bootloader(self, mock_UsbComms):
        #Setup
        usbcomms = mock_UsbComms.return_value

        #Test
        fw_update = FirmwareUpdate()
        fw_update.start_update()

        #Assert
        usbcomms.start.assert_called_with()
        usbcomms.send.assert_called_with(EnterBootloaderMessage())
        usbcomms.close.assert_called_with()


if __name__ == '__main__':
    unittest.main()
