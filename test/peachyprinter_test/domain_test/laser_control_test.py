import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from peachyprinter.domain.laser_control import LaserControl


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

    def test_laser_power_shows_0_when_laser_off(self):
        l = LaserControl()
        l.set_laser_off()
        self.assertEquals(0.0, l.laser_power())

    def test_laser_power_shows_1_when_laser_on(self):
        l = LaserControl()
        l.set_laser_on()
        self.assertEquals(1.0, l.laser_power())

    def test_laser_power_shows_default_when_provided(self):
        expected_laser_power = 0.6
        l = LaserControl(expected_laser_power)
        l.set_laser_on()
        self.assertEquals(expected_laser_power, l.laser_power())

    def test_laser_power_throws_if_outside_range(self):
        with self.assertRaises(Exception):
            LaserControl(1.001)
        with self.assertRaises(Exception):
            LaserControl(-0.001)

if __name__ == '__main__':
    unittest.main()
