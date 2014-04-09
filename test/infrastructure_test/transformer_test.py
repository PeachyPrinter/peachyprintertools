import unittest
import os
import sys
import numpy as np

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

import test_helpers
from infrastructure.transformer import OneToOneTransfomer

class OneToOneTransformerTests(unittest.TestCase):
    def test_works_on_xyz(self):
        self.assertEquals([1.0,1.0,1.0], OneToOneTransfomer().transform([1.0,1.0,1.0]))

    def test_goes_boom_on_xy(self):
        with self.assertRaises(Exception):
            OneToOneTransfomer().transform([1.0,1.0])

if __name__ == '__main__':
    unittest.main()