import unittest
import os
import sys
import logging
import numpy as np
import math

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

import test_helpers
from infrastructure.point_transformer import *
from infrastructure.simulator import PeachyPrinterFactory

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

    def test_requires_x_points(self):
        pass

    def test_transform_returns_a_set_of_deflections(self):
        pass

    def test_perfect_printer_accuracy(self):
        acceptable_diffrence = 60.53
        printer = self.factory.new_peachy_printer()
        deflection_points = [
            [ 1.0, 1.0],[-1.0, 1.0],[ 1.0,-1.0],[-1.0, -1.0],
            [ 0.0, 1.0 ],[ 0.0, -1.0 ],[1.0,0.0],[-1.0,0.0],
            [ 0.8, 0.8],[-0.8, 0.8],[ 0.8,-0.8],[-0.8, -0.8],
            [ 0.0, 0.8],[ 0.0, -0.8 ],[0.8,0.0],[-0.8,0.0]
        ]
        calibration_points = [ ((dx,dy),printer.write(dx,dy,-300).tolist()[0][:2]) for (dx,dy) in deflection_points ]

        pt = PointTransformer(calibration_points)

        difference = 0
        for (x,y,z) in self.get_test_points(10,-300):
            expected_point = printer.write(x,y,z).tolist()[0][:3]
            actual_deflection = pt.transform(expected_point)
            print('A: %s' % actual_deflection)
            difference += math.sqrt( (x - actual_deflection[0])**2 + (y - actual_deflection[1])**2 )

        self.assertTrue(difference < acceptable_diffrence, 'Difference was %s' % difference)



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




if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()