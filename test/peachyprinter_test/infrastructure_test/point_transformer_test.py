import unittest
import os
import sys
import logging
import numpy as np
import math

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

import test_helpers
from peachyprinter.infrastructure.point_transformer import *
from peachyprinter.infrastructure.simulator import PeachyPrinterFactory

class PointTransformerTest(unittest.TestCase):
    factory = PeachyPrinterFactory()

    def get_test_points(self,size,z):
        for y in range(0,size):
            for x in range(0,size):
                dx = x * 1.0 / size * 1.0
                dy = y * 1.0 / size * 1.0
                yield [dx,dy ,z]

    def test_point_transformer_throws_exception_if_not_enough_points(self):
        x,y,z = 0.0,0.0,0.0
        x1,y1,z1 = 1.0,1.0,0.0
        points = [([x,y,z],[x1,y1,z1])]
        with self.assertRaises(Exception):
            pt = PointTransformer(points)

    def test_requires_11_points_mininmum(self):
        z_height = -300
        printer = self.factory.new_peachy_printer()
        deflection_points = [
            [ 1.0, 1.0],[-1.0, 1.0],[ 1.0,-1.0],[-1.0, -1.0],
            [ 0.0, 1.0 ],[ 0.0, -1.0 ],[1.0,0.0],[-1.0,0.0],
            [ 0.8, 0.8],[-0.8, 0.8]
        ]
        calibration_points = [ ((dx,dy),printer.write(dx,dy,z_height).tolist()[0][:2]) for (dx,dy) in deflection_points ]

        with self.assertRaises(Exception):
            PointTransformer(calibration_points)

    def test_perfect_printer_accuracy(self):
        acceptable_diffrence = 1.454
        z_height = -300

        printer = self.factory.new_peachy_printer()
        deflection_points = [
            [ 1.0, 1.0],[-1.0, 1.0],[ 1.0,-1.0],[-1.0, -1.0],
            [ 0.0, 1.0 ],[ 0.0, -1.0 ],[1.0,0.0],[-1.0,0.0],
            [ 0.8, 0.8],[-0.8, 0.8],[ 0.8,-0.8],[-0.8, -0.8],
            [ 0.0, 0.8],[ 0.0, -0.8 ],[0.8,0.0],[-0.8,0.0],
            [ 0.4, 0.4],[-0.4, 0.4],[ 0.4,-0.4],[-0.4, -0.4],
        ]
        calibration_points = [ ((dx,dy),printer.write(dx,dy,z_height).tolist()[0][:2]) for (dx,dy) in deflection_points ]

        pt = PointTransformer(calibration_points)

        difference = 0
        for (x,y,z) in self.get_test_points(10, z_height):
            expected_point = printer.write(x,y,z).tolist()[0][:3]
            actual_deflection = pt.transform(expected_point)
            actual_point = printer.write(actual_deflection[0],actual_deflection[1],actual_deflection[2]).tolist()[0][:3]
            difference += math.sqrt( (expected_point[0] - actual_point[0])**2 + (expected_point[1] - actual_point[1])**2 )

        average_diffrence = difference / 100.0
        print(average_diffrence)
        self.assertTrue(average_diffrence < acceptable_diffrence, 'Difference was %s' % average_diffrence)

class SquareTransformTest(unittest.TestCase):
    def test_requires_four_square_point_mappings(self):
        points = [
            ([ 1.0, 1.0],[ 10.0, 10.0]),
            ([ 1.0,-1.0],[ 10.0,-10.0]),
            ([-1.0,-1.0],[-10.0,-10.0]),
            ]
        with self.assertRaises(Exception):
            squarer = SquareTransform(points)

    def test_can_scale(self):
        configuration_points = [
            ([ 1.0, 1.0],[ 10.0, 10.0]),
            ([ 1.0,-1.0],[ 10.0,-10.0]),
            ([-1.0,-1.0],[-10.0,-10.0]),
            ([-1.0, 1.0],[-10.0, 10.0])
            ]
        test_points = [
            ([ 0.5, 0.5],[ 5.0, 5.0]),
            ([ 0.5,-0.5],[ 5.0,-5.0]),
            ([-0.5,-0.5],[-5.0,-5.0]),
            ([-0.5, 0.5],[-5.0, 5.0])
            ]

        squarer = SquareTransform(configuration_points)

        for (expected_deflection, position) in test_points:
            actual_x, actual_y = squarer.fit(*position)
            self.assertAlmostEquals(expected_deflection[0], actual_x )
            self.assertAlmostEquals(expected_deflection[1], actual_y )

    
    def test_can_flip_x(self):
        configuration_points = [
            ([ 1.0, 1.0],[-10.0, 10.0]),
            ([ 1.0,-1.0],[-10.0,-10.0]),
            ([-1.0,-1.0],[ 10.0,-10.0]),
            ([-1.0, 1.0],[ 10.0, 10.0])
            ]
        test_points = [
            ([-0.5, 0.5],[ 5.0, 5.0]),
            ([-0.5,-0.5],[ 5.0,-5.0]),
            ([ 0.5,-0.5],[-5.0,-5.0]),
            ([ 0.5, 0.5],[-5.0, 5.0])
            ]

        squarer = SquareTransform(configuration_points)

        for (expected_deflection, position) in test_points:
            actual_x, actual_y = squarer.fit(*position)
            self.assertAlmostEquals(expected_deflection[0], actual_x )
            self.assertAlmostEquals(expected_deflection[1], actual_y )

    def test_can_flip_y(self):
        configuration_points = [
            ([ 1.0, 1.0],[ 10.0,-10.0]),
            ([ 1.0,-1.0],[ 10.0, 10.0]),
            ([-1.0,-1.0],[-10.0, 10.0]),
            ([-1.0, 1.0],[-10.0,-10.0])
            ]
        test_points = [
            ([ 0.5,-0.5],[ 5.0, 5.0]),
            ([ 0.5, 0.5],[ 5.0,-5.0]),
            ([-0.5, 0.5],[-5.0,-5.0]),
            ([-0.5,-0.5],[-5.0, 5.0])
            ]

        squarer = SquareTransform(configuration_points)

        for (expected_deflection, position) in test_points:
            actual_x, actual_y = squarer.fit(*position)
            self.assertAlmostEquals(expected_deflection[0], actual_x )
            self.assertAlmostEquals(expected_deflection[1], actual_y )

    def test_can_rotate(self):
        configuration_points = [
            ([ 1.0, 1.0],[ 10.0,-10.0]),
            ([ 1.0,-1.0],[-10.0,-10.0]),
            ([-1.0,-1.0],[-10.0, 10.0]),
            ([-1.0, 1.0],[ 10.0, 10.0])
            ]
        test_points = [
            ([-0.5, 0.5],[ 5.0, 5.0]),
            ([ 0.5, 0.5],[ 5.0,-5.0]),
            ([ 0.5,-0.5],[-5.0,-5.0]),
            ([-0.5,-0.5],[-5.0, 5.0])
            ]

        squarer = SquareTransform(configuration_points)

        for (expected_deflection, position) in test_points:
            actual_x, actual_y = squarer.fit(*position)
            self.assertAlmostEquals(expected_deflection[0], actual_x )
            self.assertAlmostEquals(expected_deflection[1], actual_y )

    def test_can_skew(self):
        configuration_points = [
            ([ 1.0, 1.0],[ 10.0, 15.0]),
            ([ 1.0,-1.0],[ 10.0,-5.0]),
            ([-1.0,-1.0],[-10.0,-10.0]),
            ([-1.0, 1.0],[-10.0, 10.0])
            ]
        test_points = [
            ([ 0.5, 0.125],[ 5.0, 5.0]),
            ([ 0.5,-0.875],[ 5.0,-5.0]),
            ([-0.5,-0.625],[-5.0,-5.0]),
            ([-0.5, 0.375],[-5.0, 5.0])
            ]

        squarer = SquareTransform(configuration_points)

        for (expected_deflection, position) in test_points:
            actual_x, actual_y = squarer.fit(*position)
            self.assertAlmostEquals(expected_deflection[0], actual_x )
            self.assertAlmostEquals(expected_deflection[1], actual_y )

    def test_can_use_somewhat_random_deflections(self):
        configuration_points = [
            ([ 0.60, 0.74],[  6.0,  7.4]),
            ([ 0.70,-0.68],[  7.0, -6.8]),
            ([-0.80,-0.90],[ -8.0, -9.0]),
            ([-0.75, 0.80],[ -7.5,  8.0])
            ]
        test_points = [
            ([ 0.5, -0.5],[ 5.0, -5.0]),
            ([ 1.0,  1.0],[ 10.0,10.0]),
            ([-0.75, 0.75],[-7.5, 7.5]),
            ([-0.5,-0.5],[-5.0, -5.0])
            ]

        squarer = SquareTransform(configuration_points)

        for (expected_deflection, position) in test_points:
            actual_x, actual_y = squarer.fit(*position)
            self.assertAlmostEquals(expected_deflection[0], actual_x )
            self.assertAlmostEquals(expected_deflection[1], actual_y )


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()