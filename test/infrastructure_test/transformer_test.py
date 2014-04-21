import unittest
import os
import sys
import numpy as np

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

import test_helpers
from infrastructure.transformer import OneToOneTransformer, TuningTransformer, HomogenousTransformer

class OneToOneTransformerTests(unittest.TestCase,test_helpers.TestHelpers):
    def test_works_on_xyz(self):
        self.assertEquals([1.0,1.0,1.0], OneToOneTransformer().transform([1.0,1.0,1.0]))

    def test_goes_boom_on_xy(self):
        with self.assertRaises(Exception):
            OneToOneTransfomer().transform([1.0,1.0])

class TuningTransformerTests(unittest.TestCase,test_helpers.TestHelpers):
    def test_works_on_xyz(self):
        tuning_transformer = TuningTransformer()
        self.assertEquals([1.0,1.0], tuning_transformer.transform([1.0,1.0,1.0]))
        self.assertEquals([0.5,0.5], tuning_transformer.transform([0.0,0.0,1.0]))
        self.assertEquals([0.0,0.0], tuning_transformer.transform([-1.0,-1.0,1.0]))

    def test_works_on_xyz_with_scale(self):
        tuning_transformer = TuningTransformer(scale = 0.5)
        self.assertEquals([0.75,0.75], tuning_transformer.transform([1.0,1.0,1.0]))
        self.assertEquals([0.5,0.5], tuning_transformer.transform([0.0,0.0,1.0]))
        self.assertEquals([0.25,0.25], tuning_transformer.transform([-1.0,-1.0,1.0]))

    def test_should_kaboom_if_scale_greater_then_1(self):
        with self.assertRaises(Exception):
            TuningTransformer(scale = 1.5)

    def test_should_kaboom_if_scale_not_greater_then_0(self):
        with self.assertRaises(Exception):
            TuningTransformer(scale = 0.0)

    def test_should_kaboom_if_request_points_out_of_bounds(self):
        tuning_transformer = TuningTransformer(scale = 1.0)
        with self.assertRaises(Exception):
            tuning_transformer.transform([1.1,1.0,1.0])
        with self.assertRaises(Exception):
            tuning_transformer.transform([-1.1,1.0,1.0])
        with self.assertRaises(Exception):
            tuning_transformer.transform([1.0,1.1,1.0])
        with self.assertRaises(Exception):
            tuning_transformer.transform([1.0,-1.1,1.0])

class HomogenousTransformerTests(unittest.TestCase,test_helpers.TestHelpers):
    def test_given_an_one_to_one_mapping_yields_expected_results(self):
        perfect_data = [
            {'in': [1.0,  1.0,0.0], 'out': [1.0,  1.0,0.0]},
            {'in': [1.0, -1.0,0.0], 'out': [1.0, -1.0,0.0]},
            {'in': [-1.0,-1.0,0.0], 'out': [-1.0,-1.0,0.0]},
            {'in': [-1.0, 1.0,0.0], 'out': [-1.0, 1.0,0.0]},
            {'in': [1.0,  1.0,1.0], 'out': [1.0,  1.0,1.0]},
            {'in': [1.0, -1.0,1.0], 'out': [1.0, -1.0,1.0]},
            {'in': [-1.0,-1.0,1.0], 'out': [-1.0,-1.0,1.0]},
            {'in': [-1.0, 1.0,1.0], 'out': [-1.0, 1.0,1.0]},
            ]
        scale = 1.0
        transformer = HomogenousTransformer(scale, perfect_data)

        test_points = [ [0,0,0] , [0.5,0.5,0.5],[-0.5,-0.5,0.5],[1.0,  1.0,0.0],[1.0, -1.0,0.0],[-1.0,-1.0,0.0],[-1.0, 1.0,0.0],[1.0,  1.0,1.0],[1.0, -1.0,1.0],[-1.0,-1.0,1.0],[-1.0, 1.0,1.0]]

        for point in test_points:
            self.assertNumpyArrayEquals(point, transformer.transform(point))

    def test_given_an_one_to_one_mapping_and_scale_yields_expected_results(self):
        perfect_data = [
            {'in': [1.0,  1.0,0.0], 'out': [1.0,  1.0,0.0]},
            {'in': [1.0, -1.0,0.0], 'out': [1.0, -1.0,0.0]},
            {'in': [-1.0,-1.0,0.0], 'out': [-1.0,-1.0,0.0]},
            {'in': [-1.0, 1.0,0.0], 'out': [-1.0, 1.0,0.0]},
            {'in': [1.0,  1.0,1.0], 'out': [1.0,  1.0,1.0]},
            {'in': [1.0, -1.0,1.0], 'out': [1.0, -1.0,1.0]},
            {'in': [-1.0,-1.0,1.0], 'out': [-1.0,-1.0,1.0]},
            {'in': [-1.0, 1.0,1.0], 'out': [-1.0, 1.0,1.0]},
            ]
        scale = 0.5
        transformer = HomogenousTransformer(scale, perfect_data)

        test_points = [ [0,0,0] , [0.5,0.5,0.5],[-0.5,-0.5,0.5],[1.0,  1.0,0.0],[1.0, -1.0,0.0],[-1.0,-1.0,0.0],[-1.0, 1.0,0.0],[1.0,  1.0,1.0],[1.0, -1.0,1.0],[-1.0,-1.0,1.0],[-1.0, 1.0,1.0]]
        expected_points = [ [ x * scale, y * scale, z * scale] for [x,y,z] in test_points ]

        for index in range(0, len(test_points)):
            self.assertNumpyArrayEquals(expected_points[index], transformer.transform(test_points[index]))

    # def test_given_a_non_to_one_mapping_and_scale_yields_expected_results(self):
    #     perfect_data = [
    #         {'in': [1.0,  1.0,0.0], 'out': [2.0,  1.0,0.0]},
    #         {'in': [1.0, -1.0,0.0], 'out': [2.0, -1.0,0.0]},
    #         {'in': [-1.0,-1.0,0.0], 'out': [-2.0,-1.0,0.0]},
    #         {'in': [-1.0, 1.0,0.0], 'out': [-2.0, 1.0,0.0]},
    #         {'in': [1.0,  1.0,1.0], 'out': [2.0,  1.0,1.0]},
    #         {'in': [1.0, -1.0,1.0], 'out': [2.0, -1.0,1.0]},
    #         {'in': [-1.0,-1.0,1.0], 'out': [-2.0,-1.0,1.0]},
    #         {'in': [-1.0, 1.0,1.0], 'out': [-2.0, 1.0,1.0]},
    #         ]
    #     scale = 1.0
    #     transformer = HomogenousTransformer(scale, perfect_data)

    #     test_points = [ [0,0,0] , [0.5,0.5,0.5],[-0.5,-0.5,0.5],[1.0,  1.0,0.0],[1.0, -1.0,0.0],[-1.0,-1.0,0.0],[-1.0, 1.0,0.0],[1.0,  1.0,1.0],[1.0, -1.0,1.0],[-1.0,-1.0,1.0],[-1.0, 1.0,1.0]]
    #     expected_points = [ [ x * 2.0, y, z] for [x,y,z] in test_points ]

    #     for index in range(0, len(test_points)):
    #         self.assertNumpyArrayEquals(expected_points[index], transformer.transform(test_points[index]))

    #Bounds check


if __name__ == '__main__':
    unittest.main()