import unittest
import os
import sys
import logging
import numpy as np

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

import test_helpers
from infrastructure.point_transformer import PointTransformer

class PointTransformerTest(unittest.TestCase):
    def test_point_transformer_throws_exception_if_not_enough_points(self):
        x,y,z = 0.0,0.0,0.0
        x1,y1,z1 = 1.0,1.0,0.0
        points = [([x,y,z],[x1,y1,z1])]
        with self.assertRaises(Exception):
            pt = PointTransformer(points)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()