import unittest
from api.drip_calibration import DripCalibrationAPI
from infrastructure.drip_based_zaxis import DripBasedZAxis

from mock import patch

class DripCalibrationAPITests(unittest.TestCase):
    
    @patch('infrastructure.drip_based_zaxis.DripBasedZAxis')
    def test_drip_calibration_requires_a_drip_based_zaxis(self, mock_DripBasedZAxis):
        passed = False
        try:
            DripCalibrationAPI()
        except:
            passed = True
        self.assertTrue(passed)

    @patch('infrastructure.drip_based_zaxis.DripBasedZAxis')
    def test_drip_calibration_should_be_able_to_get_drips(self, mock_DripBasedZAxis):
        fake_drip_counter = 77
        mock_zaxis = mock_DripBasedZAxis.retutn_value
        drip_calibration_api = DripCalibrationAPI(mock_zaxis)
        mock_zaxis.current_z_location_mm.return_value = fake_drip_counter

        result = drip_calibration_api.get_drips()

        self.assertEquals(fake_drip_counter, result)

    @patch('infrastructure.drip_based_zaxis.DripBasedZAxis')
    def test_drip_calibration_should_call_reset_when_reset_requested(self, mock_DripBasedZAxis):
        mock_zaxis = mock_DripBasedZAxis.retutn_value
        drip_calibration_api = DripCalibrationAPI(mock_zaxis)

        drip_calibration_api.reset_drips()

        self.assertEquals(mock_zaxis.reset.call_count, 1)
        

    @patch('infrastructure.drip_based_zaxis.DripBasedZAxis')
    def test_drip_calibration_should_be_able_to_set_target_height_if_float(self, mock_DripBasedZAxis):
        mock_zaxis = mock_DripBasedZAxis.retutn_value
        drip_calibration_api = DripCalibrationAPI(mock_zaxis)

        drip_calibration_api.set_target_height(10.0)

    @patch('infrastructure.drip_based_zaxis.DripBasedZAxis')
    def test_drip_calibration_should_be_able_to_set_target_height_if_int(self, mock_DripBasedZAxis):
        mock_zaxis = mock_DripBasedZAxis.retutn_value
        drip_calibration_api = DripCalibrationAPI(mock_zaxis)

        drip_calibration_api.set_target_height(10)

    @patch('infrastructure.drip_based_zaxis.DripBasedZAxis')
    def test_drip_calibration_target_height_must_be_greater_than_0(self, mock_DripBasedZAxis):
        mock_zaxis = mock_DripBasedZAxis.retutn_value
        drip_calibration_api = DripCalibrationAPI(mock_zaxis)
        passed = False
        try:
            drip_calibration_api.set_target_height(0.0)
            passed = False
        except: 
            passed = True
        self.assertTrue(passed)

    @patch('infrastructure.drip_based_zaxis.DripBasedZAxis')
    def test_drip_calibration_target_height_must_be_numeric(self, mock_DripBasedZAxis):
        mock_zaxis = mock_DripBasedZAxis.retutn_value
        drip_calibration_api = DripCalibrationAPI(mock_zaxis)
        passed = False
        try:
            drip_calibration_api.set_target_height('a')
            passed = False
        except: 
            passed = True
        self.assertTrue(passed)

    @patch('infrastructure.drip_based_zaxis.DripBasedZAxis')
    def test_drip_calibration_should_not_be_able_to_mark_when_target_not_specified(self, mock_DripBasedZAxis):
        mock_zaxis = mock_DripBasedZAxis.retutn_value
        drip_calibration_api = DripCalibrationAPI(mock_zaxis)
        passed = False

        try:
            drip_calibration_api.mark_drips_at_target()
            passed = False
        except Exception as ex:
            passed = True

        self.assertTrue(passed)

    @patch('infrastructure.drip_based_zaxis.DripBasedZAxis')
    def test_drip_calibration_should_be_able_to_mark_when_target_specified(self, mock_DripBasedZAxis):
        fake_drip_counter = 70
        target_height = 10.0
        expected_drips_per_mm = fake_drip_counter / target_height
        mock_zaxis = mock_DripBasedZAxis.retutn_value
        drip_calibration_api = DripCalibrationAPI(mock_zaxis)
        mock_zaxis.current_z_location_mm.return_value = fake_drip_counter
        drip_calibration_api.set_target_height(target_height)

        drip_calibration_api.mark_drips_at_target()

        self.assertEquals(expected_drips_per_mm, drip_calibration_api.get_drips_per_mm())


