import unittest
import os
import sys
from mock import patch, MagicMock
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

import peachyprinter.api.firmware_api as firmware_api
from peachyprinter.api.firmware_api import FirmwareAPI


@patch('peachyprinter.api.firmware_api.firmware')
@patch('peachyprinter.api.firmware_api.glob')
class FirmwareAPITests(unittest.TestCase):

    def _setup_mock(self, mock_firmware):
        self.mock_firmware_updater = MagicMock()
        mock_firmware.get_firmware_updater.return_value = self.mock_firmware_updater

    def test_is_firmware_valid_raises_exception_if_no_firmware_file_present(self, mock_glob, mock_firmware):
        self._setup_mock(mock_firmware)
        mock_glob.return_value = []
        fwapi = FirmwareAPI()

        with self.assertRaises(Exception) as context:
            fwapi.is_firmware_valid('1.0.0')

        self.assertEquals("Package missing required firmware", context.exception.message)

    def test_is_firmware_valid_raises_exception_if_multipule_firmware_files_present(self, mock_glob, mock_firmware):
        mock_glob.return_value = ['peachyprinter-firmware-1.0.0.bin', 'peachyprinter-firmware-1.0.1.bin']
        fwapi = FirmwareAPI()

        with self.assertRaises(Exception) as context:
            fwapi.is_firmware_valid('1.0.0')

        self.assertEquals("Unexpected firmware files", context.exception.message)

    def test_is_firmware_valid_returns_true_if_file_matches_version(self, mock_glob, mock_firmware):
        self._setup_mock(mock_firmware)
        mock_glob.return_value = ['peachyprinter-firmware-1.0.0.bin']
        expected_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src', 'peachyprinter', 'dependancies', 'firmware'))
        fwapi = FirmwareAPI()

        result = fwapi.is_firmware_valid('1.0.0')

        mock_glob.assert_called_with(os.path.join(expected_path, "peachyprinter-firmware-*.bin"))
        self.assertTrue(result)

    def test_is_ready_returns_false_when_firmware_api_returns_true(self, mock_glob, mock_firmware):
        self._setup_mock(mock_firmware)
        self.mock_firmware_updater.check_ready.return_value = True

        fwapi = FirmwareAPI()
        self.assertTrue(fwapi.is_ready())

    def test_is_ready_returns_false_when_firmware_api_returns_false(self, mock_glob, mock_firmware):
        self._setup_mock(mock_firmware)
        self.mock_firmware_updater.check_ready.return_value = False

        fwapi = FirmwareAPI()
        self.assertFalse(fwapi.is_ready())

    def test_init_should_be_called_with_logger(self, mock_glob, mock_firmware):
        self._setup_mock(mock_firmware)

        FirmwareAPI()
        mock_firmware.get_firmware_updater.assert_called_with(firmware_api.logger)



if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()
