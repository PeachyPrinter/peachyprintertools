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
from infrastructure.machine import *
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

@patch('api.print_api.EmailNotificationService')
@patch('api.print_api.EmailGateway')
@patch('api.print_api.PhotoZAxis')
@patch('api.print_api.TimedDripZAxis')
@patch('api.print_api.SerialCommander')
@patch('api.print_api.OverLapGenerator')
@patch('api.print_api.MachineState')
@patch('api.print_api.MachineStatus')
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
@patch('api.print_api.LayerWriter') 
@patch('api.print_api.LayerProcessing') 
class PrintAPITests(unittest.TestCase, test_helpers.TestHelpers):

    def setup_mocks(self, args):
        self.mock_EmailNotificationService =      args[19 ]
        self.mock_EmailGateway =                  args[18 ]
        self.mock_PhotoZAxis =                    args[17 ]
        self.mock_TimedDripZAxis =                args[16 ]
        self.mock_SerialCommander =               args[15 ]
        self.mock_OverLapGenerator =              args[14 ]
        self.mock_MachineState =                  args[13 ]
        self.mock_MachineStatus =                 args[12 ]
        self.mock_Controller =                    args[11 ]
        self.mock_PathToAudio =                   args[10 ]
        self.mock_HomogenousTransformer =         args[9 ]
        self.mock_AudioWriter =                   args[8 ]
        self.mock_GCodeReader =                   args[7 ]
        self.mock_AudioModulationLaserControl =   args[6 ]
        self.mock_AudioDripZAxis =                args[5 ]
        self.mock_SubLayerGenerator =             args[4 ]
        self.mock_NullCommander =                 args[3 ]
        self.mock_ShuffleGenerator =              args[2 ]
        self.mock_LayerWriter =                   args[1 ]
        self.mock_LayerProcessing =               args[0 ]

        self.mock_email_notification_service =      self.mock_EmailNotificationService.return_value
        self.mock_email_gateway =                   self.mock_EmailGateway.return_value
        self.mock_photo_zaxis =                     self.mock_PhotoZAxis.return_value
        self.mock_timed_drip_zaxis =                self.mock_TimedDripZAxis.return_value
        self.mock_serial_commander =                self.mock_SerialCommander.return_value
        self.mock_over_lap_generator =              self.mock_OverLapGenerator.return_value
        self.mock_machine_state =                   self.mock_MachineState.return_value
        self.mock_machine_status =                  self.mock_MachineStatus.return_value
        self.mock_controller =                      self.mock_Controller.return_value
        self.mock_path_to_audio =                   self.mock_PathToAudio.return_value
        self.mock_homogenous_transformer =          self.mock_HomogenousTransformer.return_value
        self.mock_audio_writer =                    self.mock_AudioWriter.return_value
        self.mock_g_code_reader =                   self.mock_GCodeReader.return_value
        self.mock_audio_modulation_laser_control =  self.mock_AudioModulationLaserControl.return_value
        self.mock_audio_drip_zaxis =                self.mock_AudioDripZAxis.return_value
        self.mock_sub_layer_generator =             self.mock_SubLayerGenerator.return_value
        self.mock_null_commander =                  self.mock_NullCommander.return_value
        self.mock_shuffle_generator =               self.mock_ShuffleGenerator.return_value
        self.mock_layer_writer =                    self.mock_LayerWriter.return_value
        self.mock_layer_processing =                self.mock_LayerProcessing.return_value
        


    def test_print_gcode_should_create_required_classes_and_start_it(self, *args):
        self.setup_mocks(args)

        gcode_path = "FakeFile"
        actual_samples_per_second = 7
        fake_layers = "Fake Layers"
        abort_on_error = True

        self.mock_audio_modulation_laser_control.actual_samples_per_second = actual_samples_per_second
        self.mock_g_code_reader.get_layers.return_value = fake_layers

        config = self.default_config
        config.options.use_shufflelayers = False
        config.options.use_sublayers = False
        config.options.use_overlap = False
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)
            self.mock_GCodeReader.assert_called_with(
            m.return_value,
            scale = config.options.scaling_factor
            )

        self.mock_AudioDripZAxis.assert_called_with(
            config.dripper.drips_per_mm,
            config.audio.input.sample_rate,
            config.audio.input.bit_depth,
            self.mock_null_commander,
            config.serial.on_command,
            config.serial.off_command
            )

        self.mock_AudioModulationLaserControl.assert_called_with(
            config.audio.output.sample_rate,
            config.audio.output.modulation_on_frequency,
            config.audio.output.modulation_off_frequency,
            config.options.laser_offset
            )
        
        self.mock_AudioWriter.assert_called_with(
            config.audio.output.sample_rate,
            config.audio.output.bit_depth,
            )

        self.mock_HomogenousTransformer.assert_called_with(
            config.calibration.max_deflection,
            config.calibration.height,
            config.calibration.lower_points,
            config.calibration.upper_points,
            )

        self.mock_PathToAudio.assert_called_with(
            actual_samples_per_second,
            self.mock_homogenous_transformer, 
            config.options.laser_thickness_mm
            )


        self.mock_LayerWriter.assert_called_with(
            self.mock_audio_writer, 
            self.mock_path_to_audio, 
            self.mock_audio_modulation_laser_control,
            self.mock_machine_state,
            config.cure_rate.draw_speed, 
            )

        self.mock_LayerProcessing.assert_called_with(
            self.mock_layer_writer,
            self.mock_machine_state,
            self.mock_machine_status,
            self.mock_audio_drip_zaxis,
            config.dripper.max_lead_distance_mm,
            self.mock_null_commander ,
            config.options.pre_layer_delay,
            config.serial.layer_started,
            config.serial.layer_ended,
            config.serial.print_ended,
            )

        self.mock_Controller.assert_called_with(
            self.mock_layer_writer,
            self.mock_layer_processing,
            fake_layers,
            self.mock_machine_status,
            abort_on_error = abort_on_error,
            )

    def test_print_gcode_should_create_required_classes_and_start_it_with_pre_layer_delay(self, *args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.options.pre_layer_delay = 1.0
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)

        self.mock_LayerProcessing.assert_called_with(
            self.mock_layer_writer,
            self.mock_machine_state,
            self.mock_machine_status,
            self.mock_audio_drip_zaxis,
            config.dripper.max_lead_distance_mm,
            self.mock_null_commander ,
            config.options.pre_layer_delay,
            config.serial.layer_started,
            config.serial.layer_ended,
            config.serial.print_ended,
            )

    def test_print_gcode_should_create_required_classes_and_start_it_without_override_speed_if_specified(self, *args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.cure_rate.draw_speed = 77.7
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)

        self.mock_LayerWriter.assert_called_with(
            self.mock_audio_writer, 
            self.mock_path_to_audio, 
            self.mock_audio_modulation_laser_control,
            self.mock_machine_state,
            config.cure_rate.draw_speed, 
            )

    def test_print_gcode_should_print_sublayers_if_requested(self,*args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.options.use_shufflelayers = False
        config.options.use_overlap = False
        config.options.use_sublayers = True
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)

        self.mock_Controller.assert_called_with(
            self.mock_layer_writer,
            self.mock_layer_processing,
            self.mock_sub_layer_generator,
            self.mock_machine_status,
            abort_on_error = True,
            )

    def test_print_gcode_should_print_overlap_layers_if_requested(self,*args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.options.use_shufflelayers = False
        config.options.use_overlap = True
        config.options.use_sublayers = False
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)

        self.mock_Controller.assert_called_with(
            self.mock_layer_writer,
            self.mock_layer_processing,
            self.mock_over_lap_generator,
            self.mock_machine_status,
            abort_on_error = True,
            )

    def test_print_gcode_should_print_shuffle_layers_if_requested(self,*args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.options.use_shufflelayers = True
        config.options.use_overlap = False
        config.options.use_sublayers = False
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)

        self.mock_Controller.assert_called_with(
            self.mock_layer_writer,
            self.mock_layer_processing,
            self.mock_shuffle_generator,
            self.mock_machine_status,
            abort_on_error = True,
            )

    def test_print_gcode_should_print_shuffle_overlap_and_sublayer_if_requested(self,*args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.options.use_shufflelayers = True
        config.options.use_overlap = True
        config.options.use_sublayers = True
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            self.mock_g_code_reader.get_layers.return_value = "LayerGenerator"
            api.print_gcode(gcode_path)

        self.mock_SubLayerGenerator.assert_called_with("LayerGenerator", config.options.sublayer_height_mm)
        self.mock_ShuffleGenerator.assert_called_with(self.mock_sub_layer_generator)
        self.mock_OverLapGenerator.assert_called_with(self.mock_shuffle_generator,config.options.overlap_amount)
        

        self.mock_Controller.assert_called_with(
            self.mock_layer_writer,
            self.mock_layer_processing,
            self.mock_over_lap_generator,
            self.mock_machine_status,
            abort_on_error = True,
            )

    def test_print_can_be_stopped_before_started(self,*args):
        api = PrintAPI(self.default_config)
        api.close()

    def test_print_gcode_should_create_serial_commander_if_specified_in_config(self,*args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.serial.on = True
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)

        self.mock_SerialCommander.assert_called_with(config.serial.port)
        self.mock_LayerProcessing.assert_called_with(
            self.mock_layer_writer,
            self.mock_machine_state,
            self.mock_machine_status,
            self.mock_audio_drip_zaxis,
            config.dripper.max_lead_distance_mm,
            self.mock_serial_commander,
            config.options.pre_layer_delay,
            config.serial.layer_started,
            config.serial.layer_ended,
            config.serial.print_ended,
            )

    def test_get_status_calls_controller_status(self,*args):
        self.setup_mocks(args)
        api = PrintAPI(self.default_config)
        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode("Spam")
            api.get_status()

        self.mock_controller.get_status.assert_called_with()

    def test_print_gcode_should_use_emulated_dripper_if_specified_in_config(self, * args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.dripper.dripper_type = 'emulated'
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)

        self.mock_TimedDripZAxis.assert_called_with(config.dripper.drips_per_mm, drips_per_second = config.dripper.emulated_drips_per_second )
        self.mock_LayerProcessing.assert_called_with(
            self.mock_layer_writer,
            self.mock_machine_state,
            self.mock_machine_status,
            self.mock_timed_drip_zaxis,
            config.dripper.max_lead_distance_mm,
            self.mock_null_commander,
            config.options.pre_layer_delay,
            config.serial.layer_started,
            config.serial.layer_ended,
            config.serial.print_ended,
            )

    def test_print_gcode_should_use_photo_dripper_if_specified_in_config(self, * args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.dripper.dripper_type = 'photo'
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)

        self.mock_PhotoZAxis.assert_called_with(config.dripper.photo_zaxis_delay )
        self.mock_LayerProcessing.assert_called_with(
            self.mock_layer_writer,
            self.mock_machine_state,
            self.mock_machine_status,
            self.mock_photo_zaxis,
            config.dripper.max_lead_distance_mm,
            self.mock_null_commander,
            config.options.pre_layer_delay,
            config.serial.layer_started,
            config.serial.layer_ended,
            config.serial.print_ended,
            )

    def test_set_drips_per_second_throws_error_if_not_using_emulated_drips(self, *args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"

        self.mock_audio_drip_zaxis.set_drips_per_second.side_effect = Exception()

        config = self.default_config

        api = PrintAPI(config)
        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)

        with self.assertRaises(Exception):
            api.set_drips_per_second(12)

    def test_print_gcode_should_send_email_when_complete_and_email_enabled(self, *args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.email.on = True
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)
        
        api.close()

        self.mock_EmailNotificationService.assert_called_with(self.mock_email_gateway,config.email.sender,config.email.recipient)
        self.mock_email_notification_service.send_message.assert_called_with("Print Complete","%s is complete" % gcode_path)


    def test_init_should_set_call_back_on_zaxis(self, *args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        actual_samples_per_second = 7
        fake_layers = "Fake Layers"
        abort_on_error = True

        self.mock_audio_modulation_laser_control.actual_samples_per_second = actual_samples_per_second
        self.mock_g_code_reader.get_layers.return_value = fake_layers

        config = self.default_config
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as m:
            api.print_gcode(gcode_path)

        self.mock_audio_drip_zaxis.set_call_back.assert_called_with(self.mock_machine_status.drip_call_back)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()
