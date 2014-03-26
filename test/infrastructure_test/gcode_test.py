import unittest
import StringIO
import os
import sys

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

import test_helpers
from mock import patch

from infrastructure.gcode import GCodeReader, GCodeToLayerGenerator, GCodeCommandReader
from domain.commands import * 

class GCodeReaderTests(unittest.TestCase, test_helpers.TestHelpers):
    @patch('infrastructure.gcode.GCodeCommandReader')
    def test_check_should_report_error_on_non_gcode(self, mock_GCodeCommandReader):
        line = "Fake Gcode"
        mock_gcode_command_reader = mock_GCodeCommandReader.return_value
        expected_exception = Exception('Unreconized Command: %s' % (line))
        mock_gcode_command_reader.to_command.side_effect = expected_exception

        test_gcode = StringIO.StringIO("%s\n" % line)

        gcode_reader = GCodeReader(test_gcode)
        errors = gcode_reader.check()
        self.assertEquals(["Error 1: Unreconized Command: %s" % line ] , errors)

class GCodeToLayerGeneratorTests(unittest.TestCase, test_helpers.TestHelpers):

    @patch('infrastructure.gcode.GCodeCommandReader')
    def test_get_layers_returns_a_single_layer(self, mock_GCodeCommandReader):
        mock_gcode_command_reader = mock_GCodeCommandReader.return_value
        mock_gcode_command_reader.to_command.return_value = LateralDraw(0.0,0.0,100.0)
        gcode_line = "G01 X0.00 Y0.00 E1 F100.0\n"
        test_gcode = StringIO.StringIO(gcode_line)
        command_generator = GCodeToLayerGenerator(test_gcode)
        expected =  [ Layer(0.0, [LateralDraw(0.00, 0.00, 100.0)]) ]

        actual = list(command_generator)

        self.assertLayersEquals(expected, actual)

    @patch('infrastructure.gcode.GCodeCommandReader')
    def test_get_layers_returns_a_single_layer_with_multipule_commands(self,mock_GCodeCommandReader):
        command1 = LateralDraw(0.0,0.0,100.0)
        command2 = LateralDraw(1.0,1.0,100.0)
        list_of_return_values= [ command2, command1 ]
        def side_effect(self):
            return list_of_return_values.pop()
        mock_gcode_command_reader = mock_GCodeCommandReader.return_value
        mock_gcode_command_reader.to_command.side_effect = side_effect

        gcode_line = "G01 X0.00 Y0.00 E1 F100.0\nG01 X0.00 Y0.00 E1 F100.0\n"
        test_gcode = StringIO.StringIO(gcode_line)
        layer_generator = GCodeToLayerGenerator(test_gcode)
        expected =  [ Layer(0.0, [ command1, command2 ]) ]

        actual = list(layer_generator)

        self.assertLayersEquals(expected, actual)

    @patch('infrastructure.gcode.GCodeCommandReader')
    def test_returns_multiple_layers_returns_a_single_commands(self,mock_GCodeCommandReader):
        command1 = LateralDraw(0.0,0.0,100.0)
        command2 = VerticalMove(0.1,100.0)
        command3 = LateralDraw(1.0,1.0,100.0)
        list_of_return_values = [ command3, command2, command1 ]
        def side_effect(self):
            return list_of_return_values.pop()
        mock_gcode_command_reader = mock_GCodeCommandReader.return_value
        mock_gcode_command_reader.to_command.side_effect = side_effect

        gcode_line = "G01 X0.00 Y0.00 E1 F100.0\nG01 Z0.1 F100.0\nG01 X1.00 Y1.00 E1 F100.0"
        test_gcode = StringIO.StringIO(gcode_line)
        layer_generator = GCodeToLayerGenerator(test_gcode)
        expected =  [ Layer(0.0, [ command1 ]), Layer(0.1, [ command3 ]) ]

        actual = list(layer_generator)
        
        self.assertLayersEquals(expected, actual)

class GCodeCommandReaderTest(unittest.TestCase, test_helpers.TestHelpers):
    def test_to_command_returns_empty_list_for_comments(self):
        test_gcode_line = ";Comment"
        command_reader = GCodeCommandReader()

        actual = command_reader.to_command(test_gcode_line)
        
        self.assertEquals([], actual)

    def test_to_command_returns_empty_list_for_ignorable_codes(self):
        test_gcode_line = ";Comment\nM101\nO NAME OF PROGRAM"
        command_reader = GCodeCommandReader()

        actual = command_reader.to_command(test_gcode_line)
        
        self.assertEquals([], actual)
# units

if __name__ == '__main__':
    unittest.main()

# @patch('my_module.MyClass')
# def test_my_method_shouldCallMyClassMethodMyMethod_whenSomeOtherClassMethodIsCalled(self, mock_my_class):
#     some_other_class =  SomeOtherClassThatUsesMyClass()
#     some_other_class.method_under_test()
#     self.assertTrue(mock_my_class.called)