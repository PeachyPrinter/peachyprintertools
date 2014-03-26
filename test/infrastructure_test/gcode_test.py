import unittest
import StringIO
import os
import sys

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

import test_helpers

from infrastructure.gcode import GCodeReader, GCodeToLayerGenerator
from domain.commands import * 

class GCodeReaderTests(unittest.TestCase, test_helpers.TestHelpers):
    def test_check_should_report_error_on_non_gcode(self):
        line = "Fake Gcode"
        test_gcode = StringIO.StringIO("%s\n" % line)

        gcode_reader = GCodeReader(test_gcode)
        errors = gcode_reader.check()
        self.assertEquals(["Unreconized Command 1: %s" % line ] , errors)

class GCodeToLayerGeneratorTests(unittest.TestCase, test_helpers.TestHelpers):

    def test_get_layers_ignores_comments(self):
        test_gcode = StringIO.StringIO(";Comment\nG1 X0.00 Y0.00 E0\n")

        command_generator = GCodeToLayerGenerator(test_gcode)
        list(command_generator)

    def test_get_layers_returns_a_single_layer(self):
        gcode_line = "G01 X0.00 Y0.00 E1 F100.0\n"
        test_gcode = StringIO.StringIO(gcode_line)
        command_generator = GCodeToLayerGenerator(test_gcode)
        expected =  [ Layer(0.0, [LateralDraw(0.00, 0.00, 100.0)]) ]
        actual = list(command_generator)

        self.assertLayersEquals(expected, actual)

    def test_get_layers_returns_a_single_layer(self):
        gcode_line = "G01 X0.00 Y0.00 E1 F100.0\n"
        test_gcode = StringIO.StringIO(gcode_line)
        command_generator = GCodeToLayerGenerator(test_gcode)
        expected =  [ Layer(0.0, [LateralDraw(0.00, 0.00, 100.0)]) ]
        actual = list(command_generator)

        self.assertLayersEquals(expected, actual)

# units

if __name__ == '__main__':
    unittest.main()