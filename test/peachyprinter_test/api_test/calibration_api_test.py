import unittest
import os
import sys
from mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

import test_helpers
from peachyprinter.api.calibration_api import CalibrationAPI

@patch('peachyprinter.api.calibration_api.OrientationGenerator')
@patch('peachyprinter.api.calibration_api.SerialCommunicator')
@patch('peachyprinter.api.calibration_api.MicroDisseminator')
@patch('peachyprinter.api.calibration_api.LaserControl')
@patch('peachyprinter.domain.configuration_manager.ConfigurationManager')
@patch('peachyprinter.api.calibration_api.HomogenousTransformer')
@patch('peachyprinter.api.calibration_api.MachineState')
@patch('peachyprinter.api.calibration_api.MachineStatus')
@patch('peachyprinter.api.calibration_api.Controller')
@patch('peachyprinter.api.calibration_api.PathToPoints')
@patch('peachyprinter.api.calibration_api.TuningTransformer')
@patch('peachyprinter.api.calibration_api.LayerWriter')
@patch('peachyprinter.api.calibration_api.LayerProcessing')
@patch('peachyprinter.api.calibration_api.SinglePointGenerator')
@patch('peachyprinter.api.calibration_api.BlinkGenerator')
@patch('peachyprinter.api.calibration_api.CalibrationLineGenerator')
@patch('peachyprinter.api.calibration_api.HilbertGenerator')
@patch('peachyprinter.api.calibration_api.SquareGenerator')
@patch('peachyprinter.api.calibration_api.CircleGenerator')
@patch('peachyprinter.api.calibration_api.SpiralGenerator')
@patch('peachyprinter.api.calibration_api.MemoryHourglassGenerator')
class CalibrationAPITests(unittest.TestCase, test_helpers.TestHelpers):

    def setup_mocks(self, args):
        self.mock_OrientationGenerator =                 args[20]
        self.mock_SerialCommunicator =                   args[19]
        self.mock_MicroDisseminator =                    args[18]
        self.mock_LaserControl =                         args[17]
        self.mock_ConfigurationManager =                 args[16]
        self.mock_HomogenousTransformer =                args[15]
        self.mock_MachineState =                         args[14]
        self.mock_MachineStatus =                        args[13]
        self.mock_Controller =                           args[12]
        self.mock_PathToPoints =                         args[11]
        self.mock_TuningTransformer =                    args[10]
        self.mock_LayerWriter =                          args[9]
        self.mock_LayerProcessing =                      args[8]
        self.mock_SinglePointGenerator =                 args[7]
        self.mock_BlinkGenerator =                       args[6]
        self.mock_CalibrationLineGenerator =             args[5]
        self.mock_HilbertGenerator =                     args[4]
        self.mock_SquareGenerator =                      args[3]
        self.mock_CircleGenerator =                      args[2]
        self.mock_SpiralGenerator =                      args[1]
        self.mock_MemoryHourglassGenerator =             args[0]

        self.mock_orientation_generator =                self.mock_OrientationGenerator.return_value
        self.mock_serial_communicator =                  self.mock_SerialCommunicator.return_value
        self.mock_micro_disseminator =                   self.mock_MicroDisseminator.return_value
        self.mock_laser_control =                        self.mock_LaserControl.return_value
        self.mock_configuration_manager =                self.mock_ConfigurationManager.return_value
        self.mock_homogenous_transformer =               self.mock_HomogenousTransformer.return_value
        self.mock_machine_state =                        self.mock_MachineState.return_value
        self.mock_machine_status =                       self.mock_MachineStatus.return_value
        self.mock_controller =                           self.mock_Controller.return_value
        self.mock_path_to_audio =                        self.mock_PathToPoints.return_value
        self.mock_tuning_transformer =                   self.mock_TuningTransformer.return_value
        self.mock_layer_writer =                         self.mock_LayerWriter.return_value
        self.mock_layer_processing =                     self.mock_LayerProcessing.return_value
        self.mock_single_point_generator =               self.mock_SinglePointGenerator.return_value
        self.mock_blink_generator =                      self.mock_BlinkGenerator.return_value
        self.mock_calibration_line_generator =           self.mock_CalibrationLineGenerator.return_value
        self.mock_hilbert_generator =                    self.mock_HilbertGenerator.return_value
        self.mock_square_generator =                     self.mock_SquareGenerator.return_value
        self.mock_circle_generator =                     self.mock_CircleGenerator.return_value
        self.mock_spiral_generator =                     self.mock_SpiralGenerator.return_value
        self.mock_memory_hourglass_generator =           self.mock_MemoryHourglassGenerator.return_value

    def test_init_creates_a_controller_with_digital_config(self, *args):
        self.setup_mocks(args)
        actual_samples = 77
        self.mock_micro_disseminator.samples_per_second = actual_samples
        config = self.default_config
        config.circut.circut_type = 'Digital'
        config.options.post_fire_delay = 5
        config.options.slew_delay = 5
        config.options.wait_after_move_milliseconds = 5
        self.mock_configuration_manager.load.return_value = config
        CalibrationAPI(self.mock_configuration_manager, 'Spam')

        self.mock_SinglePointGenerator.assert_called_with()

        self.mock_LaserControl.assert_called_with(
            self.default_config.cure_rate.override_laser_power_amount
            )
        self.mock_MicroDisseminator.assert_called_with(
            self.mock_laser_control,
            self.mock_serial_communicator,
            self.default_config.micro_com.rate
            )

        self.mock_SerialCommunicator.assert_called_with(
            self.default_config.micro_com.port,
            self.default_config.micro_com.header,
            self.default_config.micro_com.footer,
            self.default_config.micro_com.escape,
            )

        self.mock_serial_communicator.start.assert_called_with()

        self.mock_TuningTransformer.assert_called_with(
            scale=self.default_config.calibration.max_deflection
            )

        self.mock_PathToPoints.assert_called_with(
            actual_samples,
            self.mock_tuning_transformer,
            self.default_config.options.laser_thickness_mm
            )

        self.mock_LayerWriter.assert_called_with(
            self.mock_micro_disseminator,
            self.mock_path_to_audio,
            self.mock_laser_control,
            self.mock_machine_state,
            post_fire_delay_speed=100.0,
            slew_delay_speed=100.0
            )

    def test_stop_should_call_stop_on_controller(self, *args):
        self.setup_mocks(args)
        self.mock_configuration_manager.load.return_value = self.default_config
        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        calibration_api.close()

        self.mock_controller.close.assert_called_with()

    def test_ini_should_load_the_correct_printer(self, *args):
        self.setup_mocks(args)
        self.mock_configuration_manager.load.return_value = self.default_config

        CalibrationAPI(self.mock_configuration_manager, 'Spam')

        self.mock_configuration_manager.load.assert_called_with('Spam')

    def test_show_point_should_set_coordanates_on_Single_Point_Generator(self, *args):
        self.setup_mocks(args)
        self.mock_configuration_manager.load.return_value = self.default_config
        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')
        x, y, z = 1.0, 0.2, 1.0

        calibration_api.show_point([x, y, z])

        self.assertEquals([x, y], self.mock_single_point_generator.xy)

    def test_show_point_should_use_Single_Point_Generator(self, *args):
        self.setup_mocks(args)
        self.mock_configuration_manager.load.return_value = self.default_config

        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')
        x, y, z = 1.0, 0.2, 1.0

        calibration_api.show_line()
        calibration_api.show_point([x, y, z])

        self.mock_controller.change_generator.assert_called_with(self.mock_single_point_generator)

    def test_show_blink_should_use_blink_Generator(self, *args):
        self.setup_mocks(args)
        self.mock_configuration_manager.load.return_value = self.default_config

        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')
        x, y, z = 1.0, 0.2, 1.0

        calibration_api.show_line()
        calibration_api.show_blink([x, y, z])

        self.mock_controller.change_generator.assert_called_with(self.mock_blink_generator)

    def test_set_laser_override(self, *args):
        self.setup_mocks(args)
        self.mock_configuration_manager.load.return_value = self.default_config

        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        calibration_api.set_laser_off_override(True)
        self.assertTrue(self.mock_controller.laser_off_override)
        calibration_api.set_laser_off_override(False)
        self.assertFalse(self.mock_controller.laser_off_override)

    @patch('peachyprinter.api.calibration_api.CalibrationLineGenerator')
    def test_show_line_should_use_CalibrationLineGenerator(self, mock_CalibrationLineGenerator, *args):
        self.setup_mocks(args)
        self.mock_configuration_manager.load.return_value = self.default_config

        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        calibration_api.show_line()

        self.mock_controller.change_generator.assert_called_with(self.mock_calibration_line_generator)

    def test_show_line_should_use_OrientationGenerator(self, *args):
        self.setup_mocks(args)
        self.mock_configuration_manager.load.return_value = self.default_config

        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        calibration_api.show_orientation()

        self.mock_controller.change_generator.assert_called_with(self.mock_orientation_generator)

    def test_get_patterns_should_return_available_test_patterns(self, *args):
        self.setup_mocks(args)
        self.mock_configuration_manager.load.return_value = self.default_config
        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        patterns = calibration_api.get_test_patterns()

        self.assertEquals(set(['Memory Hourglass', 'NESW', 'Damping Test', 'Hilbert Space Filling Curve', 'Spiral', 'Square', 'Circle', 'Twitch']),set(patterns))

    def test_change_pattern_should_raise_exception_when_test_patterns_unavailable(self, *args):
        self.setup_mocks(args)
        self.mock_configuration_manager.load.return_value = self.default_config
        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        with self.assertRaises(Exception):
            calibration_api.show_test_pattern("Shrubberies")

    @patch('peachyprinter.api.calibration_api.HilbertGenerator')
    def test_change_pattern_should_change_pattern_on_controller(self, mock_HilbertGenerator, *args):
        self.setup_mocks(args)
        self.mock_configuration_manager.load.return_value = self.default_config

        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')
        calibration_api.show_test_pattern("Hilbert Space Filling Curve")
        self.mock_controller.change_generator.assert_called_with(self.mock_hilbert_generator)

    def test_current_calibration_returns_the_existing_configuration(self, *args):
        self.setup_mocks(args)
        expected_config = self.default_config
        self.mock_configuration_manager.load.return_value = expected_config
        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        self.assertEqual(calibration_api.current_calibration(), expected_config.calibration)

    def test_save_points_should_save_points(self, *args):
        self.setup_mocks(args)
        self.mock_configuration_manager.load.return_value = self.default_config
        expected_lower = {
                (1.0, 1.0): (1.0,  1.0), (0.0, 1.0): (-1.0,  1.0),
                (1.0, 0.0): (1.0, -1.0), (0.0, 0.0): (-1.0, -1.0)
                }
        expected_upper = {
                (1.0, 1.0): (1.0,  1.0), (0.0, 1.0): (-1.0,  1.0),
                (1.0, 0.0): (1.0, -1.0), (0.0, 0.0): (-1.0, -1.0)
                }
        expected_height = 1.0
        expected_config = self.default_config
        expected_config.calibration.height = expected_height
        expected_config.calibration.lower_points = expected_lower
        expected_config.calibration.upper_points = expected_upper

        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')
        calibration_api.save_points(expected_height, expected_lower, expected_upper)

        self.assertConfigurationEqual(expected_config, self.mock_configuration_manager.save.mock_calls[0][1][0])

    @patch('peachyprinter.api.calibration_api.HomogenousTransformer')
    def test_show_test_pattern_should_apply_calibration_should_replace_controllers_transformer(self, mock_HomogenousTransformer, *args):
        self.setup_mocks(args)
        self.mock_configuration_manager.load.return_value = self.default_config
        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        calibration_api.show_test_pattern('Hilbert Space Filling Curve')

        self.mock_HomogenousTransformer.assert_called_with(
            self.default_config.calibration.max_deflection,
            self.default_config.calibration.height,
            self.default_config.calibration.lower_points,
            self.default_config.calibration.upper_points,
            )

        self.mock_path_to_audio.set_transformer.assert_called_with(self.mock_homogenous_transformer)

    def test_show_line_should_replace_controllers_transformer(self, *args):
        self.setup_mocks(args)
        self.mock_configuration_manager.load.return_value = self.default_config
        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        calibration_api.show_test_pattern('Hilbert Space Filling Curve')
        calibration_api.show_line()

        self.mock_TuningTransformer.assert_called_with(scale=self.default_config.calibration.max_deflection)
        self.mock_path_to_audio.set_transformer.assert_called_with(self.mock_tuning_transformer)

    def test_show_point_should_replace_controllers_transformer(self, *args):
        self.setup_mocks(args)
        self.mock_configuration_manager.load.return_value = self.default_config
        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        calibration_api.show_test_pattern('Hilbert Space Filling Curve')
        calibration_api.show_point()

        self.mock_path_to_audio.set_transformer.assert_called_with(self.mock_tuning_transformer)

    def test_get_largest_object_radius_is_the_smallest_calibration_axis_at_z0(self, *args):
        self.setup_mocks(args)
        config = self.default_config
        expected = 4
        config.calibration.lower_points = {
                (1.0, 1.0): ( 7.0,  7.0),
                (0.0, 1.0): (-7.0,  7.0),
                (1.0, 0.0): ( 7.0, -7.0),
                (0.0, 0.0): (-expected, -7.0)
                }
        self.mock_configuration_manager.load.return_value = config

        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        actual = calibration_api.get_largest_object_radius()
        self.assertEquals(expected, actual)

    def test_get_max_deflection_should_return_max_deflection(self, *args):
        self.setup_mocks(args)
        config = self.default_config
        expected = 0.68
        config.calibration.max_deflection = expected
        self.mock_configuration_manager.load.return_value = config

        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        actual = calibration_api.get_max_deflection()
        self.assertEquals(expected, actual)

    def test_set_max_deflection_should_save_and_update_max_deflection(self, *args):
        self.setup_mocks(args)
        config = self.default_config
        expected_config = self.default_config
        expected = 0.68
        expected_config.calibration.max_deflection = expected
        config.calibration.max_deflection = 0.11
        self.mock_configuration_manager.load.return_value = config
        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        calibration_api.set_max_deflection(expected)

        self.assertConfigurationEqual(expected_config, self.mock_configuration_manager.save.mock_calls[0][1][0])
        self.mock_path_to_audio.set_transformer.assert_called_with(self.mock_tuning_transformer)

    def test_get_laser_offset_should_return_laser_offset(self, *args):
        self.setup_mocks(args)
        config = self.default_config
        expected = [0.01, 0.01]
        config.options.laser_offset = expected
        self.mock_configuration_manager.load.return_value = config

        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        actual = calibration_api.get_laser_offset()
        self.assertEquals(expected, actual)

    def test_set_laser_offset_should_save_and_update_laser_offset(self, *args):
        self.setup_mocks(args)
        config = self.default_config
        expected_config = self.default_config
        expected = [0.01, 0.01]
        expected_config.options.laser_offset = expected
        config.laser_offset = [0.55, 0.55]
        self.mock_configuration_manager.load.return_value = config

        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')
        calibration_api.set_laser_offset(expected)

        self.assertConfigurationEqual(expected_config, self.mock_configuration_manager.save.mock_calls[0][1][0])
        self.mock_micro_disseminator.set_offset.assert_called_with(expected)

    @patch('peachyprinter.api.calibration_api.SquareGenerator')
    def test_show_scale_should_use_Square_Generator_and_Tuning_Transformer(self, mock_SquareGenerator, *args):
        self.setup_mocks(args)
        self.mock_configuration_manager.load.return_value = self.default_config
        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        calibration_api.show_scale()

        self.mock_controller.change_generator.assert_called_with(self.mock_square_generator)
        self.mock_path_to_audio.set_transformer.assert_called_with(self.mock_tuning_transformer)

    def test_set_test_pattern_speed_changes_speeds(self, *args):
        self.setup_mocks(args)

        self.mock_configuration_manager.load.return_value = self.default_config

        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')
        calibration_api.set_test_pattern_speed(150.0)

        self.mock_hilbert_generator.set_speed.assert_called_with(150.0)
        self.mock_square_generator.set_speed.assert_called_with(150.0)
        self.mock_circle_generator.set_speed.assert_called_with(150.0)
        self.mock_spiral_generator.set_speed.assert_called_with(150.0)
        self.mock_memory_hourglass_generator.set_speed.assert_called_with(150.0)

    def test_init_calulates_pattern_radius(self, *args):
        self.setup_mocks(args)

        self.mock_configuration_manager.load.return_value = self.default_config
        CalibrationAPI(self.mock_configuration_manager, 'Spam')

        self.mock_hilbert_generator.set_radius.assert_called_with(40.0)
        self.mock_square_generator.set_radius.assert_called_with(40.0)
        self.mock_circle_generator.set_radius.assert_called_with(40.0)
        self.mock_spiral_generator.set_radius.assert_called_with(40.0)
        self.mock_memory_hourglass_generator.set_radius.assert_called_with(40.0)

    def test_set_orientation_saves_orientation_settings(self, *args):
        self.setup_mocks(args)
        config = self.default_config
        expected_config = self.default_config
        expected_flip_x_axis = True
        expected_flip_y_axis = True
        expected_swap_axis = True

        config.calibration.flip_x_axis = False
        config.calibration.flip_y_axis = False
        config.calibration.swap_axis = False

        expected_config.calibration.flip_x_axis = True
        expected_config.calibration.flip_y_axis = True
        expected_config.calibration.swap_axis = True

        self.mock_configuration_manager.load.return_value = config
        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        calibration_api.set_orientation(expected_flip_x_axis, expected_flip_y_axis, expected_swap_axis)

        self.assertConfigurationEqual(expected_config, self.mock_configuration_manager.save.mock_calls[0][1][0])

    def test_get_orientation_saves_orientation_settings(self, *args):
        self.setup_mocks(args)
        config = self.default_config

        config.calibration.flip_x_axis = True
        config.calibration.flip_y_axis = True
        config.calibration.swap_axis = True

        self.mock_configuration_manager.load.return_value = config
        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        result = calibration_api.get_orientation()

        self.assertEquals(result, (True, True, True))


    def test_set_print_area_saves_print_area_settings(self, *args):
        self.setup_mocks(args)
        config = self.default_config
        expected_config = self.default_config
        expected_print_area_x = 20.0
        expected_print_area_y = 20.0
        expected_print_area_z = 20.0

        config.calibration.print_area_x = 12.0
        config.calibration.print_area_y = 12.0
        config.calibration.print_area_z = 12.0

        expected_config.calibration.print_area_x = 20.0
        expected_config.calibration.print_area_y = 20.0
        expected_config.calibration.print_area_z = 20.0

        self.mock_configuration_manager.load.return_value = config
        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        calibration_api.set_print_area(expected_print_area_x, expected_print_area_y, expected_print_area_z)

        self.assertConfigurationEqual(expected_config, self.mock_configuration_manager.save.mock_calls[0][1][0])

    def test_get_print_area_saves_print_area_settings(self, *args):
        self.setup_mocks(args)
        config = self.default_config

        config.calibration.print_area_x = 20.0
        config.calibration.print_area_y = 20.0
        config.calibration.print_area_z = 20.0

        self.mock_configuration_manager.load.return_value = config
        calibration_api = CalibrationAPI(self.mock_configuration_manager, 'Spam')

        result = calibration_api.get_print_area()

        self.assertEquals(result, (20.0, 20.0, 20.0))

if __name__ == '__main__':
    unittest.main()
