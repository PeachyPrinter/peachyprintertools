import types
import logging

from peachyprinter.infrastructure.zaxis import SerialDripZAxis
from peachyprinter.infrastructure.communicator import UsbPacketCommunicator
from peachyprinter.infrastructure.layer_generators import CureTestGenerator
from peachyprinter.infrastructure.commander import SerialCommander
logger = logging.getLogger('peachy')


class InfoMixIn(object):
    def get_info_version_number(self):
        return "TBD"

    def get_info_serial_number(self):
        return "TBD"

    def get_info_hardware_version_number(self):
        return "TBD"

    def get_info_firmware_version_number(self):
        return "TBD"


class DripperSetupMixIn(object):

    '''Depricated use get_dripper_drips_per_mm'''
    def get_drips_per_mm(self):
        logging.warning("Depricated use get_dripper_drips_per_mm")
        return self.get_dripper_drips_per_mm()

    '''Returns Drips Per mm'''
    def get_dripper_drips_per_mm(self):
        return self._current_config.dripper.drips_per_mm

    '''Returns the configured Dripper Type'''
    def get_dripper_type(self):
        return self._current_config.dripper.dripper_type

    '''Depricated use get_dripper_emulated_drips_per_second'''
    def get_emulated_drips_per_second(self):
        logging.warning("Depricated use get_dripper_emulated_drips_per_second")
        return self.get_dripper_emulated_drips_per_second()

    '''Gets the drips per second to be emulated'''
    def get_dripper_emulated_drips_per_second(self):
        return self._current_config.dripper.emulated_drips_per_second

    '''Depricated use get_dripper_photo_zaxis_delay'''
    def get_photo_zaxis_delay(self):
        logging.warning("Depricated use get_dripper_photo_zaxis_delay")
        return self.get_dripper_photo_zaxis_delay()

    '''Gets the photo delay in seconds'''
    def get_dripper_photo_zaxis_delay(self):
        return self._current_config.dripper.photo_zaxis_delay

    '''Depricated use set_dripper_drips_per_mm'''
    def set_drips_per_mm(self, drips):
        logging.warning("Depricated use set_dripper_drips_per_mm")
        self.set_dripper_drips_per_mm(drips)

    '''Sets Drips Per mm'''
    def set_dripper_drips_per_mm(self, drips):
        self._current_config.dripper.drips_per_mm = drips
        if self._drip_detector:
            self._drip_detector.set_drips_per_mm(drips)
        self.save()

    '''Sets the configured Dripper Type'''
    def set_dripper_type(self, value):
        self._current_config.dripper.dripper_type = value
        self.save()

    '''Depricated use set_dripper_emulated_drips_per_second'''
    def set_emulated_drips_per_second(self, value):
        logging.warning("Depricated use set_dripper_emulated_drips_per_second")
        self.set_dripper_emulated_drips_per_second(value)

    '''Sets the drips per second to be emulated'''
    def set_dripper_emulated_drips_per_second(self, value):
        self._current_config.dripper.emulated_drips_per_second = value
        self.save()

    '''Depricated use set_dripper_photo_zaxis_delay'''
    def set_photo_zaxis_delay(self, value):
        logging.warning("Depricated use set_dripper_photo_zaxis_delay")
        self.set_dripper_photo_zaxis_delay(value)

    '''Sets the photo delay in seconds'''
    def set_dripper_photo_zaxis_delay(self, value):
        self._current_config.dripper.photo_zaxis_delay = value
        self.save()

    '''Sets the drip count back to 0'''
    def reset_drips(self):
        self._drip_detector.reset()

    '''Turns on the counting of drips. Stop must be called to end this.'''
    def start_counting_drips(self, drip_call_back=None):
        self.drip_call_back = drip_call_back
        if self._current_config.serial.on:
            self._commander = SerialCommander(self._current_config.serial.port)
        self._change_dripper()

    def _change_dripper(self):
        self._stop_current_dripper()
        if self._current_config.dripper.dripper_type == 'emulated':
            pass
        elif self._current_config.dripper.dripper_type == 'photo':
            pass
        elif self._current_config.dripper.dripper_type == 'microcontroller':
            self._communicator = UsbPacketCommunicator()
            self._communicator.start()
            self._drip_detector = SerialDripZAxis(self._communicator, 1, 0.0, drip_call_back=self.drip_call_back)

    def _stop_current_dripper(self):
        if self._communicator:
            self._communicator.close()
        if self._drip_detector:
            self._drip_detector.close()
            self._drip_detector = None

    '''Turns off the counting of drips if counting'''
    def stop_counting_drips(self):
        if self._commander:
            self._commander.close()
        self._stop_current_dripper()

    def send_dripper_on_command(self):
        if self._commander:
            self._commander.send_command(self._current_config.serial.on_command)
        else:
            raise Exception("Serial not Started")

    def send_dripper_off_command(self):
        if self._commander:
            self._commander.send_command(self._current_config.serial.off_command)
        else:
            raise Exception("Serial not Started")


class CureTestSetupMixIn(object):

    '''Returns a layer generator that can be used with the print API to print a cure test.'''
    def get_cure_test(self, base_height, total_height, start_speed, stop_speed):
        self._verify_cure_test_settings(base_height, total_height, start_speed, stop_speed)
        return CureTestGenerator(base_height, total_height, start_speed, stop_speed, self._current_config.options.sublayer_height_mm)

    '''Based on provided setting returns the speed the printer was going at the specified height'''
    def get_speed_at_height(self, base_height, total_height, start_speed, stop_speed, height):
        self._verify_cure_test_settings(base_height, total_height, start_speed, stop_speed)
        if (height < base_height or height > total_height):
            logger.warning('Height of ideal cure must be in range of cure test')
            raise Exception('Height of ideal cure must be in range of cure test')
        actual_height = total_height - base_height
        desired_height = height - base_height
        speed_delta = stop_speed -start_speed
        return start_speed + (speed_delta / actual_height * desired_height)

    def _verify_cure_test_settings(self, base_height, total_height, start_speed, stop_speed):
        try:
            float(base_height)
            float(total_height)
            float(start_speed)
            float(stop_speed)
        except ValueError:
            logger.warning('Entries for cure test settings must be numeric')
            raise Exception('Entries for cure test settings must be numeric')
        if(total_height <= base_height):
            logger.warning('total_height must be greater then base_height')
            raise Exception('total_height must be greater then base_height')
        if(start_speed > stop_speed):
            logger.warning('start_speed must be less then stop speed')
        if(total_height <= 0):
            logger.warning('total_height must be a positive number')
            raise Exception('start_speed must be less then stop speed')
        if(start_speed <= 0):
            logger.warning( 'start_speed must be positive')
            raise Exception( 'start_speed must be positive')
        if(stop_speed <= 0):
            logger.warning('stop_speed must be positive')
            raise Exception('stop_speed must be positive')
        if(stop_speed <= start_speed):
            logger.warning('stop_speed must faster the start_speed')
            raise Exception('stop_speed must faster the start_speed')
        if(base_height < 0):
            logger.warning('base_height cannot be negitive')
            raise Exception('base_height cannot be negitive')

    '''Sets the base_height for Cure Rate test.'''
    def set_cure_rate_base_height(self, base_height):
        if (self._zero_or_positive_float(float(base_height))):
            self._current_config.cure_rate.base_height = base_height
        else:
            logger.warning('Base height must be 0 or positive')
            raise Exception('Specified base height must be positive')

    '''Sets the total_height for Cure Rate test.'''
    def set_cure_rate_total_height(self, total_height):
        if (self._positive_float(float(total_height))):
            self._current_config.cure_rate.total_height = total_height
        else:
            logger.warning('Total height must be positive')
            raise Exception('Specified total height must be positive')

    '''Sets the start_speed for Cure Rate test.'''
    def set_cure_rate_start_speed(self, start_speed):
        if (self._positive_float(float(start_speed))):
            self._current_config.cure_rate.start_speed = start_speed
        else:
            logger.warning('start_speed must be positive')
            raise Exception('Specified start speed must be positive')

    '''Sets the finish_speed for Cure Rate test.'''
    def set_cure_rate_finish_speed(self, finish_speed):
        if (self._positive_float(float(finish_speed))):
            self._current_config.cure_rate.finish_speed = finish_speed
        else:
            logger.warning('finish_speed must be positive')
            raise Exception('Specified finish speed must be positive')

    '''Sets the draw_speed for Cure Rate test.'''
    def set_cure_rate_draw_speed(self, draw_speed):
        if (self._positive_float(float(draw_speed))):
            self._current_config.cure_rate.draw_speed = draw_speed
        else:
            logger.warning('draw_speed must be positive')
            raise Exception('Specified draw speed must be positive')

    '''Sets the use_draw_speed for Cure Rate test.'''
    def set_cure_rate_use_draw_speed(self, use_draw_speed):
        self._current_config.cure_rate.use_draw_speed = use_draw_speed

    '''Depricated use set_cure_rate_override_laser_power'''
    def set_override_laser_power(self, override_laser_power):
        logging.warning("set_override_laser_power(self, override_laser_ is Depricated use set_cure_rate_override_laser_power")
        self.set_cure_rate_override_laser_power(override_laser_power)

    '''Depricated use set_cure_rate_override_laser_power_amount'''
    def set_override_laser_power_amount(self, override_laser_power_amount):
        logging.warning("set_override_laser_power_amount(self, override_laser_power_a is Depricated use set_cure_rate_override_laser_power_amount")
        self.set_cure_rate_override_laser_power(override_laser_power_amount)

    '''Sets the override_laser_power for Cure Rate'''
    def set_cure_rate_override_laser_power(self, override_laser_power):
        self._current_config.cure_rate.override_laser_power = override_laser_power

    '''Sets the draw_speed for Cure Rate test.'''
    def set_cure_rate_override_laser_power_amount(self, override_laser_power_amount):
        if override_laser_power_amount >= 0.1568:
            raise Exception("Laser Power is too high")

        if (self._positive_percentage(float(override_laser_power_amount))):
            self._current_config.cure_rate.override_laser_power_amount = override_laser_power_amount
        else:
            logger.warning('override_laser_power_amount must be positive percentage between 0 and 1')
            raise Exception('Specified override_laser_power_amount must be positive')

    '''Gets the base_height for Cure Rate test.'''
    def get_cure_rate_base_height(self):
        return self._current_config.cure_rate.base_height

    '''Gets the total_height for Cure Rate test.'''
    def get_cure_rate_total_height(self):
        return self._current_config.cure_rate.total_height

    '''Gets the start_speed for Cure Rate test.'''
    def get_cure_rate_start_speed(self):
        return self._current_config.cure_rate.start_speed

    '''Gets the finish_speed for Cure Rate test.'''
    def get_cure_rate_finish_speed(self):
        return self._current_config.cure_rate.finish_speed

    '''Gets the draw_speed for Cure Rate test.'''
    def get_cure_rate_draw_speed(self):
        return self._current_config.cure_rate.draw_speed

    '''Gets the usedraw_speed for Cure Rate test.'''
    def get_cure_rate_use_draw_speed(self):
        return self._current_config.cure_rate.use_draw_speed

    '''Depricated get_cure_rate_override_laser_power'''
    def get_override_laser_power(self):
        logging.warning("get_override_laser_power is Depricated use get_cure_rate_override_laser_power")
        return self.get_cure_rate_override_laser_power()

    '''Depricated get_cure_rate_override_laser_power_amount'''
    def get_override_laser_power_amount(self):
        logging.warning("get_override_laser_power_amount is Depricated use get_cure_rate_override_laser_power_amount")
        return self.get_cure_rate_override_laser_power_amount()

    '''Gets the override_laser_power for Cure Rate'''
    def get_cure_rate_override_laser_power(self):
        return self._current_config.cure_rate.override_laser_power

    '''Gets the override_laser_power_amount for Cure Rate'''
    def get_cure_rate_override_laser_power_amount(self):
        return self._current_config.cure_rate.override_laser_power_amount


class OptionsSetupMixIn(object):

    '''Returns the wait after move milliseconds'''
    def get_options_wait_after_move_milliseconds(self):
        return self._current_config.options.wait_after_move_milliseconds

    def get_wait_after_move_milliseconds(self):
        logger.warning("get_wait_after_move_milliseconds is depricated use get_options_wait_after_move_milliseconds")
        return self.get_options_wait_after_move_milliseconds()

    '''Returns the pre layer delay'''
    def get_options_pre_layer_delay(self):
        return self._current_config.options.pre_layer_delay

    def get_pre_layer_delay(self):
        logger.warning("get_pre_layer_delay is depricated use get_options_pre_layer_delay")
        return self.get_options_pre_layer_delay()

    '''Returns the print queue delay'''
    def get_options_print_queue_delay(self):
        return self._current_config.options.print_queue_delay

    def get_print_queue_delay(self):
        logger.warning("get_print_queue_delay is depricated use get_options_print_queue_delay")
        return self.get_options_print_queue_delay()

    '''Returns the current setting for laser thickness'''
    def get_options_laser_thickness_mm(self):
        return self._current_config.options.laser_thickness_mm

    def get_laser_thickness_mm(self):
        logger.warning("get_laser_thickness_mm is depricated use get_options_laser_thickness_mm")
        return self.get_options_laser_thickness_mm()

    '''Returns the current setting for scaling factor'''
    def get_options_scaling_factor(self):
        return self._current_config.options.scaling_factor

    def get_scaling_factor(self):
        logger.warning("get_scaling_factor is depricated use get_options_scaling_factor")
        return self.get_options_scaling_factor()

    '''Gets the Sublayer height sublayers are added between layers for grater definition'''
    def get_options_sublayer_height_mm(self):
        return self._current_config.options.sublayer_height_mm

    def get_sublayer_height_mm(self):
        logger.warning("get_sublayer_height_mm is depricated use get_options_sublayer_height_mm")
        return self.get_options_sublayer_height_mm()

    '''Gets the Max Lead Distance or the amount the z layer can be ahead before layers are skipped'''
    def get_options_max_lead_distance_mm(self):
        return self._current_config.dripper.max_lead_distance_mm

    def get_max_lead_distance_mm(self):
        logger.warning("get_max_lead_distance_mm is depricated use get_options_max_lead_distance_mm")
        return self.get_options_max_lead_distance_mm()

    '''Gets the Post Fire Delay for each layer'''
    def get_options_post_fire_delay(self):
        return self._current_config.options.post_fire_delay

    def get_post_fire_delay(self):
        logger.warning("get_post_fire_delay is depricated use get_options_post_fire_delay")
        return self.get_options_post_fire_delay()

    '''Gets the Slew Delay for each layer'''
    def get_options_slew_delay(self):
        return self._current_config.options.slew_delay

    def get_slew_delay(self):
        logger.warning("get_slew_delay is depricated use get_options_slew_delay")
        return self.get_options_slew_delay()

    '''Gets the Overlap Amount for each layer'''
    def get_options_overlap_amount_mm(self):
        return self._current_config.options.overlap_amount

    def get_overlap_amount_mm(self):
        logger.warning("get_overlap_amount_mm is depricated use get_options_overlap_amount_mm")
        return self.get_options_overlap_amount_mm()

    '''Gets the Shuffle Layers Amount for each layer'''
    def get_options_shuffle_layers_amount(self):
        return self._current_config.options.shuffle_layers_amount

    def get_shuffle_layers_amount(self):
        logger.warning("get_shuffle_layers_amount is depricated use get_options_shuffle_layers_amount")
        return self.get_options_shuffle_layers_amount()

    '''Gets the Shuffle layers setting'''
    def get_options_use_shufflelayers(self):
        return self._current_config.options.use_shufflelayers

    def get_use_shufflelayers(self):
        logger.warning("get_use_shufflelayers is depricated use get_options_use_shufflelayers")
        return self.get_options_use_shufflelayers()

    '''Gets the Sub layers setting'''
    def get_options_use_sublayers(self):
        return self._current_config.options.use_sublayers

    def get_use_sublayers(self):
        logger.warning("get_use_sublayers is depricated use get_options_use_sublayers")
        return self.get_options_use_sublayers()

    '''Gets the Overlap layers setting'''
    def get_options_use_overlap(self):
        return self._current_config.options.use_overlap

    def get_use_overlap(self):
        logger.warning("get_use_overlap is depricated use get_options_use_overlap")
        return self.get_options_use_overlap()

    def set_wait_after_move_milliseconds(self, delay_milliseconds):
        logger.warning(" set_wait_after_move_milliseconds is depricated use set_options_wait_after_move_milliseconds")
        self.set_options_wait_after_move_milliseconds(delay_milliseconds)

    '''Sets the wait after move milliseconds'''
    def set_options_wait_after_move_milliseconds(self, delay_milliseconds):
        if self._zero_or_positive_int(delay_milliseconds):
            self._current_config.options.wait_after_move_milliseconds = delay_milliseconds
            self.save()
        else:
            raise Exception("Wait after move milliseconds must be a positive int number")

    def set_pre_layer_delay(self, delay):
        logger.warning(" is depricated use set_options_pre_layer_delay")
        self.set_options_pre_layer_delay(delay)

    '''Sets the pre layer delay'''
    def set_options_pre_layer_delay(self, delay):
        if self._zero_or_positive_float(delay):
            self._current_config.options.pre_layer_delay = delay
            self.save()
        else:
            raise Exception("Print queue delay must be a positive floating point number")

    def set_print_queue_delay(self, delay):
        logger.warning(" is depricated use set_options_print_queue_delay")
        self.set_options_print_queue_delay(delay)

    '''Sets the print queue delay'''
    def set_options_print_queue_delay(self, delay):
        if self._zero_or_positive_float(delay):
            self._current_config.options.print_queue_delay = delay
            self.save()
        else:
            raise Exception("Print queue delay must be a positive floating point number")

    def set_laser_thickness_mm(self, thickness_mm):
        logger.warning("set_laser_thickness_mm is depricated use set_options_laser_thickness_mm")
        self.set_options_laser_thickness_mm(thickness_mm)

    '''Sets the laser thickness in mm'''
    def set_options_laser_thickness_mm(self, thickness_mm):
        if self._positive_float(thickness_mm):
            self._current_config.options.laser_thickness_mm = thickness_mm
            self.save()
        else:
            raise Exception("Laser thickness must be a positive floating point number")

    def set_scaling_factor(self, scaling_factor):
        logger.warning("set_scaling_factor is depricated use set_options_scaling_factor")
        self.set_options_scaling_factor(scaling_factor)

    '''Sets the scaling factor in mm'''
    def set_options_scaling_factor(self, scaling_factor):
        if self._positive_float(scaling_factor):
            self._current_config.options.scaling_factor = scaling_factor
            self.save()
        else:
            raise Exception("Scaling Factor must be a positive floating point number")

    def set_sublayer_height_mm(self, thickness_mm):
        logger.warning("set_sublayer_height_mm is depricated use set_options_sublayer_height_mm")
        self.set_options_sublayer_height_mm(thickness_mm)

    '''Sets the Sublayer height sublayers are added between layers for grater definition'''
    def set_options_sublayer_height_mm(self, thickness_mm):
        if self._positive_float(thickness_mm):
            self._current_config.options.sublayer_height_mm = thickness_mm
            self.save()
        else:
            raise Exception("Sublayer height must be a positive floating point number")

    def set_max_lead_distance_mm(self, lead_distance_mm):
        logger.warning("set_max_lead_distance_mm is depricated use set_options_max_lead_distance_mm")
        self.set_options_max_lead_distance_mm(lead_distance_mm)

    '''Sets the Max Lead Distance or the amount the z layer can be ahead before layers are skipped'''
    def set_options_max_lead_distance_mm(self, lead_distance_mm):
        if self._zero_or_positive_float(lead_distance_mm):
            self._current_config.dripper.max_lead_distance_mm = lead_distance_mm
            self.save()
        else:
            raise Exception("Max lead distance height must be a positive floating point number")

    def set_overlap_amount_mm(self, overlap_amount):
        logger.warning("set_overlap_amount_mm is depricated use set_options_overlap_amount_mm")
        self.set_options_overlap_amount_mm(overlap_amount)

    '''Sets the Overlap Amount for each layer'''
    def set_options_overlap_amount_mm(self, overlap_amount):
        if self._positive_float(overlap_amount):
            self._current_config.options.overlap_amount = overlap_amount
            self.save()
        else:
            raise Exception("Overlap Amount must be a positive floating point number")

    def set_post_fire_delay(self, post_fire_delay):
        logger.warning("set_post_fire_delay is depricated use set_options_post_fire_delay")
        self.set_options_post_fire_delay(post_fire_delay)

    '''Sets the Post Fire Delay for each layer'''
    def set_options_post_fire_delay(self, post_fire_delay):
        if self._zero_or_positive_int(post_fire_delay):
            self._current_config.options.post_fire_delay = post_fire_delay
            self.save()
        else:
            raise Exception("Post Fire Delay must be a positive integer number")

    def set_slew_delay(self, slew_delay):
        logger.warning("set_slew_delay is depricated use set_options_slew_delay")
        self.set_options_slew_delay(slew_delay)

    '''Sets the Slew Delay for each layer'''
    def set_options_slew_delay(self, slew_delay):
        if self._zero_or_positive_int(slew_delay):
            self._current_config.options.slew_delay = slew_delay
            self.save()
        else:
            raise Exception("Post Fire Delay must be a positive integer number")

    def set_shuffle_layers_amount(self, shuffle_layers_amount):
        logger.warning("set_shuffle_layers_amount is depricated use set_options_shuffle_layers_amount")
        self.set_options_shuffle_layers_amount(shuffle_layers_amount)

    '''Sets the Shuffle Layers Amount for each layer'''
    def set_options_shuffle_layers_amount(self, shuffle_layers_amount):
        if self._positive_float(shuffle_layers_amount):
            self._current_config.options.shuffle_layers_amount = shuffle_layers_amount
            self.save()
        else:
            raise Exception("Shuffle Layers Amount must be a positive floating point number")

    def set_use_shufflelayers(self, use_shufflelayers):
        logger.warning("set_use_shufflelayers is depricated use set_options_use_shufflelayers")
        self.set_options_use_shufflelayers(use_shufflelayers)

    '''Sets the Shuffle layers setting'''
    def set_options_use_shufflelayers(self, use_shufflelayers):
        if (type(use_shufflelayers) == types.BooleanType):
            self._current_config.options.use_shufflelayers = use_shufflelayers
            self.save()
        else:
            raise Exception("Use Shuffle Layers must be True or False")

    def set_use_sublayers(self, use_sublayers):
        logger.warning("set_use_sublayers is depricated use set_options_use_sublayers")
        self.set_options_use_sublayers(use_sublayers)

    '''Sets the Sub layers setting'''
    def set_options_use_sublayers(self, use_sublayers):
        if (type(use_sublayers) == types.BooleanType):
            self._current_config.options.use_sublayers = use_sublayers
            self.save()
        else:
            raise Exception("Use SubLayers must be True or False")

    def set_use_overlap(self, use_overlap):
        logger.warning("set_use_overlap is depricated use set_options_use_overlap")
        self.set_options_use_overlap(use_overlap)

    '''Sets the Overlap layers setting'''
    def set_options_use_overlap(self, use_overlap):
        if (type(use_overlap) == types.BooleanType):
            self._current_config.options.use_overlap = use_overlap
            self.save()
        else:
            raise Exception("Use Overlap must be True or False")


class EmailSetupMixin(object):

    def set_email_on(self, on):
        self._current_config.email.on = on

    def set_email_port(self, port):
        self._current_config.email.port = port

    def set_email_host(self, host):
        self._current_config.email.host = host

    def set_email_sender(self, sender):
        self._current_config.email.sender = sender

    def set_email_recipient(self, recipient):
        self._current_config.email.recipient = recipient

    def set_email_username(self, username):
        self._current_config.email.username = username

    def set_email_password(self, password):
        self._current_config.email.password = password

    def get_email_on(self):
        return self._current_config.email.on

    def get_email_port(self):
        return self._current_config.email.port

    def get_email_host(self):
        return self._current_config.email.host

    def get_email_sender(self):
        return self._current_config.email.sender

    def get_email_recipient(self):
        return self._current_config.email.recipient

    def get_email_username(self):
        return self._current_config.email.username

    def get_email_password(self):
        return self._current_config.email.password


class SerialSetupMixin(object):

    def get_serial_enabled(self):
        return self._current_config.serial.on

    def get_serial_port(self):
        return self._current_config.serial.port

    def get_serial_on_command(self):
        return self._current_config.serial.on_command

    def get_serial_off_command(self):
        return self._current_config.serial.off_command

    def get_layer_started_command(self):
        logger.warn("configuration_api.get_layer_started_command is depricated use get_serial_layer_started_command")
        return self.get_serial_layer_started_command()

    def get_layer_ended_command(self):
        logger.warn("configuration_api.get_layer_ended_command is depricated use get_serial_layer_ended_command")
        return self.get_serial_layer_ended_command()

    def get_print_ended_command(self):
        logger.warn("configuration_api.get_print_ended_command is depricated use get_serial_print_ended_command")
        return self.get_serial_print_ended_command()

    def get_serial_layer_started_command(self):
        return self._current_config.serial.layer_started

    def get_serial_layer_ended_command(self):
        return self._current_config.serial.layer_ended

    def get_serial_print_ended_command(self):
        return self._current_config.serial.print_ended

    def set_serial_enabled(self, enabled):
        logger.info("CFG Setting changed: serial_enabled -> %s" % enabled)
        self._current_config.serial.on = enabled
        self.save()

    def set_serial_port(self, port):
        logger.info("Setting changed: serial_port -> %s" % port)
        self._current_config.serial.port = port
        self.save()

    def set_serial_on_command(self, on_command):
        logger.info("Setting changed: serial_on_command -> %s" % on_command)
        self._current_config.serial.on_command = on_command
        self.save()

    def set_serial_off_command(self, off_command):
        logger.info("Setting changed: serial_off_command -> %s" % off_command)
        self._current_config.serial.off_command = off_command
        self.save()

    def set_layer_started_command(self, layer_started):
        logger.info("Setting changed: layer_started_command -> %s" % layer_started)
        logger.warn("configuration_api.set_layer_started_command is depricated use set_serial_layer_started_command")
        self.set_serial_layer_started_command(self, layer_started)

    def set_layer_ended_command(self, layer_ended):
        logger.info("Setting changed: layer_ended_command -> %s" % layer_ended)
        logger.warn("configuration_api.set_layer_ended_command is depricated use set_serial_layer_ended_command")
        self.set_serial_layer_ended_command(self, layer_ended)

    def set_print_ended_command(self, print_ended):
        logger.info("Setting changed: print_ended_command -> %s" % print_ended)
        logger.warn("configuration_api.set_print_ended_command is depricated use set_serial_print_ended_command")
        self.set_serial_print_ended_command(self, print_ended)

    def set_serial_layer_started_command(self, layer_started):
        logger.info("Setting changed: serial_layer_started_command -> %s" % layer_started)
        self._current_config.serial.layer_started = layer_started
        self.save()

    def set_serial_layer_ended_command(self, layer_ended):
        logger.info("Setting changed: serial_layer_ended_command -> %s" % layer_ended)
        self._current_config.serial.layer_ended = layer_ended
        self.save()

    def set_serial_print_ended_command(self, print_ended):
        logger.info("Setting changed: serial_print_ended_command -> %s" % print_ended)
        self._current_config.serial.print_ended = print_ended
        self.save()


class CircutSetupMixIn(object):
    _CIRCUT_TYPES = ['Analog', 'Digital']

    def set_circut_type(self, circut_type):
        if not circut_type in self._CIRCUT_TYPES:
            logger.warning("Specified circut type %s is invalid" % circut_type)
            raise Exception("Specified circut type %s is invalid" % circut_type)
        self._current_config.circut.circut_type = circut_type

    def set_micro_com_port(self, port):
        self._current_config.micro_com.port = port

    def set_micro_com_rate(self, rate):
        self._current_config.micro_com.rate = rate

    def set_micro_com_header(self, header):
        self._current_config.micro_com.header = header

    def set_micro_com_footer(self, footer):
        self._current_config.micro_com.footer = footer

    def set_micro_com_escape(self, escape):
        self._current_config.micro_com.escape = escape

    def set_circut_version(self, version):
        self._current_config.circut.version = version

    def get_micro_com_port(self):
        return self._current_config.micro_com.port

    def get_micro_com_rate(self):
        return self._current_config.micro_com.rate

    def get_micro_com_header(self):
        return self._current_config.micro_com.header

    def get_micro_com_footer(self):
        return self._current_config.micro_com.footer

    def get_micro_com_escape(self):
        return self._current_config.micro_com.escape

    def get_circut_type(self):
        return self._current_config.circut.circut_type

    def get_circut_version(self):
        return self._current_config.circut.version


'''Api for adjusting setting for the peachy current_printer.
This API is still in active development and as is subject dramatic change'''


class ConfigurationAPI(
    InfoMixIn,
    DripperSetupMixIn,
    CureTestSetupMixIn,
    OptionsSetupMixIn,
    EmailSetupMixin,
    SerialSetupMixin,
    CircutSetupMixIn
    ):

    def __init__(self, configuration_manager):
        self._configuration_manager = configuration_manager
        self._current_config = None
        self._drip_detector = None
        self._communicator = None
        self._marked_drips = None
        self._commander = None

    '''Returns the currently loaded printer name'''
    def current_printer(self):
        if self._current_config:
            return self._current_config.name
        else:
            # logger.debug('Current config missing')
            return None

    '''Returns the current printer config in json'''
    def get_current_config(self):
        return self._current_config

    '''Returns a list of available printers'''
    def get_available_printers(self):
        return self._configuration_manager.list()

    '''Adds a printer by name with default settings'''
    def add_printer(self, name):
        self._current_config = self._configuration_manager.new(name)
        self.save()

    '''Loads a previous configured printer by name'''
    def load_printer(self, name):
        self._current_config = self._configuration_manager.load(name)
        # logger.debug("Loaded config:\n%s" % self._current_config)

    '''Saves the currently selected config'''
    def save(self):
        self._configuration_manager.save(self._current_config)

    def _positive_float(self, value):
        return (isinstance(value, types.FloatType) and value > 0.0)

    def _positive_percentage(self, value):
        return (isinstance(value, types.FloatType) and value >= 0.0 and value <= 1.0)

    def _zero_or_positive_float(self, value):
        return (isinstance(value, types.FloatType) and value >= 0.0)

    def _zero_or_positive_int(self, value):
        return (isinstance(value, types.IntType) and value >= 0.0)
