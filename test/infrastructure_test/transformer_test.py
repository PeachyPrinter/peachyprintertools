import unittest
import os
import sys
import logging
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
        self.assertEquals([0.5,0.5], tuning_transformer.transform([0.5,0.5,1.0]))
        self.assertEquals([0.0,0.0], tuning_transformer.transform([0.0,0.0,1.0]))

    def test_works_on_xyz_with_scale(self):
        tuning_transformer = TuningTransformer(scale = 0.5)
        self.assertEquals([0.75,0.75], tuning_transformer.transform([1.0,1.0,1.0]))
        self.assertEquals([0.5,0.5], tuning_transformer.transform([0.5,0.5,1.0]))
        self.assertEquals([0.25,0.25], tuning_transformer.transform([0.0,0.0,1.0]))

    def test_should_kaboom_if_scale_greater_then_1(self):
        with self.assertRaises(Exception):
            TuningTransformer(scale = 1.5)

    def test_should_kaboom_if_scale_not_greater_then_0(self):
        with self.assertRaises(Exception):
            TuningTransformer(scale = 0.0)

    def test_should_adjust_if_request_points_out_of_bounds(self):
        tuning_transformer = TuningTransformer(scale = 1.0)
        self.assertEquals([1.0, 1.0 ], tuning_transformer.transform([1.1,1.0,1.0]))
        self.assertEquals([0.0, 1.0 ], tuning_transformer.transform([-0.1,1.0,1.0]))
        self.assertEquals([1.0, 1.0 ], tuning_transformer.transform([1.0,1.1,1.0]))
        self.assertEquals([1.0, 0.0 ], tuning_transformer.transform([1.0,-0.1,1.0]))

class HomogenousTransformerTests(unittest.TestCase,test_helpers.TestHelpers):
    def test_given_a_basic_mapping_yields_expected_results(self):
        perfect_data = {
            'height': 1.0 , 
            'lower_points': { 
                (1.0, 1.0):( 1.0,  1.0),
                (0.0, 1.0):(-1.0,  1.0),
                (1.0, 0.0):( 1.0, -1.0),
                (0.0, 0.0):(-1.0, -1.0)
                },
            'upper_points': { 
                (1.0, 1.0):( 1.0,  1.0),
                (0.0, 1.0):(-1.0,  1.0),
                (1.0, 0.0):( 1.0, -1.0),
                (0.0, 0.0):(-1.0, -1.0)
                }
        }
        scale = 1.0
        transformer = HomogenousTransformer(perfect_data, scale)

        test_points = [ 
            [1.0,1.0,0.0],[-1.0,-1.0,0.0],[0.0,0.0,0.0],[0.5,0.5,0.0],
            [1.0,1.0,2.5],[-1.0,-1.0,2.5],[0.0,0.0,2.5],[0.5,0.5,2.5],
            [1.0,1.0,5.0],[-1.0,-1.0,5.0],[0.0,0.0,5.0],[0.5,0.5,5.0]
        ]

        expected_points = [((x + 1.0) / 2.0,(y + 1.0) / 2.0) for (x,y,z) in test_points ]
        actual_points   = [ transformer.transform ( point) for point in test_points ]
        
        self.assertEquals(expected_points, actual_points)

    def test_given_a_basic_mapping_yields_expected_results_with_scale(self):
        perfect_data = {
            'height': 1.0 , 
            'lower_points': { 
                (1.0, 1.0):( 1.0,  1.0),
                (0.0, 1.0):(-1.0,  1.0),
                (1.0, 0.0):( 1.0, -1.0),
                (0.0, 0.0):(-1.0, -1.0)
                },
            'upper_points': { 
                (1.0, 1.0):( 1.0,  1.0),
                (0.0, 1.0):(-1.0,  1.0),
                (1.0, 0.0):( 1.0, -1.0),
                (0.0, 0.0):(-1.0, -1.0)
                }
        }
        scale = 0.5
        transformer = HomogenousTransformer(perfect_data, scale)

        test_points = [ 
            [1.0,1.0,0.0],[-1.0,-1.0,0.0],[0.0,0.0,0.0],[0.5,0.5,0.0]
        ]

        expected_points = [
            (0.75,0.75),(0.25,0.25),(0.5,0.5),(0.625,0.625)
        ]

        actual_points   = [ transformer.transform ( point) for point in test_points ]
        
        self.assertEquals(expected_points, actual_points)

    def test_given_a_basic_mapping_yields_expected_results(self):
        perfect_data = {
            'height': 5.0 , 
            'lower_points': { 
                (1.0, 1.0):( 4.0,  4.0),
                (0.0, 1.0):(-4.0,  4.0),
                (1.0, 0.0):( 4.0, -4.0),
                (0.0, 0.0):(-4.0, -4.0)
                },
            'upper_points': { 
                (1.0, 1.0):( 1.0,  1.0),
                (0.0, 1.0):(-1.0,  1.0),
                (1.0, 0.0):( 1.0, -1.0),
                (0.0, 0.0):(-1.0, -1.0)
                }
        }
        scale = 1.0
        transformer = HomogenousTransformer(perfect_data, scale)

        test_points = [ 
            [1.0,1.0,0.0],[-1.0,-1.0,0.0],[0.0,0.0,0.0],[0.5,0.5,0.0],
            # [1.0,1.0,2.5],[-1.0,-1.0,2.5],[0.0,0.0,2.5],[0.5,0.5,2.5],
            [1.0,1.0,5.0],[-1.0,-1.0,5.0],[0.0,0.0,5.0],[0.5,0.5,5.0]
        ]

        expected_points = [ 
            ( 0.6250, 0.6250),( 0.3750, 0.3750),( 0.5000, 0.5000),( 0.5625, 0.5625),
            # ( 0.6667, 0.6667),( 0.3333, 0.3333),( 0.5000, 0.5000),( 0.5833, 0.5833),
            ( 1.0000, 1.0000),( 0.0000, 0.0000),( 0.5000, 0.5000),( 0.7500, 0.7500)
        ]

        actual_points   = [ transformer.transform ( point) for point in test_points ]
        
        self.assertEquals(expected_points, actual_points)
   

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()