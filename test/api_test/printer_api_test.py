import unittest
import os
import sys
from StringIO import StringIO

from mock import patch

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from domain.configuration_manager import ConfigurationManager
from api.print_api import PrintAPI
import test_helpers


class PrintAPITests(unittest.TestCase, test_helpers.TestHelpers):

    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.AudioDripZAxis')
    @patch('api.print_api.SubLayerGenerator')
    @patch('api.print_api.NullCommander')
    def test_print_gcode_should_create_required_classes_and_start_it(self,
            mock_NullCommander,
            mock_SubLayerGenerator, 
            mock_AudioDripZAxis,
            mock_AudioModulationLaserControl,
            mock_GCodeReader,
            mock_AudioWriter,
            mock_Transformer,
            mock_PathToAudio,
            mock_Controller,
            ):
        gcode_path = "FakeFile"
        actual_samples_per_second = 7
        fake_layers = "Fake Layers"
        mock_nullcommander = mock_NullCommander.return_value
        mock_dripbasedzaxis = mock_AudioDripZAxis.return_value
        mock_audiomodulationlasercontrol = mock_AudioModulationLaserControl.return_value
        mock_gcodereader = mock_GCodeReader.return_value
        mock_sublayergenerator = mock_SubLayerGenerator.return_value
        mock_audiowriter = mock_AudioWriter.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value

        mock_audiomodulationlasercontrol.actual_samples_per_second = actual_samples_per_second
        mock_gcodereader.get_layers.return_value = fake_layers

        config = self.default_config

        api = PrintAPI(config)
        api.print_gcode(gcode_path)

        mock_SubLayerGenerator.assert_called_with(
            fake_layers,
            config.options.sublayer_height_mm
            )

        mock_AudioDripZAxis.assert_called_with(
            config.dripper.drips_per_mm,
            config.audio.input.sample_rate,
            config.audio.input.bit_depth,
            mock_nullcommander,
            config.serial.on_command,
            config.serial.off_command
            )
        mock_AudioModulationLaserControl.assert_called_with(
            config.audio.output.sample_rate,
            config.audio.output.modulation_on_frequency,
            config.audio.output.modulation_off_frequency,
            config.options.laser_offset
            )
        mock_GCodeReader.assert_called_with(
            gcode_path, 
            scale = config.options.scaling_factor
            )
        mock_AudioWriter.assert_called_with(
            config.audio.output.sample_rate,
            config.audio.output.bit_depth,
            )
        mock_Transformer.assert_called_with(
            config.calibration.max_deflection,
            config.calibration.height,
            config.calibration.lower_points,
            config.calibration.upper_points,
            )
        mock_PathToAudio.assert_called_with(
            actual_samples_per_second,
            mock_transformer, 
            config.options.laser_thickness_mm
            )
        mock_Controller.assert_called_with(
            mock_audiomodulationlasercontrol,
            mock_pathtoaudio,
            mock_audiowriter,
            mock_sublayergenerator,
            zaxis = mock_dripbasedzaxis,
            status_call_back = None,
            max_lead_distance = config.dripper.max_lead_distance_mm,
            abort_on_error = True,
            max_speed = config.options.draw_speed
            )

    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.AudioDripZAxis')
    @patch('api.print_api.SubLayerGenerator')
    def test_verify_gcode_should_create_required_classes_and_start_it_and_return_errors(self,
            mock_SubLayerGenerator, 
            mock_AudioDripZAxis,
            mock_AudioModulationLaserControl,
            mock_GCodeReader,
            mock_AudioWriter,
            mock_Transformer,
            mock_PathToAudio,
            mock_Controller,
            ):
        gcode_path = "FakeFile"
        actual_samples_per_second = 7
        fake_layers = "Fake Layers"
        mock_dripbasedzaxis = mock_AudioDripZAxis.return_value
        mock_audiomodulationlasercontrol = mock_AudioModulationLaserControl.return_value
        mock_gcodereader = mock_GCodeReader.return_value
        mock_audiowriter = mock_AudioWriter.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value
        expected_errors = ['Some Error']
        mock_controller.get_status.return_value = {'errors':expected_errors}

        mock_audiomodulationlasercontrol.actual_samples_per_second = actual_samples_per_second
        mock_gcodereader.get_layers.return_value = fake_layers

        config = self.default_config
        api = PrintAPI(config)
        api.verify_gcode(gcode_path)

        self.assertEquals(0, mock_AudioDripZAxis.call_count)
        mock_AudioModulationLaserControl.assert_called_with(
            config.audio.output.sample_rate,
            config.audio.output.modulation_on_frequency,
            config.audio.output.modulation_off_frequency,
            config.options.laser_offset
            )
        mock_GCodeReader.assert_called_with(
            gcode_path,
            scale = config.options.scaling_factor
            )

        self.assertEquals(0, mock_AudioWriter.call_count)

        mock_Transformer.assert_called_with(
            config.calibration.max_deflection,
            config.calibration.height,
            config.calibration.lower_points,
            config.calibration.upper_points,
            )
        mock_PathToAudio.assert_called_with(
            actual_samples_per_second,
            mock_transformer, 
            config.options.laser_thickness_mm
            )
        mock_Controller.assert_called_with(
            mock_audiomodulationlasercontrol,
            mock_pathtoaudio,
            None,
            fake_layers,
            zaxis = None,
            status_call_back = None,
            max_lead_distance = config.dripper.max_lead_distance_mm,
            abort_on_error = False,
            max_speed = config.options.draw_speed
            )

    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.AudioDripZAxis')
    @patch('api.print_api.SubLayerGenerator')
    def test_print_gcode_should_not_print_sublayers_if_option_flase(self,
            mock_SubLayerGenerator, 
            mock_AudioDripZAxis,
            mock_AudioModulationLaserControl,
            mock_GCodeReader,
            mock_AudioWriter,
            mock_Transformer,
            mock_PathToAudio,
            mock_Controller,
            ):
        gcode_path = "FakeFile"
        actual_samples_per_second = 7
        fake_layers = "Fake Layers"
        mock_dripbasedzaxis = mock_AudioDripZAxis.return_value
        mock_audiomodulationlasercontrol = mock_AudioModulationLaserControl.return_value
        mock_gcodereader = mock_GCodeReader.return_value
        mock_sublayergenerator = mock_SubLayerGenerator.return_value
        mock_audiowriter = mock_AudioWriter.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value
        mock_audiomodulationlasercontrol.actual_samples_per_second = actual_samples_per_second
        mock_gcodereader.get_layers.return_value = fake_layers

        api = PrintAPI(self.default_config)
        api.print_gcode(gcode_path, print_sub_layers = False)

        mock_Controller.assert_called_with(
            mock_audiomodulationlasercontrol,
            mock_pathtoaudio,
            mock_audiowriter,
            fake_layers,
            zaxis = mock_dripbasedzaxis,
            status_call_back = None,
            max_lead_distance = self.default_config.dripper.max_lead_distance_mm,
            abort_on_error = True,
        max_speed = self.default_config.options.draw_speed
            )

    def test_print_can_be_stopped_before_started(self):
        api = PrintAPI(self.default_config)
        api.close()

    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.AudioDripZAxis')
    def test_get_status_calls_controller_status(self, 
            mock_AudioDripZAxis,
            mock_AudioModulationLaserControl,
            mock_GCodeReader,
            mock_AudioWriter,
            mock_Transformer,
            mock_PathToAudio,
            mock_Controller,):
        mock_audiomodulationlasercontrol = mock_AudioModulationLaserControl.return_value
        mock_audiomodulationlasercontrol.actual_samples_per_second = 7
        mock_controller = mock_Controller.return_value


        api = PrintAPI(self.default_config)
        api.print_gcode("Spam")
        api.get_status()

        mock_controller.get_status.assert_called_with()

    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.AudioDripZAxis')
    @patch('api.print_api.SubLayerGenerator')
    @patch('api.print_api.SerialCommander')
    def test_print_gcode_should_create_serial_commander_if_specified_in_config(self,
            mock_SerialCommander,
            mock_SubLayerGenerator, 
            mock_AudioDripZAxis,
            mock_AudioModulationLaserControl,
            mock_GCodeReader,
            mock_AudioWriter,
            mock_Transformer,
            mock_PathToAudio,
            mock_Controller,
            ):
        gcode_path = "FakeFile"
        actual_samples_per_second = 7
        fake_layers = "Fake Layers"
        mock_serialcommander = mock_SerialCommander.return_value
        mock_dripbasedzaxis = mock_AudioDripZAxis.return_value
        mock_audiomodulationlasercontrol = mock_AudioModulationLaserControl.return_value
        mock_gcodereader = mock_GCodeReader.return_value
        mock_sublayergenerator = mock_SubLayerGenerator.return_value
        mock_audiowriter = mock_AudioWriter.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value

        mock_audiomodulationlasercontrol.actual_samples_per_second = actual_samples_per_second
        mock_gcodereader.get_layers.return_value = fake_layers

        config = self.default_config
        config.serial.on = True
        config.serial.port = "COM6"
        config.serial.on_command = "ON"
        config.serial.off_command = "OFF"
        api = PrintAPI(config)
        api.print_gcode(gcode_path)

        mock_SerialCommander.assert_called_with("COM6")
        mock_AudioDripZAxis.assert_called_with(
            config.dripper.drips_per_mm,
            config.audio.input.sample_rate,
            config.audio.input.bit_depth,
            mock_serialcommander,
            config.serial.on_command,
            config.serial.off_command
            )
        mock_Controller.assert_called_with(
            mock_audiomodulationlasercontrol,
            mock_pathtoaudio,
            mock_audiowriter,
            mock_sublayergenerator,
            zaxis = mock_dripbasedzaxis,
            status_call_back = None,
            max_lead_distance = config.dripper.max_lead_distance_mm,
            abort_on_error = True,
            max_speed = config.options.draw_speed
        )


    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.TimedDripZAxis')
    @patch('api.print_api.SubLayerGenerator')
    def test_print_gcode_should_use_specified_dripper_if_specified_in_config(self,
            mock_SubLayerGenerator, 
            mock_TimedDripZAxis,
            mock_AudioModulationLaserControl,
            mock_GCodeReader,
            mock_AudioWriter,
            mock_Transformer,
            mock_PathToAudio,
            mock_Controller,
            ):
        gcode_path = "FakeFile"
        actual_samples_per_second = 7
        fake_layers = "Fake Layers"
        mock_timeddripzaxis = mock_TimedDripZAxis.return_value
        mock_audiomodulationlasercontrol = mock_AudioModulationLaserControl.return_value
        mock_gcodereader = mock_GCodeReader.return_value
        mock_sublayergenerator = mock_SubLayerGenerator.return_value
        mock_audiowriter = mock_AudioWriter.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value

        mock_audiomodulationlasercontrol.actual_samples_per_second = actual_samples_per_second
        mock_gcodereader.get_layers.return_value = fake_layers

        config = self.default_config
        config.dripper.dripper_type = 'emulated'
        api = PrintAPI(config)
        api.print_gcode(gcode_path)

        mock_TimedDripZAxis.assert_called_with(config.dripper.drips_per_mm, drips_per_second = config.dripper.emulated_drips_per_second )
        mock_Controller.assert_called_with(
            mock_audiomodulationlasercontrol,
            mock_pathtoaudio,
            mock_audiowriter,
            mock_sublayergenerator,
            zaxis = mock_timeddripzaxis,
            status_call_back = None,
            max_lead_distance = config.dripper.max_lead_distance_mm,
            abort_on_error = True,
            max_speed = config.options.draw_speed
        )

    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.AudioDripZAxis')
    @patch('api.print_api.SubLayerGenerator')
    def test_set_drips_per_second_throws_error_if_not_using_emulated_drips(self,
            mock_SubLayerGenerator, 
            mock_AudioDripZAxis,
            mock_AudioModulationLaserControl,
            mock_GCodeReader,
            mock_AudioWriter,
            mock_Transformer,
            mock_PathToAudio,
            mock_Controller,
            ):
        gcode_path = "FakeFile"

        mock_audiodripzaxis = mock_AudioDripZAxis.return_value
        mock_audiodripzaxis.set_drips_per_second.side_effect = Exception()

        config = self.default_config

        api = PrintAPI(config)
        api.print_gcode(gcode_path)

        with self.assertRaises(Exception):
            api.set_drips_per_second(12)

    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.TimedDripZAxis')
    @patch('api.print_api.SubLayerGenerator')
    def test_get_and_set_drips_per_second(self,
            mock_SubLayerGenerator, 
            mock_TimedDripZAxis,
            mock_AudioModulationLaserControl,
            mock_GCodeReader,
            mock_AudioWriter,
            mock_Transformer,
            mock_PathToAudio,
            mock_Controller,
            ):
        gcode_path = "FakeFile"
        expected_drips_per_second = 12
        mock_timeddripzaxis = mock_TimedDripZAxis.return_value
        mock_timeddripzaxis.get_drips_per_second.return_value = expected_drips_per_second
        
        config = self.default_config
        config.dripper.dripper_type = 'emulated'
        api = PrintAPI(config)
        api.print_gcode(gcode_path)


        mock_TimedDripZAxis.assert_called_with(config.dripper.drips_per_mm, drips_per_second = config.dripper.emulated_drips_per_second)
        self.assertTrue(api.can_set_drips_per_second())
        api.set_drips_per_second(expected_drips_per_second)
        self.assertEquals(expected_drips_per_second, api.get_drips_per_second())

        mock_timeddripzaxis.set_drips_per_second.assert_called_with(expected_drips_per_second)

if __name__ == '__main__':
    unittest.main()