import unittest
from domain.laser_control import LaserControl

class LaserControlTest(unittest.TestCase):
    
    def test_default_state_is_off(self):
        l = LaserControl()
        self.assertFalse(l.laser_is_on())

    def test_turn_laser_on_shows_laser_on(self):
        l = LaserControl()
        l.set_laser_on()
        self.assertTrue(l.laser_is_on())

    def test_turn_laser_off_shows_laser_off(self):
        l = LaserControl()
        l.set_laser_on()
        self.assertTrue(l.laser_is_on())
        l.set_laser_off()
        self.assertFalse(l.laser_is_on())
