import unittest
from api.drip_calibration import DripCalibration
from infrastructure.drip_based_zaxis import DripBasedZAxis

class DripCalibrationApiTests(unittest.TestCase):
    
    def test_drip_calibration_requires_a_drip_based_zaxis(self):
        passed = False
        try:
            DripCalibration()
        except:
            passed = True
        self.assertTrue(passed)