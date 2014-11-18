import unittest
import os
import sys
import time
from StringIO import StringIO

from mock import patch, mock_open, MagicMock

import logging

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from domain.configuration_manager import ConfigurationManager
from api.print_api import PrintAPI, PrintQueueAPI
from infrastructure.layer_generators import ShuffleGenerator,SubLayerGenerator,OverLapGenerator,StubLayerGenerator
import test_helpers


class PrintQueueAPITests(unittest.TestCase, test_helpers.TestHelpers):

    def setUp(self):
        self.call_backs = []

    def call_back(self, call_back):
        self.call_backs.append(call_back)

    @patch.object(os.path, 'isdir')
    def test_print_folder_should_raise_exception_when_folder_is_empty(self, mock_isdir):
        folder = os.path.join('SomthingMadeUp')
        mock_isdir.return_value = False

        with self.assertRaises(Exception):
            api = PrintQueueAPI(self.default_config)
            api.print_folder(folder)

        mock_isdir.assert_called_with(folder)

    @patch.object(os.path, 'isdir')
    @patch.object(os, 'listdir')
    def test_print_folder_should_raise_exception_when_no_files(self, mock_listdir, mock_isdir):
        folder = os.path.join('','SomthingMadeUp')
        mock_isdir.return_value = True
        mock_listdir.return_value = []
        with patch('api.print_api.listdir', return_value= []):
            with self.assertRaises(Exception):
                api = PrintQueueAPI(self.default_config)
                api.print_folder(folder)

    @patch.object(os.path, 'isdir')
    def test_print_folder_should_raise_exception_when_no_gcode_files(self,  mock_isdir):
        folder = os.path.join('','SomthingMadeUp')
        mock_isdir.return_value = True
        with patch('api.print_api.listdir', return_value= ['ASDFAS.txt','bor.fa']):
            with self.assertRaises(Exception):
                api = PrintQueueAPI(self.default_config)
                api.print_folder(folder)

    @patch.object(os.path, 'isdir')
    @patch.object(PrintAPI, 'print_gcode')
    def test_print_folder_should_call_print_api_for_gcode_files(self, mock_print_gcode, mock_isdir):
        folder = os.path.join('','SomthingMadeUp')
        expected_file = 'thingy.gcode'
        expected_path = os.path.join(folder,expected_file)
        mock_isdir.return_value = True
        with patch('api.print_api.listdir', return_value= [ 'ASDFAS.txt', 'bor.fa', expected_file ]): 
            api = PrintQueueAPI(self.default_config)
            api.print_folder(folder)
        mock_print_gcode.assert_called_with(expected_path)

    @patch.object(os.path, 'isdir')
    @patch('api.print_api.PrintAPI')
    def test_print_folder_should_call_print_api_for_each_gcode_files_after_layer_complete(self, mock_PrintAPI, mock_isdir):
        folder = os.path.join('','SomthingMadeUp')
        expected_file1 = 'thingy1.gcode'
        expected_file2 = 'thingy2.gcode'
        expected_path1 = os.path.join(folder,expected_file1)
        expected_path2 = os.path.join(folder,expected_file2)
        mock_isdir.return_value = True
        mock_print_api = mock_PrintAPI.return_value
        with patch('api.print_api.listdir', return_value= [ 'ASDFAS.txt', 'bor.fa', expected_file1, expected_file2 ]): 
            api = PrintQueueAPI(self.default_config)
            api.print_folder(folder)
            mock_print_api.print_gcode.assert_called_with(expected_path1)
            call_back = mock_PrintAPI.call_args[0][1]
            mock_status = { 'status':'Complete' }
            call_back(mock_status)
            mock_print_api.print_gcode.assert_called_with(expected_path2)

    @patch.object(os.path, 'isdir')
    @patch('api.print_api.PrintAPI')
    def test_print_folder_should_close_api_before_opening_new_one(self, mock_PrintAPI, mock_isdir):
        folder = os.path.join('','SomthingMadeUp')
        expected_file1 = 'thingy1.gcode'
        expected_file2 = 'thingy2.gcode'
        mock_isdir.return_value = True
        mock_print_api = mock_PrintAPI.return_value
        with patch('api.print_api.listdir', return_value= [ 'ASDFAS.txt', 'bor.fa', expected_file1, expected_file2 ]): 
            api = PrintQueueAPI(self.default_config)
            api.print_folder(folder)
            call_back = mock_PrintAPI.call_args[0][1]
            mock_status = { 'status':'Complete' }
            call_back(mock_status)
            mock_print_api.close.assert_called_with()

    @patch.object(os.path, 'isdir')
    @patch('api.print_api.PrintAPI')
    def test_print_folder_should_be_interuptable(self, mock_PrintAPI, mock_isdir):
        folder = os.path.join('','SomthingMadeUp')
        expected_file1 = 'thingy1.gcode'
        expected_file2 = 'thingy2.gcode'
        mock_isdir.return_value = True
        mock_print_api = mock_PrintAPI.return_value
        with patch('api.print_api.listdir', return_value= [ 'ASDFAS.txt', 'bor.fa', expected_file1, expected_file2 ]): 
            api = PrintQueueAPI(self.default_config)
            api.print_folder(folder)
            api.close()
            mock_print_api.close.assert_called_with()
            self.assertEquals(1, mock_PrintAPI.call_count)

    @patch.object(os.path, 'isdir')
    @patch('api.print_api.PrintAPI')
    def test_print_folder_ends_smoothly(self, mock_PrintAPI, mock_isdir):
        folder = os.path.join('','SomthingMadeUp')
        expected_file1 = 'thingy1.gcode'
        mock_isdir.return_value = True
        mock_print_api = mock_PrintAPI.return_value
        with patch('api.print_api.listdir', return_value= [ 'ASDFAS.txt', 'bor.fa', expected_file1 ]): 
            api = PrintQueueAPI(self.default_config)
            api.print_folder(folder)
            call_back = mock_PrintAPI.call_args[0][1]
            mock_status = { 'status':'Complete' }
            call_back(mock_status)

    @patch.object(os.path, 'isdir')
    @patch('api.print_api.PrintAPI')
    def test_print_folder_should_call_back_when_called_back(self, mock_PrintAPI, mock_isdir):
        folder = os.path.join('','SomthingMadeUp')
        expected_file1 = 'thingy1.gcode'
        mock_isdir.return_value = True
        mock_print_api = mock_PrintAPI.return_value
        with patch('api.print_api.listdir', return_value= [ 'ASDFAS.txt', 'bor.fa', expected_file1 ]): 
            api = PrintQueueAPI(self.default_config, self.call_back)
            api.print_folder(folder)
            call_back = mock_PrintAPI.call_args[0][1]
            mock_status = { 'status':'Complete' }
            call_back(mock_status)
            self.assertEqual(1, len(self.call_backs))
            self.assertEqual(mock_status, self.call_backs[0])

    @patch.object(os.path, 'isdir')
    @patch('api.print_api.PrintAPI')
    def test_print_folder_should_delay_between_prints(self, mock_PrintAPI, mock_isdir):
        folder = os.path.join('','SomthingMadeUp')
        expected_file1 = 'thingy1.gcode'
        expected_file2 = 'thingy2.gcode'
        expected_delay = 0.1
        mock_isdir.return_value = True
        mock_print_api = mock_PrintAPI.return_value
        config = self.default_config
        config.options.print_queue_delay = expected_delay
        with patch('api.print_api.listdir', return_value= [ 'ASDFAS.txt', 'bor.fa', expected_file1, expected_file2 ]): 
            api = PrintQueueAPI(config)
            api.print_folder(folder)
            self.assertEquals(1, mock_PrintAPI.call_count)
            call_back = mock_PrintAPI.call_args[0][1]
            start = time.time()
            mock_status = { 'status':'Complete' }
            call_back(mock_status)
            call_back(mock_status)
            end = time.time()
            self.assertTrue(expected_delay <=  end-start)


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
    @patch('api.print_api.ShuffleGenerator') 
    def test_print_gcode_should_create_required_classes_and_start_it(self,
            mock_ShuffleGenerator,
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
        mock_audiowriter = mock_AudioWriter.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value

        mock_audiomodulationlasercontrol.actual_samples_per_second = actual_samples_per_second
        mock_gcodereader.get_layers.return_value = fake_layers

        config = self.default_config
        config.options.use_shufflelayers = False
        config.options.use_sublayers = False
        config.options.use_overlap = False
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)
            mock_GCodeReader.assert_called_with(
            m.return_value,
            scale = config.options.scaling_factor
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
            fake_layers,
            zaxis = mock_dripbasedzaxis,
            status_call_back = None,
            max_lead_distance = config.dripper.max_lead_distance_mm,
            abort_on_error = True,
            override_speed = config.cure_rate.draw_speed,
            commander = mock_nullcommander,
            layer_start_command = config.serial.layer_started,
            layer_ended_command = config.serial.layer_ended,
            print_ended_command = config.serial.print_ended,
            pre_layer_delay = None
            )

    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.AudioDripZAxis')
    @patch('api.print_api.SubLayerGenerator')
    @patch('api.print_api.NullCommander')
    @patch('api.print_api.ShuffleGenerator') 
    def test_print_gcode_should_create_required_classes_and_start_it_with_pre_layer_delay(self,
            mock_ShuffleGenerator,
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
        mock_audiowriter = mock_AudioWriter.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value

        mock_audiomodulationlasercontrol.actual_samples_per_second = actual_samples_per_second
        mock_gcodereader.get_layers.return_value = fake_layers

        config = self.default_config
        config.options.use_shufflelayers = False
        config.options.use_sublayers = False
        config.options.use_overlap = False
        config.options.pre_layer_delay = 1.0
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)
            mock_GCodeReader.assert_called_with(
            m.return_value,
            scale = config.options.scaling_factor
            )

        mock_Controller.assert_called_with(
            mock_audiomodulationlasercontrol,
            mock_pathtoaudio,
            mock_audiowriter,
            fake_layers,
            zaxis = mock_dripbasedzaxis,
            status_call_back = None,
            max_lead_distance = config.dripper.max_lead_distance_mm,
            abort_on_error = True,
            override_speed = config.cure_rate.draw_speed,
            commander = mock_nullcommander,
            layer_start_command = config.serial.layer_started,
            layer_ended_command = config.serial.layer_ended,
            print_ended_command = config.serial.print_ended,
            pre_layer_delay = 1.0
            )

    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.AudioDripZAxis')
    @patch('api.print_api.SubLayerGenerator')
    @patch('api.print_api.NullCommander')
    @patch('api.print_api.ShuffleGenerator') 
    def test_print_gcode_should_create_required_classes_and_start_it_without_override_speed(self,
            mock_ShuffleGenerator,
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
        mock_audiowriter = mock_AudioWriter.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value

        mock_audiomodulationlasercontrol.actual_samples_per_second = actual_samples_per_second
        mock_gcodereader.get_layers.return_value = fake_layers

        config = self.default_config
        config.options.use_shufflelayers = False
        config.options.use_sublayers = False
        config.options.use_overlap = False
        config.cure_rate.use_draw_speed = False
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)
            mock_GCodeReader.assert_called_with(
            m.return_value,
            scale = config.options.scaling_factor
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
            fake_layers,
            zaxis = mock_dripbasedzaxis,
            status_call_back = None,
            max_lead_distance = config.dripper.max_lead_distance_mm,
            abort_on_error = True,
            override_speed = None,
            commander = mock_nullcommander,
            layer_start_command = config.serial.layer_started,
            layer_ended_command = config.serial.layer_ended,
            print_ended_command = config.serial.print_ended,
            pre_layer_delay = None
            )

    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.AudioDripZAxis')
    @patch('api.print_api.SubLayerGenerator')
    @patch('api.print_api.NullCommander')
    def test_verify_gcode_should_create_required_classes_and_start_it_and_return_errors(self,
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
        mock_dripbasedzaxis = mock_AudioDripZAxis.return_value
        mock_nullcommander = mock_NullCommander.return_value
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
        config.options.use_shufflelayers = False
        config.options.use_sublayers = False
        config.options.use_overlap = False

        api = PrintAPI(config)
        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.verify_gcode(gcode_path)
            mock_GCodeReader.assert_called_with(
            m.return_value,
            scale = config.options.scaling_factor
            )

        self.assertEquals(0, mock_AudioDripZAxis.call_count)
        mock_AudioModulationLaserControl.assert_called_with(
            config.audio.output.sample_rate,
            config.audio.output.modulation_on_frequency,
            config.audio.output.modulation_off_frequency,
            config.options.laser_offset
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
            override_speed = config.cure_rate.draw_speed,
            commander = mock_nullcommander,
            layer_start_command = config.serial.layer_started,
            layer_ended_command = config.serial.layer_ended,
            print_ended_command = config.serial.print_ended,
            pre_layer_delay = None
            )

    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.AudioDripZAxis')
    @patch('api.print_api.SubLayerGenerator')
    @patch('api.print_api.NullCommander')
    def test_print_gcode_should_not_print_sublayers_if_option_flase(self,
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
        config = self.default_config
        gcode_path = "FakeFile"
        actual_samples_per_second = 7
        fake_layers = "Fake Layers"
        mock_dripbasedzaxis = mock_AudioDripZAxis.return_value
        mock_audiomodulationlasercontrol = mock_AudioModulationLaserControl.return_value
        mock_nullcommander = mock_NullCommander.return_value
        mock_gcodereader = mock_GCodeReader.return_value
        mock_sublayergenerator = mock_SubLayerGenerator.return_value
        mock_audiowriter = mock_AudioWriter.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value
        mock_audiomodulationlasercontrol.actual_samples_per_second = actual_samples_per_second
        mock_gcodereader.get_layers.return_value = fake_layers

        config.options.use_shufflelayers = False
        config.options.use_sublayers = False
        config.options.use_overlap = False

        api = PrintAPI(config)
        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
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
            override_speed = self.default_config.cure_rate.draw_speed,
            commander = mock_nullcommander,
            layer_start_command = config.serial.layer_started,
            layer_ended_command = config.serial.layer_ended,
            print_ended_command = config.serial.print_ended,
            pre_layer_delay = None
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
        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
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
    @patch('api.print_api.ShuffleGenerator')
    def test_print_gcode_should_create_serial_commander_if_specified_in_config(self,
            mock_ShuffleGenerator,
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
        config.options.use_shufflelayers = False
        config.options.use_sublayers = False
        config.options.use_overlap = False
        api = PrintAPI(config)
        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
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
            fake_layers,
            zaxis = mock_dripbasedzaxis,
            status_call_back = None,
            max_lead_distance = config.dripper.max_lead_distance_mm,
            abort_on_error = True,
            override_speed = config.cure_rate.draw_speed,
            commander = mock_serialcommander,
            layer_start_command = config.serial.layer_started,
            layer_ended_command = config.serial.layer_ended,
            print_ended_command = config.serial.print_ended,
            pre_layer_delay = None
        )


    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.TimedDripZAxis')
    @patch('api.print_api.SubLayerGenerator')
    @patch('api.print_api.NullCommander')
    @patch('api.print_api.ShuffleGenerator')
    def test_print_gcode_should_use_emulated_dripper_if_specified_in_config(self,
            mock_ShuffleGenerator,
            mock_NullCommander,
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
        mock_nullcommander = mock_NullCommander.return_value
        mock_gcodereader = mock_GCodeReader.return_value
        mock_audiowriter = mock_AudioWriter.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value

        mock_audiomodulationlasercontrol.actual_samples_per_second = actual_samples_per_second
        mock_gcodereader.get_layers.return_value = fake_layers

        config = self.default_config

        config.dripper.dripper_type = 'emulated'
        config.options.use_shufflelayers = False
        config.options.use_sublayers = False
        config.options.use_overlap = False
        
        api = PrintAPI(config)
        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)

        mock_TimedDripZAxis.assert_called_with(config.dripper.drips_per_mm, drips_per_second = config.dripper.emulated_drips_per_second )
        mock_Controller.assert_called_with(
            mock_audiomodulationlasercontrol,
            mock_pathtoaudio,
            mock_audiowriter,
            fake_layers,
            zaxis = mock_timeddripzaxis,
            status_call_back = None,
            max_lead_distance = config.dripper.max_lead_distance_mm,
            abort_on_error = True,
            override_speed = config.cure_rate.draw_speed,
            commander = mock_nullcommander,
            layer_start_command = config.serial.layer_started,
            layer_ended_command = config.serial.layer_ended,
            print_ended_command = config.serial.print_ended,
            pre_layer_delay = None
            )


    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.PhotoZAxis')
    @patch('api.print_api.SubLayerGenerator')
    @patch('api.print_api.NullCommander')
    @patch('api.print_api.ShuffleGenerator')
    def test_print_gcode_should_use_photo_zaxis_if_specified_in_config(self,
            mock_ShuffleGenerator,
            mock_NullCommander,
            mock_SubLayerGenerator, 
            mock_PhotoZAxis,
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
        mock_photozaxis = mock_PhotoZAxis.return_value
        mock_audiomodulationlasercontrol = mock_AudioModulationLaserControl.return_value
        mock_nullcommander = mock_NullCommander.return_value
        mock_gcodereader = mock_GCodeReader.return_value
        mock_audiowriter = mock_AudioWriter.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value

        mock_audiomodulationlasercontrol.actual_samples_per_second = actual_samples_per_second
        mock_gcodereader.get_layers.return_value = fake_layers

        config = self.default_config

        config.dripper.dripper_type = 'photo'
        config.options.use_shufflelayers = False
        config.options.use_sublayers = False
        config.options.use_overlap = False
        
        api = PrintAPI(config)
        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)

        mock_PhotoZAxis.assert_called_with(config.dripper.photo_zaxis_delay)
        mock_Controller.assert_called_with(
            mock_audiomodulationlasercontrol,
            mock_pathtoaudio,
            mock_audiowriter,
            fake_layers,
            zaxis = mock_photozaxis,
            status_call_back = None,
            max_lead_distance = config.dripper.max_lead_distance_mm,
            abort_on_error = True,
            override_speed = config.cure_rate.draw_speed,
            commander = mock_nullcommander,
            layer_start_command = config.serial.layer_started,
            layer_ended_command = config.serial.layer_ended,
            print_ended_command = config.serial.print_ended,
            pre_layer_delay = None
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
        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)

        with self.assertRaises(Exception):
            api.set_drips_per_second(12)

    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.SubLayerGenerator')
    @patch('api.print_api.ShuffleGenerator')
    @patch('api.print_api.OverLapGenerator')
    def test_uses_layer_agument_correctly_and_orderly(self,
            mock_OverLapGenerator,
            mock_ShuffleGenerator,
            mock_SubLayerGenerator,
            mock_AudioModulationLaserControl,
            mock_GCodeReader,
            mock_AudioWriter,
            mock_Transformer,
            mock_PathToAudio,
            mock_Controller,
            ):
        gcode_path = "FakeFile"
        expected_drips_per_second = 12
        mock_gcodereader = mock_GCodeReader.return_value
        layer_generator = 'fake'
        mock_gcodereader.get_layers.return_value = layer_generator
        mock_sublayergenerator = mock_SubLayerGenerator.return_value
        mock_shufflegenerator = mock_ShuffleGenerator.return_value
        mock_overlapgenerator = mock_OverLapGenerator.return_value

        config = self.default_config

        config.options.use_shufflelayers = False
        config.options.use_sublayers = False
        config.options.use_overlap = False
        api = PrintAPI(config)
        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)
        self.assertEquals(layer_generator ,mock_Controller.call_args[0][3])

        config.options.use_shufflelayers = True
        config.options.use_sublayers = False
        config.options.use_overlap = False
        api = PrintAPI(config)
        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)
        self.assertEquals(mock_shufflegenerator ,mock_Controller.call_args[0][3])

        config.options.use_shufflelayers = False
        config.options.use_sublayers = True
        config.options.use_overlap = False
        api = PrintAPI(config)
        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)
        self.assertEquals(mock_sublayergenerator ,mock_Controller.call_args[0][3])
        mock_SubLayerGenerator.assert_called_with(layer_generator, config.options.sublayer_height_mm)

        config.options.use_shufflelayers = False
        config.options.use_sublayers = False
        config.options.use_overlap = True
        api = PrintAPI(config)
        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)
        self.assertEquals(mock_overlapgenerator ,mock_Controller.call_args[0][3])
        mock_OverLapGenerator.assert_called_with(layer_generator, config.options.overlap_amount)

        config.options.use_shufflelayers = True
        config.options.use_sublayers = True
        config.options.use_overlap = True
        api = PrintAPI(config)
        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)
        self.assertEquals(mock_overlapgenerator ,mock_Controller.call_args[0][3])
        mock_OverLapGenerator.assert_called_with(mock_shufflegenerator, config.options.overlap_amount)
        mock_ShuffleGenerator.assert_called_with(mock_sublayergenerator)
        mock_SubLayerGenerator.assert_called_with(layer_generator, config.options.sublayer_height_mm)


    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.TimedDripZAxis')
    @patch('api.print_api.SubLayerGenerator')
    def test_controller_should_be_called_with_right_layer_augments(self,
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
        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)


        mock_TimedDripZAxis.assert_called_with(config.dripper.drips_per_mm, drips_per_second = config.dripper.emulated_drips_per_second)
        self.assertTrue(api.can_set_drips_per_second())
        api.set_drips_per_second(expected_drips_per_second)
        self.assertEquals(expected_drips_per_second, api.get_drips_per_second())

        mock_timeddripzaxis.set_drips_per_second.assert_called_with(expected_drips_per_second)

    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.AudioDripZAxis')
    @patch('api.print_api.SubLayerGenerator')
    @patch('api.print_api.NullCommander')
    @patch('api.print_api.ShuffleGenerator') 
    @patch('api.print_api.EmailNotificationService') 
    @patch('api.print_api.EmailGateway') 
    def test_print_gcode_should_send_email_when_complete_and_email_enabled(self,
            mock_EmailGateway,
            mock_EmailNotificationService,
            mock_ShuffleGenerator,
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
        mock_dripbasedzaxis = mock_AudioDripZAxis.return_value
        mock_audiomodulationlasercontrol = mock_AudioModulationLaserControl.return_value
        mock_gcodereader = mock_GCodeReader.return_value
        mock_controller = mock_Controller.return_value
        mock_email_gateway = mock_EmailGateway.return_value
        mock_email_notification_service = mock_EmailNotificationService.return_value

        mock_audiomodulationlasercontrol.actual_samples_per_second = actual_samples_per_second
        mock_gcodereader.get_layers.return_value = fake_layers

        config = self.default_config
        config.email.on = True
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)
            mock_GCodeReader.assert_called_with(
            m.return_value,
            scale = config.options.scaling_factor
            )
            api.close()

        mock_EmailNotificationService.assert_called_with(mock_email_gateway,config.email.sender,config.email.recipient)
        mock_email_notification_service.send_message.assert_called_with("Print Complete","%s is complete" % gcode_path)


    # def test_init_should_set_call_back_on_zaxis(self, mock_LayerGenerator,mock_LayerWriter,mock_LayerProcessing):
    #     mock_layer_writer = mock_LayerWriter.return_value
    #     mock_layer_processing = mock_LayerProcessing.return_value
    #     mock_layer_generator = mock_LayerGenerator.return_value
    #     Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,mock_layer_generator, mock_zaxis)

    #     self.assertTrue(mock_zaxis.set_call_back.called)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()
