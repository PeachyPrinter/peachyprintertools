import unittest
import os
import sys
from math import sqrt
import logging
from mock import patch, PropertyMock, call, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from peachyprinter.infrastructure.print_test_layer_generators import *
from peachyprinter.domain.commands import Layer


class SolidObjectTestGeneratorTest(unittest.TestCase):

    def dist(self, p1, p2):
        return sqrt(pow((p2[0] - p1[0]), 2) + pow((p2[1] - p1[1]), 2))

    def test_next_returns_expected_data(self):
        height = 100
        width = 100
        layer_height = 1
        speed = 100
        generator = SolidObjectTestGenerator(height, width, layer_height, speed)
        self.assertEquals(Layer, type(generator.next()))

    def test_next_should_have_object_end_in_peak(self):
        height = 100
        width = 100
        layer_height = 1
        speed = 100
        generator = SolidObjectTestGenerator(height, width, layer_height, speed)
        layer_distance = []

        data_layers = [cmd for cmd in generator]
        for layer in data_layers:
            points = []
            for cmd in layer.commands:
                points.append([cmd.end[0], cmd.end[1]])

            distances = []
            for point1 in points:
                for point2 in points:
                    if point1 != point2:
                        distances.append(self.dist(point2, point1))
            layer_distance.append(max(distances))
        self.assertTrue(layer_distance[-1] <= 1.0, '{} <= {}'.format(layer_distance[-1], 1.0))


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()