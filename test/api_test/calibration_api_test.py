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
@patch('domain.configuration_manager.ConfigurationManager')
class CalibrationAPITests(unittest.TestCase, test_helpers.TestHelpers):

    def setUp(self):
        pass

    def test_init_creates_a_controller_with_correct_config(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        actual_samples = 7
        mock_configuration_manager = mock_ConfigurationManager.return_value
        mock_configuration_manager.load.return_value = self.DEFAULT_CONFIG
        mock_layer_generator = mock_SinglePointGenerator.return_value
        mock_laser_control = mock_AudioModulationLaserControl.return_value
        mock_audiowriter = mock_AudioWriter.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value

        mock_laser_control.actual_samples_per_second = actual_samples

        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')

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

    def test_stop_should_call_stop_on_controller(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        mock_configuration_manager.load.return_value = self.DEFAULT_CONFIG
        mock_controller = mock_Controller.return_value
        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')

        calibration_api.stop()

        mock_controller.stop.assert_called_with()

        
    def test_should_load_the_correct_printer(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        mock_configuration_manager.load.return_value = self.DEFAULT_CONFIG
        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')

        mock_configuration_manager.load.assert_called_with('Spam')

    def test_show_point_should_set_coordanates_on_Single_Point_Generator(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        mock_configuration_manager.load.return_value = self.DEFAULT_CONFIG
        mock_layer_generator = mock_SinglePointGenerator.return_value
        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')
        x,y,z = 1.0,0.2,1.0

        calibration_api.show_point([x,y,z])

        self.assertEquals([x,y],mock_layer_generator.xy)

    def test_show_point_should_set_coordanates_on_Single_Point_Generator(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        mock_configuration_manager.load.return_value = self.DEFAULT_CONFIG
        mock_layer_generator = mock_SinglePointGenerator.return_value
        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')
        x,y,z = 0.1,1.0,1.0

        calibration_api.show_point([x,y,z])

        self.assertEquals([x,y],mock_layer_generator.xy)

    def test_show_point_should_use_Single_Point_Generator(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        mock_configuration_manager.load.return_value = self.DEFAULT_CONFIG
        mock_layer_generator = mock_SinglePointGenerator.return_value
        mock_controller = mock_Controller.return_value

        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')
        x,y,z = 1.0,0.2,1.0

        calibration_api.show_line()
        calibration_api.show_point([x,y,z])

        mock_controller.change_generator.assert_called_with(mock_layer_generator)

    @patch('api.calibration_api.BlinkGenerator')
    def test_show_blink_should_use_blink_Generator(self, mock_BlinkGenerator, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        mock_configuration_manager.load.return_value = self.DEFAULT_CONFIG
        mock_layer_generator = mock_BlinkGenerator.return_value
        mock_controller = mock_Controller.return_value

        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')
        x,y,z = 1.0,0.2,1.0

        calibration_api.show_line()
        calibration_api.show_blink([x,y,z])

        mock_controller.change_generator.assert_called_with(mock_layer_generator)

    @patch('api.calibration_api.CalibrationLineGenerator')
    def test_show_line_should_use_CalibrationLineGenerator(self, mock_CalibrationLineGenerator,mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        mock_configuration_manager.load.return_value = self.DEFAULT_CONFIG
        mock_layer_generator = mock_CalibrationLineGenerator.return_value
        mock_controller = mock_Controller.return_value

        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')
        x,y,z = 1.0,0.2,1.0

        calibration_api.show_line()

        mock_controller.change_generator.assert_called_with(mock_layer_generator)

    def test_get_patterns_should_return_available_test_patterns(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        mock_configuration_manager.load.return_value = self.DEFAULT_CONFIG
        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')

        patterns = calibration_api.get_test_patterns()

        self.assertEquals(['Circle','Hilbert Space Filling Curve','Spiral','Square'],patterns)

    def test_change_pattern_should_raise_exception_when_test_patterns_unavailable(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        mock_configuration_manager.load.return_value = self.DEFAULT_CONFIG
        mock_layer_generator = mock_SinglePointGenerator.return_value
        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')

        with self.assertRaises(Exception):
            calibration_api.show_test_pattern("Shrubberies")

    @patch('api.calibration_api.HilbertGenerator')
    def test_change_pattern_should_change_pattern_on_controller(self, mock_HilbertGenerator,mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        mock_configuration_manager.load.return_value = self.DEFAULT_CONFIG
        mock_controller = mock_Controller.return_value
        expected_generator = mock_HilbertGenerator.return_value
        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')
        calibration_api.show_test_pattern("Hilbert Space Filling Curve")
        mock_controller.change_generator.assert_called_with(expected_generator)

    def test_current_calibration_returns_the_existing_configuration(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        mock_configuration_manager.load.return_value = self.DEFAULT_CONFIG
        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')

        self.assertEquals(calibration_api.current_calibration(), self.DEFAULT_CONFIG['calibration_data'])

    def test_save_should_save_points(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value

        mock_configuration_manager.load.return_value = dict(self.DEFAULT_CONFIG)
        expected_config = dict(self.DEFAULT_CONFIG)
        data = {
            'height': 1.0 , 
            'lower_points': { 
                (1.0, 1.0):( 1.0,  1.0),
                (0.0, 1.0):(-1.0,  1.0),
                (1.0, 0.0):( 1.0, -1.0),
                (0.0, 0.0):(-1.0, -1.0)
                },
            'upper_points': { 
                (1.0, 1.0):( 1.0,  1.0),
                (0.0, 1.0):(-1.0,  1.0),
                (1.0, 0.0):( 1.0, -1.0),
                (0.0, 0.0):(-1.0, -1.0)
                }
        }
        expected_config['calibration_data'] = data
        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')
        
        calibration_api.save(data)
        actual = calibration_api.current_calibration()

        self.assertEquals(data,actual)
        mock_configuration_manager.save.assert_called_with(expected_config)

    def test_save_should_except_if_invalid_data(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value

        mock_configuration_manager.load.return_value = dict(self.DEFAULT_CONFIG)
        expected_config = dict(self.DEFAULT_CONFIG)
        bad_points = [{'in':[1.0,1.0,0.0], 'out': [50.0,50.0,50.0]}]
        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')

        with self.assertRaises(Exception):
            calibration_api.save(bad_points)

    def test_save_should_except_if_no_height(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value

        mock_configuration_manager.load.return_value = dict(self.DEFAULT_CONFIG)
        config = dict(self.DEFAULT_CONFIG)
        config['calibration_data'] =  {
            'lower_points': { 
                (1.0, 1.0):( 1.0,  1.0),
                (0.0, 1.0):(-1.0,  1.0),
                (1.0, 0.0):( 1.0, -1.0),
                (0.0, 0.0):(-1.0, -1.0)
                },
            'upper_points': { 
                (1.0, 1.0):( 1.0,  1.0),
                (0.0, 1.0):(-1.0,  1.0),
                (1.0, 0.0):( 1.0, -1.0),
                (0.0, 0.0):(-1.0, -1.0)
                }
        }
        mock_configuration_manager.load.return_value = config
        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')

        with self.assertRaises(Exception):
            calibration_api.save(bad_data)

    def test_save_should_except_if_not_enough_points(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        config = dict(self.DEFAULT_CONFIG)
        config['calibration_data'] = {
            'height': 1.0 , 
            'lower_points': { 
                (1.0, 1.0):( 1.0,  1.0),
                (0.0, 1.0):(-1.0,  1.0),
                (1.0, 0.0):( 1.0, -1.0),
                },
            'upper_points': { 
                (1.0, 1.0):( 1.0,  1.0),
                (0.0, 1.0):(-1.0,  1.0),
                (1.0, 0.0):( 1.0, -1.0),
                (0.0, 0.0):(-1.0, -1.0)
                }
        }
        mock_configuration_manager.load.return_value = config
        
        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')

        with self.assertRaises(Exception):
            calibration_api.save(bad_data)

    def test_save_should_except_if_missing_upper(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        config = dict(self.DEFAULT_CONFIG)
        config['calibration_data'] =  {
            'height': 1.0 , 
            'lower_points': { 
                (1.0, 1.0):( 1.0,  1.0),
                (0.0, 1.0):(-1.0,  1.0),
                (1.0, 0.0):( 1.0, -1.0),
                },
        }
        mock_configuration_manager.load.return_value = config
        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')

        with self.assertRaises(Exception):
            calibration_api.save(bad_data)

    @patch('api.calibration_api.HomogenousTransformer')
    def test_show_test_pattern_should_apply_calibration_should_replace_controllers_transformer(self, mock_HomogenousTransformer, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        mock_configuration_manager.load.return_value = self.DEFAULT_CONFIG
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value
        mock_homogenous_transformer = mock_HomogenousTransformer.return_value
        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')

        calibration_api.show_test_pattern('Hilbert Space Filling Curve')

        mock_HomogenousTransformer.assert_called_with(self.DEFAULT_CONFIG['calibration_data'], scale = self.DEFAULT_CONFIG['max_deflection'])
        mock_pathtoaudio.set_transformer.assert_called_with(mock_homogenous_transformer)

    def test_show_line_should_replace_controllers_transformer(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        mock_configuration_manager.load.return_value = self.DEFAULT_CONFIG
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value
        
        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')

        mock_transformer = mock_Transformer.return_value

        calibration_api.show_test_pattern('Hilbert Space Filling Curve')
        calibration_api.show_line()

        mock_Transformer.assert_called_with(scale = self.DEFAULT_CONFIG['max_deflection'])
        mock_pathtoaudio.set_transformer.assert_called_with(mock_transformer)

    def test_show_point_should_replace_controllers_transformer(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        mock_configuration_manager.load.return_value = self.DEFAULT_CONFIG
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value
        
        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')

        mock_transformer = mock_Transformer.return_value

        calibration_api.show_test_pattern('Hilbert Space Filling Curve')
        calibration_api.show_point()

        mock_Transformer.assert_called_with(scale = self.DEFAULT_CONFIG['max_deflection'])
        mock_pathtoaudio.set_transformer.assert_called_with(mock_transformer)

    def test_get_largest_object_radius_is_the_smallest_calibration_axis_at_z0(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        config = dict(self.DEFAULT_CONFIG)
        expected = 4
        config['calibration_data'] =  {
            'lower_points': { 
                (1.0, 1.0):( 7.0,  7.0),
                (0.0, 1.0):(-7.0,  7.0),
                (1.0, 0.0):( 7.0, -7.0),
                (0.0, 0.0):(-expected, -7.0)
                },
            'upper_points': { 
                (1.0, 1.0):( 1.0,  1.0),
                (0.0, 1.0):(-1.0,  1.0),
                (1.0, 0.0):( 1.0, -1.0),
                (0.0, 0.0):(-1.0, -1.0)
                }
        }
        mock_configuration_manager.load.return_value = config

        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')

        actual = calibration_api.get_largest_object_radius()
        self.assertEquals(expected, actual)

    def test_get_max_deflection_should_return_max_deflection(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        config = self.DEFAULT_CONFIG.copy()
        expected = 0.68
        config['max_deflection'] =  expected
        mock_configuration_manager.load.return_value = config

        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')

        actual = calibration_api.get_max_deflection()
        self.assertEquals(expected, actual)

    def test_set_max_deflection_should_save_and_update_max_deflection(self, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        config = self.DEFAULT_CONFIG.copy()
        expected_config = config.copy()
        expected = 0.68
        expected_config['max_deflection'] = expected
        config['max_deflection'] = 0.11
        mock_configuration_manager.load.return_value = config

        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')

        actual = calibration_api.set_max_deflection(expected)
        
        mock_configuration_manager.save.assert_called_with(expected_config)
        mock_pathtoaudio.set_transformer.assert_called_with(mock_transformer)
        
    @patch('api.calibration_api.SquareGenerator')
    def test_show_scale_should_use_Square_Generator_and_Tuning_Transformer(self, mock_SquareGenerator, mock_ConfigurationManager,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
        mock_configuration_manager = mock_ConfigurationManager.return_value
        mock_squaregenerator = mock_SquareGenerator.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_configuration_manager.load.return_value = self.DEFAULT_CONFIG
        mock_controller = mock_Controller.return_value

        calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')

        calibration_api.show_scale()
        
        mock_controller.change_generator.assert_called_with(mock_squaregenerator)
        mock_pathtoaudio.set_transformer.assert_called_with(mock_transformer)

    # def test_get_calibration_points_returns_pattern_if_the_existing_configuration_empty(self,mock_SinglePointGenerator,mock_AudioModulationLaserControl,mock_AudioWriter,mock_Transformer,mock_PathToAudio,mock_Controller):
    #     calibration_api = CalibrationAPI(mock_configuration_manager,'Spam')
    #     expected
    #     self.assertEquals(calibration_api.get_calibration_points(), [])


if __name__ == '__main__':
    unittest.main()