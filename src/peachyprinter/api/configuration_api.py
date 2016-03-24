import types
import logging

from peachyprinter.infrastructure.zaxis import SerialDripZAxis
from peachyprinter.infrastructure.communicator import UsbPacketCommunicator
from peachyprinter.infrastructure.layer_generators import CureTestGenerator
from peachyprinter.infrastructure.commander import SerialCommander
logger = logging.getLogger('peachy')


class InfoMixIn(object):
    '''This is a Mixin for the ConfigurationAPI and exists only for organizational purposes'''

    def get_info_version_number(self):
        return "TBD"

    def get_info_serial_number(self):
        '''Returns the serial number of the atttached printer'''

        return self._current_config.circut.serial_number

    def get_info_hardware_version_number(self):
        '''Returns the revision number of the current hardware'''

        return self._current_config.circut.hardware_revision

    def get_info_firmware_version_number(self):
        '''Returns th current firmware revision of the hardware'''

        return self._current_config.circut.software_revision

    def get_info_firmware_data_rate(self):
        '''Returns the expected data rate for the attached hardware'''

        return self._current_config.circut.data_rate

    def get_info_print_queue_length(self):
        '''The length of the USB buffer in packets whilst printing'''

        return self._current_config.circut.print_queue_length

    def get_info_calibration_queue_length(self):
        '''The length of the USB buffer in packets whilst calibrating (typically shorter the print to encourage responsiviness)'''
        return self._current_config.circut.calibration_queue_length

    def set_info_print_queue_length(self, length):
        '''Sets the circut queue length'''

        if self._zero_or_positive_int(length):
            self._current_config.circut.print_queue_length = length
            self.save()
        else:
            raise Exception("Print queue length must be a positive integer")

    def set_info_calibration_queue_length(self, length):
        '''Sets the circut calibration queue length'''

        if self._zero_or_positive_int(length):
            self._current_config.circut.calibration_queue_length = length
            self.save()
        else:
            raise Exception("Calibration queue length must be a positive integer")


class DripperSetupMixIn(object):
    '''This is a Mixin for the ConfigurationAPI and exists only for organizational purposes'''

    def get_dripper_drips_per_mm(self):
        '''Returns Drips Per mm'''

        return self._current_config.dripper.drips_per_mm

    def get_dripper_type(self):
        '''Returns the configured Dripper Type'''

        return self._current_config.dripper.dripper_type

    def get_dripper_emulated_drips_per_second(self):
        '''Gets the drips per second to be emulated'''

        return self._current_config.dripper.emulated_drips_per_second

    def get_dripper_photo_zaxis_delay(self):
        '''Gets the photo delay in seconds'''

        return self._current_config.dripper.photo_zaxis_delay

    def set_dripper_drips_per_mm(self, drips):
        '''Sets Drips Per mm'''

        self._current_config.dripper.drips_per_mm = drips
        if self._drip_detector:
            self._drip_detector.set_drips_per_mm(drips)
        self.save()

    def set_dripper_type(self, value):
        '''Sets the configured Dripper Type'''

        self._current_config.dripper.dripper_type = value
        self.save()

    def set_dripper_emulated_drips_per_second(self, value):
        '''Sets the drips per second to be emulated'''

        self._current_config.dripper.emulated_drips_per_second = value
        self.save()

    def set_dripper_photo_zaxis_delay(self, value):
        '''Sets the photo delay in seconds'''

        self._current_config.dripper.photo_zaxis_delay = value
        self.save()

    def reset_drips(self):
        '''Sets the drip count back to 0'''

        self._drip_detector.reset()

    def start_counting_drips(self, drip_call_back=None):
        '''Turns on the counting of drips. Stop must be called to end this.'''

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
            self._communicator = UsbPacketCommunicator(self._current_config.circut.calibration_queue_length)
            self._communicator.start()
            self._drip_detector = SerialDripZAxis(self._communicator, 1, 0.0, drip_call_back=self.drip_call_back)

    def _stop_current_dripper(self):
        if self._communicator:
            self._communicator.close()
        if self._drip_detector:
            self._drip_detector.close()
            self._drip_detector = None

    def stop_counting_drips(self):
        '''Turns off the counting of drips if counting'''

        if self._commander:
            self._commander.close()
        self._stop_current_dripper()

    def send_dripper_on_command(self):
        '''If serial commuinication is enabled this send the turn on drips command'''

        if self._commander:
            self._commander.send_command(self._current_config.serial.on_command)
        else:
            raise Exception("Serial not Started")

    def send_dripper_off_command(self):
        '''If serial commuinication is enabled this send the turn off drips command'''

        if self._commander:
            self._commander.send_command(self._current_config.serial.off_command)
        else:
            raise Exception("Serial not Started")


class CureTestSetupMixIn(object):
    '''This is a Mixin for the ConfigurationAPI and exists only for organizational purposes'''

    def get_cure_test(self, base_height, total_height, start_speed, stop_speed, base_speed=None):
        '''Returns a layer generator that can be used with the print API to print a cure test.'''

        self._verify_cure_test_settings(base_height, total_height, start_speed, stop_speed, base_speed=base_speed)
        return CureTestGenerator(base_height, total_height, start_speed, stop_speed, self._current_config.options.sublayer_height_mm)

    def get_speed_at_height(self, base_height, total_height, start_speed, stop_speed, height, base_speed=None):
        '''Based on provided setting returns the speed the printer was going at the specified height'''

        self._verify_cure_test_settings(base_height, total_height, start_speed, stop_speed, base_speed=base_speed)
        if (height < base_height or height > total_height):
            logger.warning('Height of ideal cure must be in range of cure test')
            raise Exception('Height of ideal cure must be in range of cure test')
        actual_height = total_height - base_height
        desired_height = height - base_height
        speed_delta = stop_speed -start_speed
        return start_speed + (speed_delta / actual_height * desired_height)

    def _verify_cure_test_settings(self, base_height, total_height, start_speed, stop_speed, base_speed):
        try:
            float(base_height)
            float(total_height)
            float(start_speed)
            float(stop_speed)
            if base_speed is not None:
                float(base_speed)
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
        if base_speed is not None:
            if(base_speed <= 0):
                logger.warning('base_speed cannot be zero or negitive')
                raise Exception('base_speed cannot be zero or negitive')

    def set_cure_rate_base_height(self, base_height):
        '''Sets the base_height for Cure Rate test.'''

        if (self._zero_or_positive_float(float(base_height))):
            self._current_config.cure_rate.base_height = base_height
        else:
            logger.warning('Base height must be 0 or positive')
            raise Exception('Specified base height must be positive')

    def set_cure_rate_total_height(self, total_height):
        '''Sets the total_height for Cure Rate test.'''

        if (self._positive_float(float(total_height))):
            self._current_config.cure_rate.total_height = total_height
        else:
            logger.warning('Total height must be positive')
            raise Exception('Specified total height must be positive')

    def set_cure_rate_start_speed(self, start_speed):
        '''Sets the start_speed for Cure Rate test.'''

        if (self._positive_float(float(start_speed))):
            self._current_config.cure_rate.start_speed = start_speed
        else:
            logger.warning('start_speed must be positive')
            raise Exception('Specified start speed must be positive')

    def set_cure_rate_finish_speed(self, finish_speed):
        '''Sets the finish_speed for Cure Rate test.'''

        if (self._positive_float(float(finish_speed))):
            self._current_config.cure_rate.finish_speed = finish_speed
        else:
            logger.warning('finish_speed must be positive')
            raise Exception('Specified finish speed must be positive')

    def set_cure_rate_move_speed(self, move_speed):
        '''Sets the draw_speed for Cure Rate test.'''

        if (self._positive_float(float(move_speed))):
            self._current_config.cure_rate.move_speed = move_speed
        else:
            logger.warning('move_speed must be positive')
            raise Exception('Specified move speed must be positive')

    def set_cure_rate_draw_speed(self, draw_speed):
        '''Sets the draw_speed for Cure Rate test.'''

        if (self._positive_float(float(draw_speed))):
            self._current_config.cure_rate.draw_speed = draw_speed
        else:
            logger.warning('draw_speed must be positive')
            raise Exception('Specified draw speed must be positive')

    def set_cure_rate_use_draw_speed(self, use_draw_speed):
        '''Sets the use_draw_speed for Cure Rate test.'''

        self._current_config.cure_rate.use_draw_speed = use_draw_speed

    def set_cure_rate_override_laser_power(self, override_laser_power):
        '''Sets the override_laser_power for Cure Rate'''

        self._current_config.cure_rate.override_laser_power = override_laser_power

    def set_cure_rate_override_laser_power_amount(self, override_laser_power_amount):
        '''Sets the draw_speed for Cure Rate test.'''

        if override_laser_power_amount >= 1.0:
            raise Exception("Laser Power is too high")

        if (self._positive_percentage(float(override_laser_power_amount))):
            self._current_config.cure_rate.override_laser_power_amount = override_laser_power_amount
        else:
            logger.warning('override_laser_power_amount must be positive percentage between 0 and 1')
            raise Exception('Specified override_laser_power_amount must be positive')

    def get_cure_rate_base_height(self):
        '''Gets the base_height for Cure Rate test.'''

        return self._current_config.cure_rate.base_height

    def get_cure_rate_total_height(self):
        '''Gets the total_height for Cure Rate test.'''

        return self._current_config.cure_rate.total_height

    def get_cure_rate_start_speed(self):
        '''Gets the start_speed for Cure Rate test.'''

        return self._current_config.cure_rate.start_speed

    def get_cure_rate_finish_speed(self):
        '''Gets the finish_speed for Cure Rate test.'''

        return self._current_config.cure_rate.finish_speed

    def get_cure_rate_draw_speed(self):
        '''Gets the draw_speed for Cure Rate test.'''

        return self._current_config.cure_rate.draw_speed

    def get_cure_rate_move_speed(self):
        '''Gets the move_speed for Cure Rate test.'''

        return self._current_config.cure_rate.move_speed

    def get_cure_rate_use_draw_speed(self):
        '''Gets the usedraw_speed for Cure Rate test.'''

        return self._current_config.cure_rate.use_draw_speed

    def get_cure_rate_override_laser_power(self):
        '''Gets the override_laser_power for Cure Rate'''

        return self._current_config.cure_rate.override_laser_power

    def get_cure_rate_override_laser_power_amount(self):
        '''Gets the override_laser_power_amount for Cure Rate'''

        return self._current_config.cure_rate.override_laser_power_amount


class OptionsSetupMixIn(object):
    '''This is a Mixin for the ConfigurationAPI and exists only for organizational purposes'''

    def get_options_wait_after_move_milliseconds(self):
        '''Returns the wait after move milliseconds'''

        return self._current_config.options.wait_after_move_milliseconds

    def get_options_pre_layer_delay(self):
        '''Returns the pre layer delay'''

        return self._current_config.options.pre_layer_delay

    def get_options_print_queue_delay(self):
        '''Returns the print queue delay'''

        return self._current_config.options.print_queue_delay

    def get_options_laser_thickness_mm(self):
        '''Returns the current setting for laser thickness'''

        return self._current_config.options.laser_thickness_mm

    def get_options_scaling_factor(self):
        '''Returns the current setting for scaling factor'''

        return self._current_config.options.scaling_factor

    def get_options_sublayer_height_mm(self):
        '''Gets the Sublayer height sublayers are added between layers for grater definition'''

        return self._current_config.options.sublayer_height_mm

    def get_options_max_lead_distance_mm(self):
        '''Gets the Max Lead Distance or the amount the z layer can be ahead before layers are skipped'''

        return self._current_config.dripper.max_lead_distance_mm

    def get_options_post_fire_delay(self):
        '''Gets the Post Fire Delay for each layer'''

        return self._current_config.options.post_fire_delay

    def get_options_slew_delay(self):
        '''Gets the Slew Delay for each layer'''

        return self._current_config.options.slew_delay

    def get_options_overlap_amount_mm(self):
        '''Gets the Overlap Amount for each layer'''

        return self._current_config.options.overlap_amount

    def get_options_shuffle_layers_amount(self):
        '''Gets the Shuffle Layers Amount for each layer'''

        return self._current_config.options.shuffle_layers_amount

    def get_options_use_shufflelayers(self):
        '''Gets the Shuffle layers setting'''

        return self._current_config.options.use_shufflelayers

    def get_options_use_sublayers(self):
        '''Gets the Sub layers setting'''

        return self._current_config.options.use_sublayers

    def get_options_use_overlap(self):
        '''Gets the Overlap layers setting'''

        return self._current_config.options.use_overlap

    def set_options_wait_after_move_milliseconds(self, delay_milliseconds):
        '''Sets the wait after move milliseconds'''

        if self._zero_or_positive_int(delay_milliseconds):
            self._current_config.options.wait_after_move_milliseconds = delay_milliseconds
            self.save()
        else:
            raise Exception("Wait after move milliseconds must be a positive int number")

    def set_options_pre_layer_delay(self, delay):
        '''Sets the pre layer delay'''

        if self._zero_or_positive_float(delay):
            self._current_config.options.pre_layer_delay = delay
            self.save()
        else:
            raise Exception("Print queue delay must be a positive floating point number")

    def set_options_print_queue_delay(self, delay):
        '''Sets the print queue delay'''

        if self._zero_or_positive_float(delay):
            self._current_config.options.print_queue_delay = delay
            self.save()
        else:
            raise Exception("Print queue delay must be a positive floating point number")

    def set_options_laser_thickness_mm(self, thickness_mm):
        '''Sets the laser thickness in mm'''

        if self._positive_float(thickness_mm):
            self._current_config.options.laser_thickness_mm = thickness_mm
            self.save()
        else:
            raise Exception("Laser thickness must be a positive floating point number")

    def set_options_scaling_factor(self, scaling_factor):
        '''Sets the scaling factor in mm'''

        if self._positive_float(scaling_factor):
            self._current_config.options.scaling_factor = scaling_factor
            self.save()
        else:
            raise Exception("Scaling Factor must be a positive floating point number")

    def set_options_sublayer_height_mm(self, thickness_mm):
        '''Sets the Sublayer height sublayers are added between layers for grater definition'''

        if self._positive_float(thickness_mm):
            self._current_config.options.sublayer_height_mm = thickness_mm
            self.save()
        else:
            raise Exception("Sublayer height must be a positive floating point number")

    def set_options_max_lead_distance_mm(self, lead_distance_mm):
        '''Sets the Max Lead Distance or the amount the z layer can be ahead before layers are skipped'''

        if self._zero_or_positive_float(lead_distance_mm):
            self._current_config.dripper.max_lead_distance_mm = lead_distance_mm
            self.save()
        else:
            raise Exception("Max lead distance height must be a positive floating point number")

    def set_options_overlap_amount_mm(self, overlap_amount):
        '''Sets the Overlap Amount for each layer'''

        if self._positive_float(overlap_amount):
            self._current_config.options.overlap_amount = overlap_amount
            self.save()
        else:
            raise Exception("Overlap Amount must be a positive floating point number")

    def set_options_post_fire_delay(self, post_fire_delay):
        '''Sets the Post Fire Delay for each layer'''

        if self._zero_or_positive_int(post_fire_delay):
            self._current_config.options.post_fire_delay = post_fire_delay
            self.save()
        else:
            raise Exception("Post Fire Delay must be a positive integer number")

    def set_options_slew_delay(self, slew_delay):
        '''Sets the Slew Delay for each layer'''

        if self._zero_or_positive_int(slew_delay):
            self._current_config.options.slew_delay = slew_delay
            self.save()
        else:
            raise Exception("Post Fire Delay must be a positive integer number")

    def set_options_shuffle_layers_amount(self, shuffle_layers_amount):
        '''Sets the Shuffle Layers Amount for each layer'''

        if self._positive_float(shuffle_layers_amount):
            self._current_config.options.shuffle_layers_amount = shuffle_layers_amount
            self.save()
        else:
            raise Exception("Shuffle Layers Amount must be a positive floating point number")

    def set_options_use_shufflelayers(self, use_shufflelayers):
        '''Sets the Shuffle layers setting'''

        if (type(use_shufflelayers) == types.BooleanType):
            self._current_config.options.use_shufflelayers = use_shufflelayers
            self.save()
        else:
            raise Exception("Use Shuffle Layers must be True or False")

    def set_options_use_sublayers(self, use_sublayers):
        '''Sets the Sub layers setting'''

        if (type(use_sublayers) == types.BooleanType):
            self._current_config.options.use_sublayers = use_sublayers
            self.save()
        else:
            raise Exception("Use SubLayers must be True or False")

    def set_options_use_overlap(self, use_overlap):
        '''Sets the Overlap layers setting'''

        if (type(use_overlap) == types.BooleanType):
            self._current_config.options.use_overlap = use_overlap
            self.save()
        else:
            raise Exception("Use Overlap must be True or False")


class EmailSetupMixin(object):
    '''This is a Mixin for the ConfigurationAPI and exists only for organizational purposes'''

    def set_email_on(self, on):
        '''Set email notifications to boolean'''

        self._current_config.email.on = on

    def set_email_port(self, port):
        '''Sets the port of the smtp server'''

        self._current_config.email.port = port

    def set_email_host(self, host):
        '''Sets the host address of the email server'''

        self._current_config.email.host = host

    def set_email_sender(self, sender):
        '''Sets the email address of the sender'''
        self._current_config.email.sender = sender

    def set_email_recipient(self, recipient):
        '''Sets the recipient for the email'''

        self._current_config.email.recipient = recipient

    def set_email_username(self, username):
        '''Sets the username for the email account'''

        self._current_config.email.username = username

    def set_email_password(self, password):
        '''Sets the password of the email account (Note: this is stored as plain text)'''

        self._current_config.email.password = password

    def get_email_on(self):
        '''Returns status of email as boolean'''

        return self._current_config.email.on

    def get_email_port(self):
        '''Returns the port for the smtp address'''

        return self._current_config.email.port

    def get_email_host(self):
        '''Returns the host name for the smtp address'''

        return self._current_config.email.host

    def get_email_sender(self):
        '''Returns the sender email address'''

        return self._current_config.email.sender

    def get_email_recipient(self):
        '''Returns the email reciepient address'''

        return self._current_config.email.recipient

    def get_email_username(self):
        '''Returns the email account username'''

        return self._current_config.email.username

    def get_email_password(self):
        '''Returns the email account password'''

        return self._current_config.email.password


class SerialSetupMixin(object):
    '''This is a Mixin for the ConfigurationAPI and exists only for organizational purposes'''

    def get_serial_enabled(self):
        '''Returns is serial is enabled'''

        return self._current_config.serial.on

    def get_serial_port(self):
        '''Returns the current serial port'''

        return self._current_config.serial.port

    def get_serial_on_command(self):
        '''Returns the serial dripper on command'''

        return self._current_config.serial.on_command

    def get_serial_off_command(self):
        '''Returns the serial dripper off command'''

        return self._current_config.serial.off_command

    def get_serial_layer_started_command(self):
        '''Returns the layer started command'''

        return self._current_config.serial.layer_started

    def get_serial_layer_ended_command(self):
        '''Returns the layer ended command'''

        return self._current_config.serial.layer_ended

    def get_serial_print_start_command(self):
        '''Returns the print start command'''

        return self._current_config.serial.print_start

    def get_serial_print_ended_command(self):
        '''Returns the print ended command'''

        return self._current_config.serial.print_ended

    def set_serial_enabled(self, enabled):
        '''Sets the serial enabnle as boolean'''

        logger.info("CFG Setting changed: serial_enabled -> %s" % enabled)
        self._current_config.serial.on = enabled
        self.save()

    def set_serial_port(self, port):
        '''Sets the port as string'''

        logger.info("Setting changed: serial_port -> %s" % port)
        self._current_config.serial.port = port
        self.save()

    def set_serial_on_command(self, on_command):
        '''Sets the on command as a single character string'''

        logger.info("Setting changed: serial_on_command -> %s" % on_command)
        self._current_config.serial.on_command = on_command
        self.save()

    def set_serial_off_command(self, off_command):
        '''Sets the off command as a single character string'''

        logger.info("Setting changed: serial_off_command -> %s" % off_command)
        self._current_config.serial.off_command = off_command
        self.save()

    def set_serial_layer_started_command(self, layer_started):
        '''Sets the layer started command as a single character string'''

        logger.info("Setting changed: serial_layer_started_command -> %s" % layer_started)
        self._current_config.serial.layer_started = layer_started
        self.save()

    def set_serial_layer_ended_command(self, layer_ended):
        '''Sets the layer ended command as a single character string'''

        logger.info("Setting changed: serial_layer_ended_command -> %s" % layer_ended)
        self._current_config.serial.layer_ended = layer_ended
        self.save()

    def set_serial_print_start_command(self, print_start):
        '''Sets the print start command as a single character string'''

        logger.info("Setting changed: serial_print_start_command -> %s" % print_start)
        self._current_config.serial.print_start = print_start
        self.save()

    def set_serial_print_ended_command(self, print_ended):
        '''Sets the print ended command as a single character string'''

        logger.info("Setting changed: serial_print_ended_command -> %s" % print_ended)
        self._current_config.serial.print_ended = print_ended
        self.save()


class ConfigurationAPI(
    InfoMixIn,
    DripperSetupMixIn,
    CureTestSetupMixIn,
    OptionsSetupMixIn,
    EmailSetupMixin,
    SerialSetupMixin,
    ):
    '''Api for adjusting settings for the peachy current_printer.'''

    def __init__(self, configuration_manager):
        self._configuration_manager = configuration_manager
        self._current_config = None
        self._drip_detector = None
        self._communicator = None
        self._marked_drips = None
        self._commander = None

    def current_printer(self):
        '''Returns the currently loaded printer name'''

        if self._current_config:
            return self._current_config.name
        else:
            return None

    def get_current_config(self):
        '''Returns the current printer config in json'''

        self.load_printer()
        return self._current_config

    def load_printer(self):
        '''Loads an attached printer'''
        if self._current_config:
            pass
        else:
            self._current_config = self._configuration_manager.load()

    def reset_printer(self):
        '''Resets configured printer to defaults'''

        self._current_config = self._configuration_manager.reset()

    def save(self):
        '''Saves the currently selected config'''

        self._configuration_manager.save(self._current_config)

    def _positive_float(self, value):
        return (isinstance(value, types.FloatType) and value > 0.0)

    def _positive_percentage(self, value):
        return (isinstance(value, types.FloatType) and value >= 0.0 and value <= 1.0)

    def _zero_or_positive_float(self, value):
        return (isinstance(value, types.FloatType) and value >= 0.0)

    def _zero_or_positive_int(self, value):
        return (isinstance(value, types.IntType) and value >= 0.0)
