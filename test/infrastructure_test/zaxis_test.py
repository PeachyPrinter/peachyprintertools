import unittest
import os
import sys
import time
import datetime
import logging
from mock import patch, PropertyMock, call, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.zaxis import SerialDripZAxis


class SerialDripZAxisTests(unittest.TestCase):
    pass




if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()