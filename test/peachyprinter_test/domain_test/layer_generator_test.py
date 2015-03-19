import unittest
from peachyprinter.domain.layer_generator import TestLayerGenerator


class TestLayerGeneratorTests(unittest.TestCase):
    def test_set_speed_accepts_positive_numbers_only(self):
        layer_generator = TestLayerGenerator()
        with self.assertRaises(AttributeError):
            layer_generator.set_speed('a')
        with self.assertRaises(AttributeError):
            layer_generator.set_speed(-1)
        with self.assertRaises(AttributeError):
            layer_generator.set_speed(0)
        layer_generator.set_speed(1)

    def test_set_radius_accepts_positive_numbers_only(self):
        layer_generator = TestLayerGenerator()
        with self.assertRaises(AttributeError):
            layer_generator.set_radius('a')
        with self.assertRaises(AttributeError):
            layer_generator.set_radius(-1)
        with self.assertRaises(AttributeError):
            layer_generator.set_radius(0)
        layer_generator.set_radius(1)