import unittest
import os
import sys
from mock import patch

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

import test_helpers
from api.calibration_api import CalibrationAPI

@patch('api.calibration_api.Controller')
@patch('api.calibration_api.PathToAudio')
@patch('api.calibration_api.TuningTransformer')
@patch('api.calibration_api.AudioWriter')
@patch('api.calibration_api.AudioModulationLaserControl')
@patch('api.calibration_api.SinglePointGenerator')
class CalibrationAPITests(unittest.TestCase, test_helpers.TestHelpers):
    def test_start_creates_a_controller_with_correct_config(self, mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        actual_samples = 7
        mock_layer_generator = mock_SinglePointGenerator.return_value
        mock_laser_control = mock_AudioModulationLaserControl.return_value
        mock_audiowriter = mock_AudioWriter.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value

        mock_laser_control.actual_samples_per_second = actual_samples

        calibration_api = CalibrationAPI(self.DEFAULT_CONFIG)

        mock_SinglePointGenerator.assert_called_with()
        mock_AudioModulationLaserControl.assert_called_with(
            self.DEFAULT_CONFIG['output_sample_frequency'],
            self.DEFAULT_CONFIG['on_modulation_frequency'],
            self.DEFAULT_CONFIG['off_modulation_frequency']
            )
        mock_Transformer.assert_called_with(
            scale = self.DEFAULT_CONFIG['max_deflection']
            )
        mock_PathToAudio.assert_called_with(
            actual_samples,
            mock_transformer,
            self.DEFAULT_CONFIG['laser_thickness_mm']
            )

        calibration_api.start()

        mock_AudioWriter.assert_called_with(
            self.DEFAULT_CONFIG['output_sample_frequency'],
            self.DEFAULT_CONFIG['output_bit_depth']
            )
        mock_Controller.assert_called_with(
            mock_laser_control,
            mock_pathtoaudio,
            mock_audiowriter,
            mock_layer_generator
            )

    def test_stop_should_throw_exception_when_controller_not_running(self,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        calibration_api = CalibrationAPI(self.DEFAULT_CONFIG)
        with self.assertRaises(Exception):
            calibration_api.stop()

    def test_stop_should_not_throw_exception_when_controller_running(self,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        calibration_api = CalibrationAPI(self.DEFAULT_CONFIG)
        calibration_api.start()
        calibration_api.stop()
        
    def test_move_to_should_set_coordanates_on_Single_Point_Generator(self,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_layer_generator = mock_SinglePointGenerator.return_value
        calibration_api = CalibrationAPI(self.DEFAULT_CONFIG)
        x,y,z = 1.0,1.0,1.0

        calibration_api.move_to([x,y,z])

        self.assertEquals([x,y],mock_layer_generator.xy)

    def test_move_to_should_set_coordanates_on_Single_Point_Generator(self,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_layer_generator = mock_SinglePointGenerator.return_value
        calibration_api = CalibrationAPI(self.DEFAULT_CONFIG)
        x,y,z = 1.0,1.0,1.0

        calibration_api.move_to([x,y,z])

        self.assertEquals([x,y],mock_layer_generator.xy)

    def test_get_patterns_should_return_available_test_patterns(self,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_layer_generator = mock_SinglePointGenerator.return_value
        calibration_api = CalibrationAPI(self.DEFAULT_CONFIG)

        patterns = calibration_api.get_patterns()

        self.assertEquals(['Hilbert Space filling','Single Point','Grid Alignment Line'],patterns)

    def test_change_pattern_should_raise_exception_when_test_patterns_unavailable(self,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_layer_generator = mock_SinglePointGenerator.return_value
        calibration_api = CalibrationAPI(self.DEFAULT_CONFIG)
        calibration_api.start()

        with self.assertRaises(Exception):
            calibration_api.change_pattern("Shrubberies")

    @patch('api.calibration_api.CalibrationLineGenerator')
    def test_change_pattern_should_change_pattern_on_controller(self,mock_CalibrationLineGenerator,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_controller = mock_Controller.return_value
        expected_generator = mock_CalibrationLineGenerator.return_value
        calibration_api = CalibrationAPI(self.DEFAULT_CONFIG)
        calibration_api.start()
        calibration_api.change_pattern("Grid Alignment Line")
        mock_controller.change_generator.assert_called_with(expected_generator)

    def test_get_calibration_points_returns_the_existing_configuration(self,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        calibration_api = CalibrationAPI(self.DEFAULT_CONFIG)

        self.assertEquals(calibration_api.get_calibration_points(), [])

    def test_get_calibration_scale_returns_the_existing_scale_used_for_calibration(self,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        calibration_api = CalibrationAPI(self.DEFAULT_CONFIG)

        self.assertEquals(calibration_api.get_calibration_scale(), 1.0)

    # def test_get_calibration_points_returns_pattern_if_the_existing_configuration_empty(self,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
    #     calibration_api = CalibrationAPI(self.DEFAULT_CONFIG)
    #     expected
    #     self.assertEquals(calibration_api.get_calibration_points(), [])


if __name__ == '__main__':
    unittest.main()