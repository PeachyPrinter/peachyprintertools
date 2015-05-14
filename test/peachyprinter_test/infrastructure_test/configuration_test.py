import unittest
import os
import sys
import json

from StringIO import StringIO

from mock import patch, MagicMock, mock_open

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from peachyprinter.infrastructure.configuration import *

import test_helpers

class CalibrationConfigurationTests(unittest.TestCase, test_helpers.TestHelpers):
    def test_set_should_fail_for_bad_values(self):
        expected_print_area_x = "Bad Values"
        expected_print_area_y = "Bad Values"
        expected_print_area_z = "Bad Values"
        expected_flip_x_axis = "Bad Values"
        expected_flip_y_axis = "Bad Values"
        expected_swap_axis = "Bad Values"

        calibration = CalibrationConfiguration()

        with self.assertRaises(Exception):
            calibration.print_area_x = expected_print_area_x
        with self.assertRaises(Exception):
            calibration.print_area_y = expected_print_area_y
        with self.assertRaises(Exception):
            calibration.print_area_z = expected_print_area_z
        with self.assertRaises(Exception):
            calibration.flip_x_axis = expected_flip_x_axis
        with self.assertRaises(Exception):
            calibration.flip_y_axis = expected_flip_y_axis
        with self.assertRaises(Exception):
            calibration.swap_axis = expected_swap_axis

    def test_can_create_json_and_load_from_file(self):
        expected_print_area_x = 10.0
        expected_print_area_y = 20.0
        expected_print_area_z = 30.0
        expected_flip_x_axis = False
        expected_flip_y_axis = False
        expected_swap_axis = False


        original_config= Configuration()

        original_config.calibration.print_area_x = expected_print_area_x
        original_config.calibration.print_area_y = expected_print_area_y
        original_config.calibration.print_area_z = expected_print_area_z
        original_config.calibration.flip_x_axis = expected_flip_x_axis
        original_config.calibration.flip_y_axis = expected_flip_y_axis
        original_config.calibration.swap_axis = expected_swap_axis

        actual_json = json.loads(original_config.toJson())
        config = Configuration(source=actual_json)

        self.assertEquals(type(expected_print_area_x),  type(config.calibration.print_area_x))
        self.assertEquals(type(expected_print_area_y),  type(config.calibration.print_area_y))
        self.assertEquals(type(expected_print_area_z),  type(config.calibration.print_area_z))
        self.assertEquals(type(expected_flip_x_axis),   type(config.calibration.flip_x_axis))
        self.assertEquals(type(expected_flip_y_axis),   type(config.calibration.flip_y_axis))
        self.assertEquals(type(expected_swap_axis),     type(config.calibration.swap_axis))
 
        self.assertEquals(expected_print_area_x,    config.calibration.print_area_x)
        self.assertEquals(expected_print_area_y,    config.calibration.print_area_y)
        self.assertEquals(expected_print_area_z,    config.calibration.print_area_z)
        self.assertEquals(expected_flip_x_axis,     config.calibration.flip_x_axis)
        self.assertEquals(expected_flip_y_axis,     config.calibration.flip_y_axis)
        self.assertEquals(expected_swap_axis,       config.calibration.swap_axis)


class CircutConfigurationTests(unittest.TestCase, test_helpers.TestHelpers):
    def test_set_should_fail_for_incorrect_values(self):
        expected_software_revision = True
        expected_hardware_revision = True
        expected_serial_number = True
        expected_data_rate = True

        circut = CircutConfiguration()

        with self.assertRaises(Exception):
            circut.software_revision = expected_software_revision
        with self.assertRaises(Exception):
            circut.hardware_revision = expected_hardware_revision
        with self.assertRaises(Exception):
            circut.serial_number = expected_serial_number
        with self.assertRaises(Exception):
            circut.data_rate = expected_data_rate



    def test_can_create_json_and_load_from_json(self):
        expected_software_revision = "SR1"
        expected_hardware_revision = "HW1"
        expected_serial_number ="SN1"
        expected_data_rate= 9600

        original_config = Configuration()

        original_config.circut.software_revision = expected_software_revision
        original_config.circut.hardware_revision = expected_hardware_revision
        original_config.circut.serial_number = expected_serial_number
        original_config.circut.data_rate = expected_data_rate

        actual_json = json.loads(original_config.toJson())
        config = Configuration(source=actual_json)

        self.assertEquals(type(expected_software_revision), type(config.circut.software_revision))
        self.assertEquals(type(expected_hardware_revision), type(config.circut.hardware_revision))
        self.assertEquals(type(expected_serial_number),     type(config.circut.serial_number))
        self.assertEquals(type(expected_data_rate),         type(config.circut.data_rate))
        self.assertEquals(expected_software_revision,       config.circut.software_revision)
        self.assertEquals(expected_hardware_revision,       config.circut.hardware_revision)
        self.assertEquals(expected_serial_number,           config.circut.serial_number)
        self.assertEquals(expected_data_rate,               config.circut.data_rate)

class CureRateConfigurationTests(unittest.TestCase, test_helpers.TestHelpers):
    def test_set_should_fail_for_incorrect_values(self):
        expected_base_height = True
        expected_total_height = True
        expected_start_speed = True
        expected_finish_speed = True
        expected_draw_speed = True
        expected_move_speed = True
        expected_use_draw_speed = 123
        expected_override_laser_power = 123
        expected_override_laser_power_amount = True

        cure_rate_config = CureRateConfiguration()

        with self.assertRaises(Exception):
            cure_rate_config.base_height = expected_base_height
        with self.assertRaises(Exception):
            cure_rate_config.total_height = expected_total_height
        with self.assertRaises(Exception):
            cure_rate_config.start_speed = expected_start_speed
        with self.assertRaises(Exception):
            cure_rate_config.finish_speed = expected_finish_speed
        with self.assertRaises(Exception):
            cure_rate_config.draw_speed = expected_draw_speed
        with self.assertRaises(Exception):
            cure_rate_config.draw_speed = expected_move_speed
        with self.assertRaises(Exception):
            cure_rate_config.use_draw_speed = expected_use_draw_speed
        with self.assertRaises(Exception):
            cure_rate_config.override_laser_power = expected_override_laser_power
        with self.assertRaises(Exception):
            cure_rate_config.override_laser_power_amount = expected_override_laser_power_amount

    def test_can_create_json_and_load_from_json(self):
        expected_base_height = 3.0
        expected_total_height = 13.0
        expected_start_speed = 50.0
        expected_finish_speed = 200.0
        expected_draw_speed = 100.0
        expected_move_speed = 300.0
        expected_use_draw_speed = True
        expected_override_laser_power = True
        expected_override_laser_power_amount = 0.05

        original_config = Configuration()

        original_config.cure_rate.base_height                   = expected_base_height
        original_config.cure_rate.total_height                  = expected_total_height
        original_config.cure_rate.start_speed                   = expected_start_speed
        original_config.cure_rate.finish_speed                  = expected_finish_speed
        original_config.cure_rate.draw_speed                    = expected_draw_speed
        original_config.cure_rate.move_speed                    = expected_move_speed
        original_config.cure_rate.use_draw_speed                = expected_use_draw_speed
        original_config.cure_rate.override_laser_power          = expected_override_laser_power
        original_config.cure_rate.override_laser_power_amount   = expected_override_laser_power_amount

        actual_json = json.loads(original_config.toJson())
        config = Configuration(source=actual_json)

        self.assertEquals(type(expected_base_height),                   type(config.cure_rate.base_height))
        self.assertEquals(type(expected_total_height),                  type(config.cure_rate.total_height))
        self.assertEquals(type(expected_start_speed),                   type(config.cure_rate.start_speed))
        self.assertEquals(type(expected_finish_speed),                  type(config.cure_rate.finish_speed))
        self.assertEquals(type(expected_draw_speed),                    type(config.cure_rate.draw_speed))
        self.assertEquals(type(expected_move_speed),                    type(config.cure_rate.move_speed))
        self.assertEquals(type(expected_use_draw_speed),                type(config.cure_rate.use_draw_speed))
        self.assertEquals(type(expected_override_laser_power),          type(config.cure_rate.override_laser_power))
        self.assertEquals(type(expected_override_laser_power_amount),   type(config.cure_rate.override_laser_power_amount))

        self.assertEquals(expected_base_height,                     config.cure_rate.base_height)
        self.assertEquals(expected_total_height,                    config.cure_rate.total_height)
        self.assertEquals(expected_start_speed,                     config.cure_rate.start_speed)
        self.assertEquals(expected_finish_speed,                    config.cure_rate.finish_speed)
        self.assertEquals(expected_draw_speed,                      config.cure_rate.draw_speed)
        self.assertEquals(expected_move_speed,                      config.cure_rate.move_speed)
        self.assertEquals(expected_use_draw_speed,                  config.cure_rate.use_draw_speed)
        self.assertEquals(expected_override_laser_power,            config.cure_rate.override_laser_power)
        self.assertEquals(expected_override_laser_power_amount,     config.cure_rate.override_laser_power_amount)


class EmailConfigurationTests(unittest.TestCase, test_helpers.TestHelpers):
    def test_set_should_fail_for_incorrect_values(self):
        expected_on = "ASDF"
        expected_port = True
        expected_host = 1354
        expected_sender = "ASDF"
        expected_recipient = "ASDF"
        expected_username = True
        expected_password = True

        email_config = EmailConfiguration()

        with self.assertRaises(Exception):
            email_config.on = expected_on
        with self.assertRaises(Exception):
            email_config.port = expected_port
        with self.assertRaises(Exception):
            email_config.host = expected_host
        with self.assertRaises(Exception):
            email_config.sender = expected_sender
        with self.assertRaises(Exception):
            email_config.recipient = expected_recipient
        with self.assertRaises(Exception):
            email_config.sender = expected_username
        with self.assertRaises(Exception):
            email_config.recipient = expected_password


    def test_can_create_json_and_load_from_json(self):

        expected_on = True
        expected_port = 25
        expected_host = "smtp.host.com"
        expected_sender = "valid@email.com"
        expected_recipient = "anothervalid@email.com"
        expected_username = "username"
        expected_password = "Pa55word"

        original_config = Configuration()

        original_config.email.on                   = expected_on
        original_config.email.port                 = expected_port
        original_config.email.host                 = expected_host
        original_config.email.sender               = expected_sender
        original_config.email.recipient            = expected_recipient
        original_config.email.username             = expected_username
        original_config.email.password             = expected_password

        actual_json = json.loads(original_config.toJson())
        config = Configuration(source=actual_json)

        self.assertEquals(type(expected_on), type(config.email.on))
        self.assertEquals(type(expected_port), type(config.email.port))
        self.assertEquals(type(expected_host), type(config.email.host))
        self.assertEquals(type(expected_sender), type(config.email.sender))
        self.assertEquals(type(expected_recipient), type(config.email.recipient))
        self.assertEquals(type(expected_username), type(config.email.username))
        self.assertEquals(type(expected_password), type(config.email.password))

        self.assertEquals(expected_on, config.email.on)
        self.assertEquals(expected_port, config.email.port)
        self.assertEquals(expected_host, config.email.host)
        self.assertEquals(expected_username, config.email.username)
        self.assertEquals(expected_password, config.email.password)


class OptionsConfigurationTests(unittest.TestCase, test_helpers.TestHelpers):
    def test_set_should_fail_for_incorrect_values(self):
        expected_sublayer_height_mm = True
        expected_laser_thickness_mm = True
        expected_scaling_factor = True
        expected_overlap_amount = True
        expected_shuffle_layers_amount = True
        expected_use_shufflelayers = "WRONG"
        expected_use_sublayers = "WRONG"
        expected_use_overlap = "WRONG"
        expected_print_queue_delay = True
        expected_pre_layer_delay = True
        expected_post_fire_delay = True
        expected_slew_delay = True
        expected_wait_after_move_milliseconds = True
        expected_write_wav_files = "WRONG"
        expected_write_wav_files_folder = True

        options_config = OptionsConfiguration()

        with self.assertRaises(Exception):
            options_config.options.shuffle_layers_amount = expected_shuffle_layers_amount
        with self.assertRaises(Exception):
            options_config.options.post_fire_delay = expected_post_fire_delay
        with self.assertRaises(Exception):
            options_config.options.slew_delay = expected_slew_delay
        with self.assertRaises(Exception):
            options_config.options.sublayer_height_mm = expected_sublayer_height_mm
        with self.assertRaises(Exception):
            options_config.options.laser_thickness_mm = expected_laser_thickness_mm
        with self.assertRaises(Exception):
            options_config.options.scaling_factor = expected_scaling_factor
        with self.assertRaises(Exception):
            options_config.options.overlap_amount = expected_overlap_amount
        with self.assertRaises(Exception):
            options_config.options.use_shufflelayers = expected_use_shufflelayers
        with self.assertRaises(Exception):
            options_config.options.use_sublayers = expected_use_sublayers
        with self.assertRaises(Exception):
            options_config.options.use_overlap = expected_use_overlap
        with self.assertRaises(Exception):
            options_config.options.print_queue_delay = expected_print_queue_delay
        with self.assertRaises(Exception):
            options_config.options.pre_layer_delay = expected_pre_layer_delay
        with self.assertRaises(Exception):
            options_config.options.wait_after_move_milliseconds = expected_wait_after_move_milliseconds
        with self.assertRaises(Exception):
            options_config.options.write_wave_files = expected_write_wav_files
        with self.assertRaises(Exception):
            options_config.options.write_wave_files_folder = expected_write_wav_files_folder

    def test_can_create_json_and_load_from_json(self):
        expected_shuffle_layers_amount = 1.0
        expected_post_fire_delay = 5
        expected_slew_delay = 5
        expected_sublayer_height_mm = 0.
        expected_laser_thickness_mm = 0.1
        expected_scaling_factor = 1.0
        expected_overlap_amount = 1.0
        expected_use_shufflelayers = True
        expected_use_sublayers = True
        expected_use_overlap = True
        expected_print_queue_delay = 0.0
        expected_pre_layer_delay = 1.0
        expected_wait_after_move_milliseconds = 5
        expected_laser_offset = [0.1, 0.1]
        expected_write_wav_files = False
        expected_write_wav_files_folder = 'tmp'

        original_config = Configuration()
        original_config.options.shuffle_layers_amount        = expected_shuffle_layers_amount
        original_config.options.post_fire_delay              = expected_post_fire_delay
        original_config.options.slew_delay                   = expected_slew_delay
        original_config.options.sublayer_height_mm           = expected_sublayer_height_mm
        original_config.options.laser_thickness_mm           = expected_laser_thickness_mm
        original_config.options.overlap_amount               = expected_overlap_amount
        original_config.options.use_shufflelayers            = expected_use_shufflelayers
        original_config.options.use_sublayers                = expected_use_sublayers
        original_config.options.use_overlap                  = expected_use_overlap
        original_config.options.print_queue_delay            = expected_print_queue_delay
        original_config.options.pre_layer_delay              = expected_pre_layer_delay
        original_config.options.wait_after_move_milliseconds = expected_wait_after_move_milliseconds
        original_config.options.scaling_factor               = expected_scaling_factor
        original_config.options.write_wave_files             = expected_write_wav_files
        original_config.options.write_wave_files_folder      = expected_write_wav_files_folder

        actual_json = json.loads(original_config.toJson())
        config = Configuration(source=actual_json)

        self.assertEquals(type(expected_shuffle_layers_amount), type(config.options.shuffle_layers_amount))
        self.assertEquals(type(expected_post_fire_delay), type(config.options.post_fire_delay))
        self.assertEquals(type(expected_slew_delay), type(config.options.slew_delay))
        self.assertEquals(type(expected_sublayer_height_mm), type(config.options.sublayer_height_mm))
        self.assertEquals(type(expected_laser_thickness_mm), type(config.options.laser_thickness_mm))
        self.assertEquals(type(expected_scaling_factor), type(config.options.scaling_factor))
        self.assertEquals(type(expected_overlap_amount), type(config.options.overlap_amount))
        self.assertEquals(type(expected_use_shufflelayers), type(config.options.use_shufflelayers))
        self.assertEquals(type(expected_use_sublayers), type(config.options.use_sublayers))
        self.assertEquals(type(expected_use_overlap), type(config.options.use_overlap))
        self.assertEquals(type(expected_pre_layer_delay), type(config.options.pre_layer_delay))
        self.assertEquals(type(expected_wait_after_move_milliseconds), type(config.options.wait_after_move_milliseconds))
        self.assertEquals(type(expected_write_wav_files), type(config.options.write_wav_files))
        self.assertEquals(type(expected_write_wav_files_folder), type(config.options.write_wav_files_folder))

        self.assertEquals(expected_shuffle_layers_amount, config.options.shuffle_layers_amount)
        self.assertEquals(expected_post_fire_delay, config.options.post_fire_delay)
        self.assertEquals(expected_slew_delay, config.options.slew_delay)
        self.assertEquals(expected_sublayer_height_mm, config.options.sublayer_height_mm)
        self.assertEquals(expected_laser_thickness_mm, config.options.laser_thickness_mm)
        self.assertEquals(expected_scaling_factor, config.options.scaling_factor)
        self.assertEquals(expected_overlap_amount, config.options.overlap_amount)
        self.assertEquals(expected_use_shufflelayers, config.options.use_shufflelayers)
        self.assertEquals(expected_use_sublayers, config.options.use_sublayers)
        self.assertEquals(expected_use_overlap, config.options.use_overlap)
        self.assertEquals(expected_pre_layer_delay, config.options.pre_layer_delay)
        self.assertEquals(expected_wait_after_move_milliseconds, config.options.wait_after_move_milliseconds)
        self.assertEquals(expected_write_wav_files, config.options.write_wav_files)
        self.assertEquals(expected_write_wav_files_folder, config.options.write_wav_files_folder)


class ConfigurationTests(unittest.TestCase, test_helpers.TestHelpers):

    def test_set_should_fail_for_incorrect_values(self):
        expected_name = True

        expected_output_bit_depth = True
        expected_output_sample_frequency = True
        expected_on_modulation_frequency = True
        expected_off_modulation_frequency = True
        expected_input_bit_depth = True
        expected_input_sample_frequency = True

        expected_drips_per_mm = True
        expected_dripper_type = True
        expected_dripper_emulated_drips_per_second = True
        expected_max_lead_distance_mm = True
        expected_photo_zaxis_delay = True

        expected_max_deflection = True
        expected_calibration_height = True
        expected_calibration_lower_points = True
        expected_calibration_upper_points = True
        
        
        expected_use_serial_zaxis = "!@#!@#"
        expected_serial_port = True
        expected_serial_on = True
        expected_serial_off = True
        expected_layer_started = True
        expected_layer_ended = True
        expected_print_ended = True

        config = Configuration()

        with self.assertRaises(Exception):
            config.name = expected_name
        with self.assertRaises(Exception):
            config.audio.output.bit_depth = expected_output_bit_depth
        with self.assertRaises(Exception):
            config.audio.output.sample_rate = expected_output_sample_frequency
        with self.assertRaises(Exception):
            config.audio.output.modulation_on_frequency = expected_on_modulation_frequency
        with self.assertRaises(Exception):
            config.audio.output.modulation_off_frequency = expected_off_modulation_frequency
        with self.assertRaises(Exception):
            config.audio.input.bit_depth = expected_input_bit_depth
        with self.assertRaises(Exception):
            config.audio.input.sample_rate = expected_input_sample_frequency

        with self.assertRaises(Exception):
            config.dripper.drips_per_mm = expected_drips_per_mm
        with self.assertRaises(Exception):
            config.dripper.dripper_type = expected_dripper_type
        with self.assertRaises(Exception):
            config.dripper.emulated_drips_per_second = expected_dripper_emulated_drips_per_second
        with self.assertRaises(Exception):
            config.dripper.max_lead_distance_mm = expected_max_lead_distance_mm
        with self.assertRaises(Exception):
            config.dripper.photo_zaxis_delay = expected_photo_zaxis_delay

        with self.assertRaises(Exception):
            config.calibration.height = expected_calibration_height
        with self.assertRaises(Exception):
            config.calibration.lower_points = expected_calibration_lower_points
        with self.assertRaises(Exception):
            config.calibration.upper_points = expected_calibration_upper_points
        with self.assertRaises(Exception):
            config.calibration.max_deflection = expected_max_deflection

        with self.assertRaises(Exception):
            config.serial.on = expected_use_serial_zaxis
        with self.assertRaises(Exception):
            config.serial.port = expected_serial_port
        with self.assertRaises(Exception):
            config.serial.on_command = expected_serial_on
        with self.assertRaises(Exception):
            config.serial.off_command = expected_serial_off
        with self.assertRaises(Exception):
            config.serial.layer_started = expected_layer_started
        with self.assertRaises(Exception):
            config.serial.layer_ended = expected_layer_ended
        with self.assertRaises(Exception):
            config.serial.print_ended = expected_print_ended

    def test_can_create_json_and_load_from_json(self):
        expected_name = "PP"

        expected_drips_per_mm = 10.1
        expected_dripper_type = "audio"
        expected_dripper_emulated_drips_per_second = 1.0
        expected_max_lead_distance_mm = 0.2
        expected_photo_zaxis_delay = 2.0

        expected_max_deflection = 75.2
        expected_calibration_height = 1.0
        expected_calibration_lower_points = { (1.0, 1.0): ( 1.0,  1.0), (0.0, 1.0): (-1.0,  1.0), (1.0, 0.0): ( 1.0, -1.0), (0.0, 0.0): (-1.0, -1.0) }
        expected_calibration_upper_points = { (1.0, 1.0): ( 1.0,  1.0), (0.0, 1.0): (-1.0,  1.0), (1.0, 0.0): ( 1.0, -1.0), (0.0, 0.0): (-1.0, -1.0) }

        expected_use_serial_zaxis = True
        expected_serial_port = "COM2"
        expected_serial_on = "12"
        expected_serial_off = "13"
        expected_layer_started = "14"
        expected_layer_ended = "15"
        expected_print_ended = "Z"

        original_config = Configuration()
        original_config.name                                 = expected_name

        original_config.dripper.drips_per_mm                 = expected_drips_per_mm
        original_config.dripper.dripper_type                 = expected_dripper_type
        original_config.dripper.emulated_drips_per_second    = expected_dripper_emulated_drips_per_second
        original_config.dripper.max_lead_distance_mm         = expected_max_lead_distance_mm
        original_config.dripper.photo_zaxis_delay            = expected_photo_zaxis_delay

        original_config.calibration.max_deflection           = expected_max_deflection
        original_config.calibration.height                   = expected_calibration_height
        original_config.calibration.lower_points             = expected_calibration_lower_points
        original_config.calibration.upper_points             = expected_calibration_upper_points

        original_config.serial.on                            = expected_use_serial_zaxis
        original_config.serial.port                          = expected_serial_port
        original_config.serial.on_command                    = expected_serial_on
        original_config.serial.off_command                   = expected_serial_off
        original_config.serial.layer_started                 = expected_layer_started
        original_config.serial.layer_ended                   = expected_layer_ended
        original_config.serial.print_ended                   = expected_print_ended

        actual_json = json.loads(original_config.toJson())

        config = Configuration(source=actual_json)

        self.maxDiff = None
        self.assertEquals(type(expected_name), type(config.name))
        self.assertEquals(expected_name, config.name)

        self.assertEquals(expected_drips_per_mm, config.dripper.drips_per_mm)
        self.assertEquals(expected_max_lead_distance_mm, config.dripper.max_lead_distance_mm)
        self.assertEquals(type(expected_dripper_type), type(config.dripper.dripper_type))
        self.assertEquals(expected_dripper_type, config.dripper.dripper_type)
        self.assertEquals(expected_dripper_emulated_drips_per_second, config.dripper.emulated_drips_per_second)
        self.assertEquals(expected_photo_zaxis_delay, config.dripper.photo_zaxis_delay)

        self.assertEquals(expected_max_deflection, config.calibration.max_deflection)
        self.assertEquals(expected_calibration_height, config.calibration.height)
        self.assertEquals(expected_calibration_lower_points, config.calibration.lower_points)
        self.assertEquals(expected_calibration_upper_points, config.calibration.upper_points)

        self.assertEquals(expected_use_serial_zaxis, config.serial.on)
        self.assertEquals(type(expected_serial_port), type(config.serial.port))
        self.assertEquals(expected_serial_port, config.serial.port)
        self.assertEquals(type(expected_serial_on), type(config.serial.on_command))
        self.assertEquals(expected_serial_on, config.serial.on_command)
        self.assertEquals(type(expected_serial_off), type(config.serial.off_command))
        self.assertEquals(expected_serial_off, config.serial.off_command)
        self.assertEquals(type(expected_layer_started), type(config.serial.layer_started))
        self.assertEquals(expected_layer_started, config.serial.layer_started)
        self.assertEquals(type(expected_layer_ended), type(config.serial.layer_ended))
        self.assertEquals(expected_layer_ended, config.serial.layer_ended)
        self.assertEquals(type(expected_print_ended), type(config.serial.print_ended))
        self.assertEquals(expected_print_ended, config.serial.print_ended)

if __name__ == '__main__':
    unittest.main()
