import unittest
import os
import sys
import time

from mock import patch, mock_open, MagicMock

import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from peachyprinter.api.print_api import PrintAPI, PrintQueueAPI
from peachyprinter.infrastructure.machine import *
from peachyprinter.infrastructure.messages import PrinterStatusMessage

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
        folder = os.path.join('', 'SomthingMadeUp')
        mock_isdir.return_value = True
        mock_listdir.return_value = []
        with patch('peachyprinter.api.print_api.listdir', return_value=[]):
            with self.assertRaises(Exception):
                api = PrintQueueAPI(self.default_config)
                api.print_folder(folder)

    @patch.object(os.path, 'isdir')
    def test_print_folder_should_raise_exception_when_no_gcode_files(self,  mock_isdir):
        folder = os.path.join('', 'SomthingMadeUp')
        mock_isdir.return_value = True
        with patch('peachyprinter.api.print_api.listdir', return_value=['ASDFAS.txt', 'bor.fa']):
            with self.assertRaises(Exception):
                api = PrintQueueAPI(self.default_config)
                api.print_folder(folder)

    @patch.object(os.path, 'isdir')
    @patch.object(PrintAPI, 'print_gcode')
    def test_print_folder_should_call_print_api_for_gcode_files(self, mock_print_gcode, mock_isdir):
        folder = os.path.join('', 'SomthingMadeUp')
        expected_file = 'thingy.gcode'
        expected_path = os.path.join(folder, expected_file)
        mock_isdir.return_value = True
        with patch('peachyprinter.api.print_api.listdir', return_value=['ASDFAS.txt', 'bor.fa', expected_file]):
            api = PrintQueueAPI(self.default_config)
            api.print_folder(folder)
        mock_print_gcode.assert_called_with(expected_path)

    @patch.object(os.path, 'isdir')
    @patch('peachyprinter.api.print_api.PrintAPI')
    def test_print_folder_should_call_print_api_for_each_gcode_files_after_layer_complete(self, mock_PrintAPI, mock_isdir):
        folder = os.path.join('', 'SomthingMadeUp')
        expected_file1 = 'thingy1.gcode'
        expected_file2 = 'thingy2.gcode'
        expected_path1 = os.path.join(folder, expected_file1)
        expected_path2 = os.path.join(folder, expected_file2)
        mock_isdir.return_value = True
        mock_print_api = mock_PrintAPI.return_value
        with patch('peachyprinter.api.print_api.listdir', return_value=['ASDFAS.txt', 'bor.fa', expected_file1, expected_file2]):
            api = PrintQueueAPI(self.default_config)
            api.print_folder(folder)
            mock_print_api.print_gcode.assert_called_with(expected_path1)
            call_back = mock_PrintAPI.call_args[0][1]
            mock_status = {'status': 'Complete'}
            call_back(mock_status)
            mock_print_api.print_gcode.assert_called_with(expected_path2)

    @patch.object(os.path, 'isdir')
    @patch('peachyprinter.api.print_api.PrintAPI')
    def test_print_folder_should_close_api_before_opening_new_one(self, mock_PrintAPI, mock_isdir):
        folder = os.path.join('', 'SomthingMadeUp')
        expected_file1 = 'thingy1.gcode'
        expected_file2 = 'thingy2.gcode'
        mock_isdir.return_value = True
        mock_print_api = mock_PrintAPI.return_value
        with patch('peachyprinter.api.print_api.listdir', return_value=['ASDFAS.txt', 'bor.fa', expected_file1, expected_file2]):
            api = PrintQueueAPI(self.default_config)
            api.print_folder(folder)
            call_back = mock_PrintAPI.call_args[0][1]
            mock_status = {'status': 'Complete'}
            call_back(mock_status)
            mock_print_api.close.assert_called_with()

    @patch.object(os.path, 'isdir')
    @patch('peachyprinter.api.print_api.PrintAPI')
    def test_print_folder_should_be_interuptable(self, mock_PrintAPI, mock_isdir):
        folder = os.path.join('', 'SomthingMadeUp')
        expected_file1 = 'thingy1.gcode'
        expected_file2 = 'thingy2.gcode'
        mock_isdir.return_value = True
        mock_print_api = mock_PrintAPI.return_value
        with patch('peachyprinter.api.print_api.listdir', return_value=['ASDFAS.txt', 'bor.fa', expected_file1, expected_file2]):
            api = PrintQueueAPI(self.default_config)
            api.print_folder(folder)
            api.close()
            mock_print_api.close.assert_called_with()
            self.assertEquals(1, mock_PrintAPI.call_count)

    @patch.object(os.path, 'isdir')
    @patch('peachyprinter.api.print_api.PrintAPI')
    def test_print_folder_ends_smoothly(self, mock_PrintAPI, mock_isdir):
        folder = os.path.join('', 'SomthingMadeUp')
        expected_file1 = 'thingy1.gcode'
        mock_isdir.return_value = True
        with patch('peachyprinter.api.print_api.listdir', return_value=['ASDFAS.txt', 'bor.fa', expected_file1]):
            api = PrintQueueAPI(self.default_config)
            api.print_folder(folder)
            call_back = mock_PrintAPI.call_args[0][1]
            mock_status = {'status': 'Complete'}
            call_back(mock_status)

    @patch.object(os.path, 'isdir')
    @patch('peachyprinter.api.print_api.PrintAPI')
    def test_print_folder_should_delay_between_prints(self, mock_PrintAPI, mock_isdir):
        folder = os.path.join('', 'SomthingMadeUp')
        expected_file1 = 'thingy1.gcode'
        expected_file2 = 'thingy2.gcode'
        expected_delay = 0.1
        mock_isdir.return_value = True
        config = self.default_config
        config.options.print_queue_delay = expected_delay
        with patch('peachyprinter.api.print_api.listdir', return_value=['ASDFAS.txt', 'bor.fa', expected_file1, expected_file2]):
            api = PrintQueueAPI(config)
            api.print_folder(folder)
            self.assertEquals(1, mock_PrintAPI.call_count)
            call_back = mock_PrintAPI.call_args[0][1]
            start = time.time()
            mock_status = {'status': 'Complete'}
            call_back(mock_status)
            call_back(mock_status)
            end = time.time()
            self.assertTrue(expected_delay <= end-start + 0.01, "%s was not <= %s" % (expected_delay, (end - start + 0.01)))

@patch('peachyprinter.api.print_api.SerialDripZAxis')
@patch('peachyprinter.api.print_api.MicroDisseminator')
@patch('peachyprinter.api.print_api.UsbPacketCommunicator')
@patch('peachyprinter.api.print_api.LaserControl')
@patch('peachyprinter.api.print_api.FileWriter')
@patch('peachyprinter.api.print_api.EmailNotificationService')
@patch('peachyprinter.api.print_api.EmailGateway')
@patch('peachyprinter.api.print_api.PhotoZAxis')
@patch('peachyprinter.api.print_api.TimedDripZAxis')
@patch('peachyprinter.api.print_api.SerialCommander')
@patch('peachyprinter.api.print_api.OverLapGenerator')
@patch('peachyprinter.api.print_api.MachineState')
@patch('peachyprinter.api.print_api.MachineStatus')
@patch('peachyprinter.api.print_api.Controller')
@patch('peachyprinter.api.print_api.PathToPoints')
@patch('peachyprinter.api.print_api.HomogenousTransformer')
@patch('peachyprinter.api.print_api.GCodeReader')
@patch('peachyprinter.api.print_api.SubLayerGenerator')
@patch('peachyprinter.api.print_api.NullCommander')
@patch('peachyprinter.api.print_api.ShuffleGenerator')
@patch('peachyprinter.api.print_api.LayerWriter')
@patch('peachyprinter.api.print_api.LayerProcessing')
class PrintAPITests(unittest.TestCase, test_helpers.TestHelpers):

    def setup_mocks(self, args):
        self.mock_SerialDripZAxis =               args[21]
        self.mock_MicroDisseminator =             args[20]
        self.mock_UsbPacketCommunicator =         args[19]
        self.mock_LaserControl =                  args[18]
        self.mock_FileWriter =                    args[17]
        self.mock_EmailNotificationService =      args[16]
        self.mock_EmailGateway =                  args[15]
        self.mock_PhotoZAxis =                    args[14]
        self.mock_TimedDripZAxis =                args[13]
        self.mock_SerialCommander =               args[12]
        self.mock_OverLapGenerator =              args[11]
        self.mock_MachineState =                  args[10]
        self.mock_MachineStatus =                 args[9]
        self.mock_Controller =                    args[8]
        self.mock_PathToPoints =                  args[7]
        self.mock_HomogenousTransformer =         args[6]
        self.mock_GCodeReader =                   args[5]
        self.mock_SubLayerGenerator =             args[4]
        self.mock_NullCommander =                 args[3]
        self.mock_ShuffleGenerator =              args[2]
        self.mock_LayerWriter =                   args[1]
        self.mock_LayerProcessing =               args[0]

        self.mock_serial_drip_zaxis =               self.mock_SerialDripZAxis.return_value
        self.mock_micro_disseminator =              self.mock_MicroDisseminator.return_value
        self.mock_usb_packet_communicator =             self.mock_UsbPacketCommunicator.return_value
        self.mock_laser_control =                   self.mock_LaserControl.return_value
        self.mock_filewriter =                      self.mock_FileWriter.return_value
        self.mock_email_notification_service =      self.mock_EmailNotificationService.return_value
        self.mock_email_gateway =                   self.mock_EmailGateway.return_value
        self.mock_photo_zaxis =                     self.mock_PhotoZAxis.return_value
        self.mock_timed_drip_zaxis =                self.mock_TimedDripZAxis.return_value
        self.mock_serial_commander =                self.mock_SerialCommander.return_value
        self.mock_over_lap_generator =              self.mock_OverLapGenerator.return_value
        self.mock_machine_state =                   self.mock_MachineState.return_value
        self.mock_machine_status =                  self.mock_MachineStatus.return_value
        self.mock_controller =                      self.mock_Controller.return_value
        self.mock_path_to_audio =                   self.mock_PathToPoints.return_value
        self.mock_homogenous_transformer =          self.mock_HomogenousTransformer.return_value
        self.mock_g_code_reader =                   self.mock_GCodeReader.return_value
        self.mock_sub_layer_generator =             self.mock_SubLayerGenerator.return_value
        self.mock_null_commander =                  self.mock_NullCommander.return_value
        self.mock_shuffle_generator =               self.mock_ShuffleGenerator.return_value
        self.mock_layer_writer =                    self.mock_LayerWriter.return_value
        self.mock_layer_processing =                self.mock_LayerProcessing.return_value


    def test_print_gcode_should_create_required_classes_and_start_it_for_digital(self, *args):
        self.setup_mocks(args)

        gcode_path = "FakeFile"
        actual_samples_per_second = 7
        fake_layers = "Fake Layers"

        self.mock_micro_disseminator.samples_per_second = actual_samples_per_second
        self.mock_g_code_reader.get_layers.return_value = fake_layers

        config = self.default_config
        config.options.use_shufflelayers = False
        config.options.use_sublayers = False
        config.options.use_overlap = False
        config.options.post_fire_delay = 5
        config.options.slew_delay = 5
        config.options.wait_after_move_milliseconds = 5
        config.dripper.dripper_type = 'microcontroller'
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as mocked_open:
            api.print_gcode(gcode_path)
            self.mock_GCodeReader.assert_called_with(
                mocked_open.return_value,
                scale=config.options.scaling_factor,
                start_height=0.0
                )

        self.mock_LaserControl.assert_called_with(
            config.cure_rate.override_laser_power_amount
            )

        self.mock_UsbPacketCommunicator.assert_called_with(config.circut.print_queue_length)
        
        self.mock_usb_packet_communicator.start.assert_called_with()

        self.mock_MicroDisseminator.assert_called_with(
            self.mock_laser_control,
            self.mock_usb_packet_communicator,
            config.circut.data_rate
            )

        self.assertEquals(0, self.mock_usb_packet_communicator.call_count)

        self.mock_HomogenousTransformer.assert_called_with(
            config.calibration.max_deflection,
            config.calibration.height,
            config.calibration.lower_points,
            config.calibration.upper_points,
            )

        self.mock_PathToPoints.assert_called_with(
            actual_samples_per_second,
            self.mock_homogenous_transformer,
            config.options.laser_thickness_mm
            )

        self.mock_LayerWriter.assert_called_with(
            self.mock_micro_disseminator,
            self.mock_path_to_audio,
            self.mock_laser_control,
            self.mock_machine_state,
            move_distance_to_ignore=config.options.laser_thickness_mm,
            override_draw_speed=config.cure_rate.draw_speed,
            override_move_speed=config.cure_rate.move_speed,
            wait_speed=100.0,
            post_fire_delay_speed=100.0,
            slew_delay_speed=100.0,
            )

        self.mock_SerialDripZAxis.assert_called_with(
            self.mock_usb_packet_communicator,
            config.dripper.drips_per_mm,
            0.0
            )

        self.mock_LayerProcessing.assert_called_with(
            self.mock_layer_writer,
            self.mock_machine_state,
            self.mock_machine_status,
            self.mock_serial_drip_zaxis,
            config.dripper.max_lead_distance_mm,
            self.mock_null_commander,
            config.options.pre_layer_delay,
            config.serial.layer_started,
            config.serial.layer_ended,
            config.serial.print_ended,
            config.serial.on_command,
            config.serial.off_command,
            )

    def test_print_gcode_should_use_start_height(self, *args):
        self.setup_mocks(args)
        expected_start_height = 7.7
        gcode_path = "FakeFile"
        actual_samples_per_second = 7
        fake_layers = "Fake Layers"

        self.mock_micro_disseminator.actual_samples_per_second = actual_samples_per_second
        self.mock_g_code_reader.get_layers.return_value = fake_layers

        config = self.default_config
        api = PrintAPI(config, start_height=expected_start_height)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True) as mocked_open:
            api.print_gcode(gcode_path)
            self.mock_GCodeReader.assert_called_with(
                mocked_open.return_value,
                scale=config.options.scaling_factor,
                start_height=expected_start_height
                )

        self.mock_SerialDripZAxis.assert_called_with(
            self.mock_usb_packet_communicator,
            config.dripper.drips_per_mm,
            expected_start_height,
            )

    def test_print_gcode_should_create_required_classes_and_start_it_with_pre_layer_delay(self, *args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.options.pre_layer_delay = 1.0
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True):
            api.print_gcode(gcode_path)

        self.mock_LayerProcessing.assert_called_with(
            self.mock_layer_writer,
            self.mock_machine_state,
            self.mock_machine_status,
            self.mock_serial_drip_zaxis,
            config.dripper.max_lead_distance_mm,
            self.mock_null_commander,
            config.options.pre_layer_delay,
            config.serial.layer_started,
            config.serial.layer_ended,
            config.serial.print_ended,
            config.serial.on_command,
            config.serial.off_command,
            )

    def test_print_gcode_should_handle_0_wait_after_move_settings(self, *args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.cure_rate.draw_speed = 77.7
        config.options.slew_delay = 5
        config.options.post_fire_delay = 5
        config.options.wait_after_move_milliseconds = 0

        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True):
            api.print_gcode(gcode_path)

        self.mock_LayerWriter.assert_called_with(
            self.mock_micro_disseminator,
            self.mock_path_to_audio,
            self.mock_laser_control,
            self.mock_machine_state,
            move_distance_to_ignore=config.options.laser_thickness_mm,
            override_draw_speed=config.cure_rate.draw_speed,
            override_move_speed=config.cure_rate.move_speed,
            wait_speed=None,
            post_fire_delay_speed=100.0,
            slew_delay_speed=100.0
            )

    def test_print_gcode_should_create_required_classes_and_start_it_with_override_speed_if_specified(self, *args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.cure_rate.draw_speed = 77.7
        config.options.slew_delay = 5
        config.options.post_fire_delay = 5
        config.options.wait_after_move_milliseconds = 5

        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True):
            api.print_gcode(gcode_path)

        self.mock_LayerWriter.assert_called_with(
            self.mock_micro_disseminator,
            self.mock_path_to_audio,
            self.mock_laser_control,
            self.mock_machine_state,
            move_distance_to_ignore=config.options.laser_thickness_mm,
            override_draw_speed=config.cure_rate.draw_speed,
            override_move_speed=config.cure_rate.move_speed,
            wait_speed=100.0,
            post_fire_delay_speed=100.0,
            slew_delay_speed=100.0
            )

    def test_print_gcode_should_create_required_classes_and_start_it_without_override_speed_if_force_source_speed_flagged(self, *args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.cure_rate.draw_speed = 77.7
        config.options.slew_delay = 5
        config.options.post_fire_delay = 5
        config.options.wait_after_move_milliseconds = 5

        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True):
            api.print_gcode(gcode_path, force_source_speed=True)

        self.mock_LayerWriter.assert_called_with(
            self.mock_micro_disseminator,
            self.mock_path_to_audio,
            self.mock_laser_control,
            self.mock_machine_state,
            move_distance_to_ignore=config.options.laser_thickness_mm,
            override_draw_speed=None,
            override_move_speed=None,
            wait_speed=100.0,
            post_fire_delay_speed=100.0,
            slew_delay_speed=100.0
            )

    def test_print_gcode_should_print_sublayers_if_requested(self, *args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.options.use_shufflelayers = False
        config.options.use_overlap = False
        config.options.use_sublayers = True
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True):
            api.print_gcode(gcode_path)

        self.mock_Controller.assert_called_with(
            self.mock_layer_writer,
            self.mock_layer_processing,
            self.mock_sub_layer_generator,
            self.mock_machine_status,
            abort_on_error=True,
            )

    def test_print_gcode_should_print_overlap_layers_if_requested(self, *args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.options.use_shufflelayers = False
        config.options.use_overlap = True
        config.options.use_sublayers = False
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True):
            api.print_gcode(gcode_path)

        self.mock_Controller.assert_called_with(
            self.mock_layer_writer,
            self.mock_layer_processing,
            self.mock_over_lap_generator,
            self.mock_machine_status,
            abort_on_error=True,
            )

    def test_print_gcode_should_print_shuffle_layers_if_requested(self, *args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.options.use_shufflelayers = True
        config.options.use_overlap = False
        config.options.use_sublayers = False
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True):
            api.print_gcode(gcode_path)

        self.mock_Controller.assert_called_with(
            self.mock_layer_writer,
            self.mock_layer_processing,
            self.mock_shuffle_generator,
            self.mock_machine_status,
            abort_on_error=True,
            )

    def test_print_gcode_should_print_shuffle_overlap_and_sublayer_if_requested(self, *args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.options.use_shufflelayers = True
        config.options.use_overlap = True
        config.options.use_sublayers = True
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True):
            self.mock_g_code_reader.get_layers.return_value = "LayerGenerator"
            api.print_gcode(gcode_path)

        self.mock_SubLayerGenerator.assert_called_with("LayerGenerator", config.options.sublayer_height_mm)
        self.mock_ShuffleGenerator.assert_called_with(self.mock_sub_layer_generator, config.options.shuffle_layers_amount)
        self.mock_OverLapGenerator.assert_called_with(self.mock_shuffle_generator, config.options.overlap_amount)

        self.mock_Controller.assert_called_with(
            self.mock_layer_writer,
            self.mock_layer_processing,
            self.mock_over_lap_generator,
            self.mock_machine_status,
            abort_on_error=True,
            )

    def test_print_can_be_stopped_before_started(self, *args):
        api = PrintAPI(self.default_config)
        api.close()

    def test_print_gcode_should_create_serial_commander_if_specified_in_config(self, *args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.serial.on = True
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True):
            api.print_gcode(gcode_path)

        self.mock_SerialCommander.assert_called_with(config.serial.port)
        self.mock_LayerProcessing.assert_called_with(
            self.mock_layer_writer,
            self.mock_machine_state,
            self.mock_machine_status,
            self.mock_serial_drip_zaxis,
            config.dripper.max_lead_distance_mm,
            self.mock_serial_commander,
            config.options.pre_layer_delay,
            config.serial.layer_started,
            config.serial.layer_ended,
            config.serial.print_ended,
            config.serial.on_command,
            config.serial.off_command,

            )

    def test_get_status_calls_controller_status(self, *args):
        self.setup_mocks(args)
        api = PrintAPI(self.default_config)
        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True):
            api.print_gcode("Spam")
            api.get_status()

        self.mock_controller.get_status.assert_called_with()

    def test_print_gcode_should_use_emulated_dripper_if_specified_in_config(self, * args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.dripper.dripper_type = 'emulated'
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True):
            api.print_gcode(gcode_path)

        self.mock_TimedDripZAxis.assert_called_with(config.dripper.drips_per_mm, 0.0, drips_per_second=config.dripper.emulated_drips_per_second)
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
            config.serial.on_command,
            config.serial.off_command,
            )

    def test_print_gcode_should_use_emulated_dripper_and_start_height(self, * args):
        self.setup_mocks(args)
        expected_start_height = 7.7
        gcode_path = "FakeFile"
        config = self.default_config
        config.dripper.dripper_type = 'emulated'
        api = PrintAPI(config, start_height=expected_start_height)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True):
            api.print_gcode(gcode_path)

        self.mock_TimedDripZAxis.assert_called_with(config.dripper.drips_per_mm, expected_start_height, drips_per_second=config.dripper.emulated_drips_per_second)

    def test_print_gcode_should_use_photo_dripper_if_specified_in_config(self, * args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.dripper.dripper_type = 'photo'
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True):
            api.print_gcode(gcode_path)

        self.mock_PhotoZAxis.assert_called_with(0.0, config.dripper.photo_zaxis_delay)
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
            config.serial.on_command,
            config.serial.off_command,
            )

    def test_print_gcode_should_use_photo_dripper_and_start_height(self, * args):
        self.setup_mocks(args)
        expected_start_height = 7.7
        gcode_path = "FakeFile"
        config = self.default_config
        config.dripper.dripper_type = 'photo'
        api = PrintAPI(config, start_height=expected_start_height)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True):
            api.print_gcode(gcode_path)

        self.mock_PhotoZAxis.assert_called_with(expected_start_height, config.dripper.photo_zaxis_delay)

    def test_set_drips_per_second_throws_error_if_not_using_emulated_drips(self, *args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"

        self.mock_serial_drip_zaxis.set_drips_per_second.side_effect = Exception()

        config = self.default_config

        api = PrintAPI(config)
        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True):
            api.print_gcode(gcode_path)

        with self.assertRaises(Exception):
            api.set_drips_per_second(12)

    def test_print_gcode_should_send_email_when_complete_and_email_enabled(self, *args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        config = self.default_config
        config.email.on = True
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True):
            api.print_gcode(gcode_path)

        api.close()

        self.mock_EmailNotificationService.assert_called_with(self.mock_email_gateway, config.email.sender, config.email.recipient)
        self.mock_email_notification_service.send_message.assert_called_with("Print Complete", "%s is complete" % gcode_path)

    def test_print_should_set_call_back_on_zaxis(self, *args):
        self.setup_mocks(args)
        gcode_path = "FakeFile"
        actual_samples_per_second = 7
        fake_layers = "Fake Layers"

        self.mock_micro_disseminator.actual_samples_per_second = actual_samples_per_second
        self.mock_g_code_reader.get_layers.return_value = fake_layers

        config = self.default_config
        api = PrintAPI(config)

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True):
            api.print_gcode(gcode_path)

        self.mock_serial_drip_zaxis.set_call_back.assert_called_with(self.mock_machine_status.drip_call_back)

    def test_configuration_returns_configuration(self, *args):
        self.setup_mocks(args)
        config = self.default_config
        config.email.on = True
        api = PrintAPI(config)

        self.assertEqual(config, api.configuration)

    def test_subscribe_to_status_should_do_nothing_if_printer_not_started(self, *args):
        self.setup_mocks(args)
        config = self.default_config
        api = PrintAPI(config)
        mock_call_back = MagicMock()

        api.subscribe_to_status(mock_call_back)

        self.assertEquals(0, self.mock_UsbPacketCommunicator.return_value.register_handler.call_count)

    def test_subscribe_to_status_should_if_printer_started(self, *args):
        self.setup_mocks(args)
        config = self.default_config
        api = PrintAPI(config)
        mock_call_back = MagicMock()

        with patch('__builtin__.open', mock_open(read_data='bibble'), create=True):
            api.print_gcode('FakeFile')
            api.subscribe_to_status(mock_call_back)

        self.mock_UsbPacketCommunicator.return_value.register_handler.assert_called_with(PrinterStatusMessage, mock_call_back)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()
