import unittest
import os
import sys
from mock import patch
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from peachyprinter.api.firmware_api import FirmwareAPI

@patch('peachyprinter.api.firmware_api.glob')
class FirmwareAPITests(unittest.TestCase):

    def test_is_firmware_valid_raises_exception_if_no_firmware_file_present(self, mock_glob):
        mock_glob.return_value = []
        fwapi = FirmwareAPI()

        with self.assertRaises(Exception) as context:
            fwapi.is_firmware_valid('1.0.0')

        self.assertEquals("Package missing required firmware", context.exception.message)

    def test_is_firmware_valid_raises_exception_if_multipule_firmware_files_present(self, mock_glob):
        mock_glob.return_value = ['peachyprinter-firmware-1.0.0.bin', 'peachyprinter-firmware-1.0.1.bin']
        fwapi = FirmwareAPI()

        with self.assertRaises(Exception) as context:
            fwapi.is_firmware_valid('1.0.0')

        self.assertEquals("Unexpected firmware files", context.exception.message)

    def test_is_firmware_valid_returns_true_if_file_matches_version(self, mock_glob):
        mock_glob.return_value = ['peachyprinter-firmware-1.0.0.bin']
        expected_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src', 'peachyprinter', 'dependancies', 'firmware'))
        fwapi = FirmwareAPI()

        result = fwapi.is_firmware_valid('1.0.0')

        mock_glob.assert_called_with(os.path.join(expected_path, "peachyprinter-firmware-*.bin"))
        self.assertTrue(result)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()
