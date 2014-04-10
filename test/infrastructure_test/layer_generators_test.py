import unittest
import os
import sys
from mock import patch

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from infrastructure.layer_generators import SinglePointGenerator, CalibrationLineGenerator
from domain.commands import *
import test_helpers

class SinglePointGeneratorTests(unittest.TestCase,test_helpers.TestHelpers):
    def test_can_call_next_and_get_specified_command(self):
        layer_generator = SinglePointGenerator([0.0,0.0])
        expected = Layer(0.0, commands = [LateralDraw([0.0,0.0],[0.0,0.0],1)])
        actual = layer_generator.next()
        self.assertLayerEquals(expected,actual)

    def test_can_call_next_after_updating_point(self):
        layer_generator = SinglePointGenerator([0.0,0.0])
        expected = Layer(0.0, commands = [LateralDraw([1.0,1.0],[1.0,1.0],1)])
        layer_generator.next()
        layer_generator.set([1.0,1.0])
        actual = layer_generator.next()
        self.assertLayerEquals(expected,actual)

class CalibrationLineGeneratorTests(unittest.TestCase,test_helpers.TestHelpers):
    def test_can_call_next_and_get_specified_command(self):
        layer_generator = CalibrationLineGenerator()
        expected = Layer(0.0, commands = [LateralDraw([-1.0,0.0],[1.0,0.0],1),LateralDraw([1.0,0.0],[-1.0,0.0],1)], )
        actual = layer_generator.next()
        self.assertLayerEquals(expected,actual)