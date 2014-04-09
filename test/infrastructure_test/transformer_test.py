import unittest
import os
import sys
import numpy as np

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

import test_helpers
from infrastructure.transformer import OneToOneTransformer, TuningTransformer

class OneToOneTransformerTests(unittest.TestCase):
    def test_works_on_xyz(self):
        self.assertEquals([1.0,1.0,1.0], OneToOneTransformer().transform([1.0,1.0,1.0]))

    def test_goes_boom_on_xy(self):
        with self.assertRaises(Exception):
            OneToOneTransfomer().transform([1.0,1.0])

class TuningTransformerTests(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()