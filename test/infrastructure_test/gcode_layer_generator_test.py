import unittest
import StringIO
import os
import sys
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import test_helpers
from mock import patch

from infrastructure.gcode_layer_generator import GCodeReader, GCodeToLayerGenerator, GCodeCommandReader
from domain.commands import *


class GCodeReaderTests(unittest.TestCase, test_helpers.TestHelpers):
    @patch('infrastructure.gcode_layer_generator.GCodeCommandReader')
    def test_check_should_report_error_on_non_gcode(self, mock_GCodeCommandReader):
        line = "Fake Gcode"
        mock_gcode_command_reader = mock_GCodeCommandReader.return_value
        expected_exception = Exception('Unreconized Command: %s' % (line))
        mock_gcode_command_reader.to_command.side_effect = expected_exception

        test_gcode = StringIO.StringIO("%s\n" % line)

        gcode_reader = GCodeReader(test_gcode)
        errors = gcode_reader.check()
        self.assertEquals(["Error 1: Unreconized Command: %s" % line], errors)

    @patch('infrastructure.gcode_layer_generator.GCodeToLayerGenerator')
    def test_get_layers_should_use_scale(self, mock_GCodeToLayerGenerator):
        line = "Fake Gcode"
        test_gcode = StringIO.StringIO("%s\n" % line)

        gcode_reader = GCodeReader(test_gcode, scale=0.1)
        gcode_reader.get_layers()
        mock_GCodeToLayerGenerator.assert_called_with(test_gcode, scale=0.1, start_height=None)

    @patch('infrastructure.gcode_layer_generator.GCodeToLayerGenerator')
    def test_check_should_use_scale(self, mock_GCodeToLayerGenerator):
        line = "Fake Gcode"
        test_gcode = StringIO.StringIO("%s\n" % line)

        gcode_reader = GCodeReader(test_gcode, scale=0.1)
        gcode_reader.check()
        mock_GCodeToLayerGenerator.assert_called_with(test_gcode, scale=0.1, start_height=None)

    @patch('infrastructure.gcode_layer_generator.GCodeToLayerGenerator')
    def test_check_should_use_start_height(self, mock_GCodeToLayerGenerator):
        line = "Fake Gcode"
        test_gcode = StringIO.StringIO("%s\n" % line)
        expected_start_height = 7

        gcode_reader = GCodeReader(test_gcode, start_height=expected_start_height)
        gcode_reader.check()
        mock_GCodeToLayerGenerator.assert_called_with(test_gcode, scale=1.0, start_height=expected_start_height)


class GCodeToLayerGeneratorTests(unittest.TestCase, test_helpers.TestHelpers):

    @patch('infrastructure.gcode_layer_generator.GCodeCommandReader')
    def test_get_layers_returns_a_single_layer(self, mock_GCodeCommandReader):
        mock_gcode_command_reader = mock_GCodeCommandReader.return_value
        mock_gcode_command_reader.to_command.return_value = [LateralDraw([0.0, 0.0], [0.0, 0.0], 100.0)]
        gcode_line = "G01 X0.00 Y0.00 E1 F100.0\n"
        test_gcode = StringIO.StringIO(gcode_line)
        command_generator = GCodeToLayerGenerator(test_gcode)
        expected = [Layer(0.0, [LateralDraw([0.0, 0.0], [0.0, 0.0], 100.0)])]

        actual = list(command_generator)

        self.assertLayersEquals(expected, actual)

    @patch('infrastructure.gcode_layer_generator.GCodeCommandReader')
    def test_when_scale_provided_gcode_command_called_with_scale(self, mock_GCodeCommandReader):
        mock_gcode_command_reader = mock_GCodeCommandReader.return_value
        mock_gcode_command_reader.to_command.return_value = [LateralDraw([0.0, 0.0], [0.0, 0.0], 100.0)]
        gcode_line = "G01 X0.00 Y0.00 E1 F100.0\n"
        test_gcode = StringIO.StringIO(gcode_line)
        GCodeToLayerGenerator(test_gcode, scale=0.1)
        mock_GCodeCommandReader.assert_called_with(scale=0.1)

    @patch('infrastructure.gcode_layer_generator.GCodeCommandReader')
    def test_get_layers_returns_a_single_layer_with_multipule_commands(self, mock_GCodeCommandReader):
        command1 = LateralDraw([0.0, 0.0], [0.0, 0.0], 100.0)
        command2 = LateralDraw([0.0, 0.0], [1.0, 1.0], 100.0)
        list_of_return_values = [[command2], [command1]]

        def side_effect(self):
            return list_of_return_values.pop()
        mock_gcode_command_reader = mock_GCodeCommandReader.return_value
        mock_gcode_command_reader.to_command.side_effect = side_effect

        gcode_line = "G01 X0.00 Y0.00 E1 F100.0\nG01 X0.00 Y0.00 E1 F100.0\n"
        test_gcode = StringIO.StringIO(gcode_line)
        layer_generator = GCodeToLayerGenerator(test_gcode)
        expected = [Layer(0.0, [command1, command2])]

        actual = list(layer_generator)

        self.assertLayersEquals(expected, actual)

    @patch('infrastructure.gcode_layer_generator.GCodeCommandReader')
    def test_returns_multiple_layers_returns_a_single_commands(self, mock_GCodeCommandReader):
        command1 = LateralDraw([0.0, 0.0], [0.0, 0.0], 100.0)
        command2 = VerticalMove(0.0, 0.1, 100.0)
        command3 = LateralDraw([0.0, 0.0], [1.0, 1.0], 100.0)
        list_of_return_values = [[command3], [command2], [command1]]

        def side_effect(self):
            return list_of_return_values.pop()
        mock_gcode_command_reader = mock_GCodeCommandReader.return_value
        mock_gcode_command_reader.to_command.side_effect = side_effect

        gcode_line = "G01 X0.00 Y0.00 E1 F100.0\nG01 Z0.1 F100.0\nG01 X1.00 Y1.00 E1 F100.0"
        test_gcode = StringIO.StringIO(gcode_line)
        layer_generator = GCodeToLayerGenerator(test_gcode)
        expected = [Layer(0.0, [command1]), Layer(0.1, [command3])]

        actual = list(layer_generator)

        self.assertLayersEquals(expected, actual)

    @patch('infrastructure.gcode_layer_generator.GCodeCommandReader')
    def test_returns_multiple_layers_when_single_command_yields_multipule_lines(self, mock_GCodeCommandReader):
        command1 = LateralDraw([0.0, 0.0], [0.0, 0.0], 100.0)
        command2 = VerticalMove(0.0, 0.1, 100.0)
        command3 = LateralDraw([0.0, 0.0], [1.0, 1.0], 100.0)
        list_of_return_values = [[command3], [command2], [command1]]

        def side_effect(self):
            return list_of_return_values.pop()
        mock_gcode_command_reader = mock_GCodeCommandReader.return_value
        mock_gcode_command_reader.to_command.side_effect = side_effect

        gcode_line = "G01 X0.00 Y0.00 E1 F100.0\nG01 Z0.1 F100.0\nG01 X1.00 Y1.00 E1 F100.0"
        test_gcode = StringIO.StringIO(gcode_line)
        layer_generator = GCodeToLayerGenerator(test_gcode)
        expected = [Layer(0.0, [command1]), Layer(0.1, [command3])]

        actual = list(layer_generator)

        self.assertLayersEquals(expected, actual)

    @patch('infrastructure.gcode_layer_generator.GCodeCommandReader')
    def test_returns_multiple_layers_when_single_command_yields_multipule_vertical_moves(self, mock_GCodeCommandReader):
        command1 = VerticalMove(0.0, 0.1, 100.0)
        command2 = LateralDraw([0.0, 0.0], [1.0, 1.0], 100.0)
        command3 = VerticalMove(0.1, 0.2, 100.0)
        command4 = LateralDraw([0.0, 0.0], [1.0, 1.0], 100.0)
        list_of_return_values = [[command1, command2, command3, command4]]

        def side_effect(self):
            return list_of_return_values.pop()
        mock_gcode_command_reader = mock_GCodeCommandReader.return_value
        mock_gcode_command_reader.to_command.side_effect = side_effect

        gcode_line = "G01 Z0.1 F100.0"
        test_gcode = StringIO.StringIO(gcode_line)
        layer_generator = GCodeToLayerGenerator(test_gcode)
        expected = [Layer(0.1, [command2]), Layer(0.2, [command4])]

        actual = list(layer_generator)

        self.assertLayersEquals(expected, actual)

    @patch('infrastructure.gcode_layer_generator.GCodeCommandReader')
    def test_returns_multiple_layers_start_at_start_height(self, mock_GCodeCommandReader):
        return_values = [[]]
        for i in range(0, 51):
            height = float(i) / 10.0
            return_values[0].append(VerticalMove(height - 0.1, height, 100.0))
            return_values[0].append(LateralDraw([float((i-1) % 2), float((i-1) % 2)], [float(i % 2), float(i % 2)], 100.0))

        def side_effect(self):
            return return_values.pop()

        mock_gcode_command_reader = mock_GCodeCommandReader.return_value
        mock_gcode_command_reader.to_command.side_effect = side_effect

        gcode_line = "G01 Z0.1 F100.0"
        test_gcode = StringIO.StringIO(gcode_line)
        layer_generator = GCodeToLayerGenerator(test_gcode, start_height=4.9)
        expected = [Layer(4.9, [LateralDraw([0.0, 0.0], [1.0, 1.0], 100.0)]), Layer(5.0, [LateralDraw([1.0, 1.0], [0.0, 0.0], 100.0)])]

        actual = list(layer_generator)

        self.assertLayersEquals(expected, actual)

    @patch('infrastructure.gcode_layer_generator.GCodeCommandReader')
    def test_if_last_command_is_move_omited(self, mock_GCodeCommandReader):
        command1 = VerticalMove(0.0, 0.1, 100.0)
        command2 = LateralDraw([0.0, 0.0], [1.0, 1.0], 100.0)
        command3 = LateralDraw([1.0, 1.0], [0.5, 0.5], 100.0)
        command4 = LateralMove([0.5, 0.5], [1.0, 1.0], 100.0)
        list_of_return_values = [[command1, command2, command3, command4]]

        def side_effect(self):
            return list_of_return_values.pop()
        mock_gcode_command_reader = mock_GCodeCommandReader.return_value
        mock_gcode_command_reader.to_command.side_effect = side_effect

        gcode_line = "G01 Z0.1 F100.0\nG01 X1.00 Y1.00 E1 F100.0\nG01 X0.50 Y0.50 E1 F100.0\nG00 X1.00 Y1.00 E1 F100.0"
        test_gcode = StringIO.StringIO(gcode_line)
        layer_generator = GCodeToLayerGenerator(test_gcode)
        expected = [Layer(0.1, [command2, command3])]

        actual = list(layer_generator)

        self.assertLayersEquals(expected, actual)


class GCodeCommandReaderTest(unittest.TestCase, test_helpers.TestHelpers):
    def test_to_command_returns_empty_list_for_comments(self):
        test_gcode_line = ";Comment"
        command_reader = GCodeCommandReader()

        actual = command_reader.to_command(test_gcode_line)

        self.assertEquals([], actual)

    def test_to_command_returns_empty_list_for_blank_lines(self):
        test_gcode_line = "\n"
        command_reader = GCodeCommandReader()

        actual = command_reader.to_command(test_gcode_line)

        self.assertEquals([], actual)

    def test_to_command_returns_empty_list_for_blank(self):
        test_gcode_line = ""
        command_reader = GCodeCommandReader()

        actual = command_reader.to_command(test_gcode_line)

        self.assertEquals([], actual)

    def test_to_command_returns_empty_list_for_ignorable_codes(self):
        test_gcode_lines = [";Comment", "M101", "O NAME OF PROGRAM"]
        command_reader = GCodeCommandReader()

        actuals = [command_reader.to_command(line) for line in test_gcode_lines]

        self.assertEquals([[], [], []], actuals)

    def test_unsupported_codes_raises_exception(self):
        test_gcode_line = "P01 X123.0 C7"
        command_reader = GCodeCommandReader()
        with self.assertRaises(Exception):
            command_reader.to_command(test_gcode_line)

    def test_to_command_returns_a_LateralDraw_given_move_with_extrude(self):
        gcode_line = "G1 X1.0 Y1.0 F6000 E12"
        command_reader = GCodeCommandReader()
        expected = [LateralDraw([0.0, 0.0], [1.0, 1.0], 100.0)]

        actual = command_reader.to_command(gcode_line)

        self.assertCommandsEqual(expected, actual)

    def test_to_command_returns_a_LateralDraw_when_0(self):
        gcode_setup = "G1 X0.0 Y0.0 F6000 E12"
        gcode_line = "G1 X-8.98 Y0.00 E1.71364"
        command_reader = GCodeCommandReader()
        expected = [LateralDraw([0.0, 0.0], [-8.98, 0.0], 100.0)]
        command_reader.to_command(gcode_setup)
        actual = command_reader.to_command(gcode_line)

        self.assertCommandsEqual(expected, actual)

    def test_to_command_remembers_last_speed_if_none_specified(self):
        gcode_setup = "G1 X1.0 Y1.0 F6000 E12"
        gcode_test = "G1 X1.0 Y1.0 E12"
        command_reader = GCodeCommandReader()
        expected = [LateralDraw([1.0, 1.0], [1.0, 1.0], 100.0)]

        command_reader.to_command(gcode_setup)
        actual = command_reader.to_command(gcode_test)

        self.assertCommandsEqual(expected, actual)

    def test_to_command_throws_exception_if_speed_never_specified(self):
        gcode_test = "G1 X1.0 Y1.0 E12"
        command_reader = GCodeCommandReader()

        with self.assertRaises(Exception):
            command_reader.to_command(gcode_test)

    def test_to_command_remembers_last_speed_if_only_specified(self):
        gcode_setup = "G1 F6000"
        gcode_test = "G1 X1.0 Y1.0 E12"
        command_reader = GCodeCommandReader()
        expected_verify = [LateralDraw([0.0, 0.0], [1.0, 1.0], 100.0)]

        setup = command_reader.to_command(gcode_setup)
        verify = command_reader.to_command(gcode_test)

        self.assertEqual([], setup)
        self.assertCommandsEqual(expected_verify, verify)

    def test_to_command_creates_move_if_E_is_0(self):
        gcode_test = "G0 X1.0 Y1.0 F6000 E0.0"
        command_reader = GCodeCommandReader()
        expected = [LateralMove([0.0, 0.0], [1.0, 1.0], 100.0)]

        actual = command_reader.to_command(gcode_test)

        self.assertCommandsEqual(expected, actual)

    def test_to_command_creates_move_if_E_not_specified(self):
        gcode_test = "G0 X1.0 Y1.0 F6000"
        command_reader = GCodeCommandReader()
        expected = [LateralMove([0.0, 0.0], [1.0, 1.0], 100.0)]

        actual = command_reader.to_command(gcode_test)

        self.assertCommandsEqual(expected, actual)

    def test_to_command_handles_vertical_movement(self):
        gcode_test = "G0 Z1.0 F6000 E0"
        command_reader = GCodeCommandReader()
        expected = [VerticalMove(0.0, 1.0, 100.0)]

        actual = command_reader.to_command(gcode_test)

        self.assertCommandsEqual(expected, actual)

    def test_to_command_does_not_permit_handles_vertical_down_movement(self):
        gcode_setup = "G0 Z1.0 F6000 E0"
        gcode_test = "G0 Z0.1 F6000 E0"
        command_reader = GCodeCommandReader()

        command_reader.to_command(gcode_setup)

        with self.assertRaises(Exception):
            command_reader.to_command(gcode_test)

    def test_to_command_allows_vertical_write_provide_layer_increment_specified(self):
        gcode_setup1 = "G0 Z0.1 F6000 E0"
        gcode_setup2 = "G0 Z0.2 F6000 E0"
        gcode_setup3 = "G0 X0.5 Y0.5 F6000"
        gcode_test = "G0 Z0.5 F6000 E1"
        command_reader = GCodeCommandReader()
        expected = [
            VerticalMove(0.2, 0.3, 100.0),
            LateralDraw([0.5, 0.5], [0.5, 0.5], 100.0),
            VerticalMove(0.3, 0.4, 100.0),
            LateralDraw([0.5, 0.5], [0.5, 0.5], 100.0),
            VerticalMove(0.4, 0.5, 100.0),
            LateralDraw([0.5, 0.5], [0.5, 0.5], 100.0),
            ]

        command_reader.to_command(gcode_setup1)
        command_reader.to_command(gcode_setup2)
        command_reader.to_command(gcode_setup3)

        actual = command_reader.to_command(gcode_test)

        self.assertCommandsEqual(expected, actual)

    def test_vertically_diagonal_writes_are_made_moves_and_lateral_draws(self):
        gcode_setup1 = "G0 Z0.1 F6000 E0"
        gcode_setup2 = "G0 Z0.2 F6000 E0"
        gcode_setup3 = "G0 X0.5 Y0.5 F6000"
        gcode_test = "G0 X0.7 Y0.7 Z0.5 F6000 E1"
        command_reader = GCodeCommandReader()
        expected = [
            VerticalMove(0.2, 0.3, 100.0),
            LateralDraw([0.5, 0.5], [0.5, 0.5], 100.0),
            VerticalMove(0.3, 0.4, 100.0),
            LateralDraw([0.5, 0.5], [0.5, 0.5], 100.0),
            VerticalMove(0.4, 0.5, 100.0),
            LateralDraw([0.5, 0.5], [0.5, 0.5], 100.0),
            LateralDraw([0.5, 0.5], [0.7, 0.7], 100.0),
            ]

        command_reader.to_command(gcode_setup1)
        command_reader.to_command(gcode_setup2)
        command_reader.to_command(gcode_setup3)

        self.assertCommandsEqual(expected, command_reader.to_command(gcode_test))

    def test_vertically_diagonal_move_are_made_moves_and_lateral_moves(self):
        gcode_setup1 = "G0 Z0.1 F6000 E0"
        gcode_setup2 = "G0 Z0.2 F6000 E0"
        gcode_setup3 = "G0 X0.5 Y0.5 F6000"
        gcode_test = "G0 X0.7 Y0.7 Z0.5 F6000"
        command_reader = GCodeCommandReader()
        expected = [
            VerticalMove(0.2, 0.5, 100.0),
            LateralMove([0.5, 0.5], [0.7, 0.7], 100.0),
            ]

        command_reader.to_command(gcode_setup1)
        command_reader.to_command(gcode_setup2)
        command_reader.to_command(gcode_setup3)

        self.assertCommandsEqual(expected, command_reader.to_command(gcode_test))

    def test_to_command_handles_unknown_sub_command(self):
        gcode_line = "G1 X1.0 Y1.0 F6000 E12 Q55"
        command_reader = GCodeCommandReader()
        expected = [LateralDraw([0.0, 0.0], [1.0, 1.0], 100)]

        actual = command_reader.to_command(gcode_line)

        self.assertCommandsEqual(expected, actual)

    def test_to_command_handles_units(self):
        gcode_metric = "G21"
        gcode_metric_line = "G1 X1.0 Y1.0 F6000 E12"
        gcode_feet = "G20"
        gcode_feet_line = "G1 X1.0 Y1.0 F6000 E12"
        command_reader = GCodeCommandReader()
        expected_metric = [LateralDraw([0.0, 0.0], [1.0, 1.0], 100.0)]
        expected_feet = [LateralDraw([1.0, 1.0], [25.4, 25.4], 2540.0)]

        command_reader.to_command(gcode_metric)
        self.assertCommandsEqual(expected_metric, command_reader.to_command(gcode_metric_line))

        command_reader.to_command(gcode_feet)
        self.assertCommandsEqual(expected_feet, command_reader.to_command(gcode_feet_line))

    def test_to_command_can_scale_when_scale_provided(self):
        gcode_setup1 = "G0 Z0.1 F6000 E0"
        gcode_setup2 = "G0 Z0.2 F6000 E0"
        gcode_setup3 = "G0 X0.0 Y0.0 F6000"
        gcode_test = "G0 X1.0 Y1.0 Z0.3 F6000"
        command_reader = GCodeCommandReader(scale=0.1)
        expected = [
            VerticalMove(0.02, 0.03, 100.0),
            LateralMove([0.0, 0.0], [0.1, 0.1], 100.0),
            ]

        command_reader.to_command(gcode_setup1)
        command_reader.to_command(gcode_setup2)
        command_reader.to_command(gcode_setup3)

        self.assertCommandsEqual(expected, command_reader.to_command(gcode_test))

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()
