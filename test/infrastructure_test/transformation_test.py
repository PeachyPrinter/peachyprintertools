import unittest
import os
import sys

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))


import test_helpers
from infrastructure.transformation import Transformation

class TransformationTests(unittest.TestCase, test_helpers.TestHelpers):

    def test_given_a_square_refrence_area_center_is_center(self):
        square = [[-1.0,-1.0],[1.0,-1.0],[1.0,1.0],[-1.0,1.0]]
        t = Transformation(square)
        expected = [0,0]
        actual = t.translate([0,0])
        self.assertEqual(expected, actual)

    # def test_given_a_retangular_refrence_area_off_center(self):
    #     square = [[-2.0,-1.0],[2.0,-1.0],[2.0,1.0],[-2.0,1.0]]
    #     t = Transformation(square)
    #     expected = [0.5,1]
    #     actual = t.translate([1,1])
    #     self.assertEqual(expected, actual)