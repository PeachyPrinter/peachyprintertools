import unittest
import os
import sys
from mock import patch, MagicMock
import logging
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

import peachyprinter.api.firmware_api as firmware_api
from peachyprinter.api.firmware_api import FirmwareAPI, FirmwareUpdate
from peachyprinter.infrastructure.messages import EnterBootloaderMessage


@patch('peachyprinter.api.firmware_api.FirmwareUpdate')
@patch('peachyprinter.api.firmware_api.firmware_manager_factory')
@patch('peachyprinter.api.firmware_api.glob')
class FirmwareAPITests(unittest.TestCase):

    def _setup_mock(self, mock_firmware_manager_factory, mock_glob, firmware_version='1.0.0'):
        self.mock_firmware_updater = MagicMock()
        self.expected_firmware_file = 'peachyprinter-firmware-{}.bin'.format(firmware_version)
        mock_firmware_manager_factory.get_firmware_updater.return_value = self.mock_firmware_updater
        self.mock_firmware_updater.check_ready.return_value = True
        mock_glob.return_value = [self.expected_firmware_file]

    def test_is_firmware_valid_raises_exception_if_no_firmware_file_present(self, mock_glob, mock_firmware_manager_factory, mock_FirmwareUpdate):
        self._setup_mock(mock_firmware_manager_factory, mock_glob)
        mock_glob.return_value = []

        with self.assertRaises(Exception) as context:
            fwapi = FirmwareAPI()
            fwapi.is_firmware_valid('1.0.0')

        self.assertEquals("Package missing required firmware", context.exception.message)

    def test_is_firmware_valid_raises_exception_if_multipule_firmware_files_present(self, mock_glob, mock_firmware_manager_factory, mock_FirmwareUpdate):
        mock_glob.return_value = ['peachyprinter-firmware-1.0.0.bin', 'peachyprinter-firmware-1.0.1.bin']

        with self.assertRaises(Exception) as context:
            fwapi = FirmwareAPI()
            fwapi.is_firmware_valid('1.0.0')

        self.assertEquals("Unexpected firmware files", context.exception.message)

    def test_is_firmware_valid_returns_true_if_file_matches_version(self, mock_glob, mock_firmware_manager_factory, mock_FirmwareUpdate):
        self._setup_mock(mock_firmware_manager_factory, mock_glob)
        mock_glob.return_value = ['peachyprinter-firmware-1.0.0.bin']
        expected_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src', 'peachyprinter', 'dependancies', 'firmware'))
        fwapi = FirmwareAPI()

        result = fwapi.is_firmware_valid('1.0.0')

        mock_glob.assert_called_with(os.path.join(expected_path, "peachyprinter-firmware-*.bin"))
        self.assertTrue(result)

    def test_is_ready_returns_false_when_firmware_api_returns_true(self, mock_glob, mock_firmware_manager_factory, mock_FirmwareUpdate):
        self._setup_mock(mock_firmware_manager_factory, mock_glob)
        self.mock_firmware_updater.check_ready.return_value = True

        fwapi = FirmwareAPI()
        self.assertTrue(fwapi.is_ready())

    def test_is_ready_returns_false_when_firmware_api_returns_false(self, mock_glob, mock_firmware_manager_factory, mock_FirmwareUpdate):
        self._setup_mock(mock_firmware_manager_factory, mock_glob)
        self.mock_firmware_updater.check_ready.return_value = False

        fwapi = FirmwareAPI()
        self.assertFalse(fwapi.is_ready())

    def test_init_should_be_called_with_logger(self, mock_glob, mock_firmware_manager_factory, mock_FirmwareUpdate):
        self._setup_mock(mock_firmware_manager_factory, mock_glob)

        FirmwareAPI()
        mock_firmware_manager_factory.get_firmware_updater.assert_called_with(firmware_api.logger)

    def test_required_version_gets_version_from_bin(self, mock_glob, mock_firmware_manager_factory, mock_FirmwareUpdate):
        expected_verison = "1.8.2"
        self._setup_mock(mock_firmware_manager_factory, mock_glob, firmware_version=expected_verison)
        fwapi = FirmwareAPI()

        self.assertEquals(expected_verison, fwapi.required_version)

    def test_make_ready_should_create_a_communicator_and_send_the_correct_message(self, mock_glob, mock_firmware_manager_factory, mock_FirmwareUpdate):
        mock_firmware_update = mock_FirmwareUpdate.return_value
        self._setup_mock(mock_firmware_manager_factory, mock_glob)

        fwapi = FirmwareAPI()
        fwapi.make_ready()

        mock_firmware_update.prepare.assert_called_with()
        mock_FirmwareUpdate.assert_called_with(self.expected_firmware_file, self.mock_firmware_updater)

    def test_firmware_update_should_raise_exception_if_not_ready(self, mock_glob, mock_firmware_manager_factory, mock_FirmwareUpdate):
        self._setup_mock(mock_firmware_manager_factory, mock_glob)
        self.mock_firmware_updater.check_ready.return_value = False

        fwapi = FirmwareAPI()

        with self.assertRaises(Exception) as context:
            fwapi.update_firmware()

        self.assertEquals("Peachy Printer not ready for update", context.exception.message)

    def test_firmware_update_should_create_and_run_firmware_update(self, mock_glob, mock_firmware_manager_factory, mock_FirmwareUpdate):
        mock_firmware_update = mock_FirmwareUpdate.return_value
        self._setup_mock(mock_firmware_manager_factory, mock_glob)
        expected_call_back = "Boop"

        fwapi = FirmwareAPI()
        fwapi.update_firmware(expected_call_back)

        mock_FirmwareUpdate.assert_called_with(self.expected_firmware_file, self.mock_firmware_updater)
        mock_firmware_update.start.assert_called_with(expected_call_back)


class FirmwareUpdateTests(unittest.TestCase):
    wait_time = 0.2

    def test_start_should_call_firmware_updater_and_then_call_back_with_true(self):
        mock_updater = MagicMock()
        mock_updater.update.return_value = True
        call_back = MagicMock()
        expected_file = "A bin file"

        firmware_update = FirmwareUpdate(expected_file, mock_updater)
        firmware_update.start(call_back)

        time.sleep(self.wait_time)

        mock_updater.update.assert_called_with(expected_file)
        call_back.assert_called_with(True)

    def test_start_should_call_firmware_updater_and_then_call_back_with_false(self):
        mock_updater = MagicMock()
        mock_updater.update.return_value = False
        call_back = MagicMock()
        expected_file = "A bin file"

        firmware_update = FirmwareUpdate(expected_file, mock_updater)
        firmware_update.start(call_back)

        time.sleep(self.wait_time)

        mock_updater.update.assert_called_with(expected_file)
        call_back.assert_called_with(False)

    @patch('peachyprinter.api.firmware_api.UsbPacketCommunicator')
    def test_prepare_creates_a_usb_communicator_and_sends_enter_bootloader(self, mock_UsbPacketCommunicator):
        mock_updater = MagicMock()
        mock_usb_packet_communicator = mock_UsbPacketCommunicator.return_value

        fw_update = FirmwareUpdate('afile', mock_updater)
        fw_update.prepare()

        mock_usb_packet_communicator.start.assert_called_with()
        mock_usb_packet_communicator.send.assert_called_with(EnterBootloaderMessage())
        mock_usb_packet_communicator.close.assert_called_with()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()
