import unittest
import os
import sys

from mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from api.test_print_api import TestPrintAPI
from infrastructure.print_test_layer_generators import *
import test_helpers


class TestPrintAPITests(unittest.TestCase, test_helpers.TestHelpers):

    def test_test_print_names_should_return_names(self):
        tpa = TestPrintAPI()
        expected_key = "Half Vase With A Twist"

        results = tpa.test_print_names()

        self.assertTrue(expected_key in results)


    def test_test_print_names_should_not_include_super_return_names(self):
        tpa = TestPrintAPI()
        bad_key = "I have no name"

        results = tpa.test_print_names()

        self.assertFalse(bad_key in results)

    def test_get_test_print_should_return_at_least_expected_classes(self):
        tpa = TestPrintAPI()
        name = "Half Vase With A Twist"
        height = 10
        width = 10
        layer_height = 0.1
        speed = 99

        result = tpa.get_test_print(name, height, width, layer_height, speed)

        self.assertEqual(type(result), HalfVaseTestGenerator)
        self.assertEqual(height, result._height)
        self.assertEqual(width / 2.0, result._max_radius)
        self.assertEqual(layer_height, result._layer_height)
        self.assertEqual(speed, result._speed)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()
