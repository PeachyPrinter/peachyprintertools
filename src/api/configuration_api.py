import types
import logging

from infrastructure.audio import AudioSetup
from infrastructure.drip_based_zaxis import DripBasedZAxis
from infrastructure.layer_generators import CureTestGenerator

'''Details the audio settings'''
class AudioSetting(object):
    def __init__(self, sample_frequency, bit_depth, recommended = False, current = False):
        self.sample_frequency = sample_frequency
        self.bit_depth = bit_depth
        self.recommended = recommended
        self.current = current

    def set_recommended(self):
        self.recommended = True

    def set_current(self):
        self.current = True

    def __eq__(self, other):
        return self.sample_frequency == other.sample_frequency and self.bit_depth == other.bit_depth and self.recommended == other.recommended and self.current == other.current

    def __str__(self):
        if self.recommended:
            return "%s Hz, %s (Recommended)" % (self.sample_frequency, self.bit_depth)
        else:
            return "%s Hz, %s" % (self.sample_frequency, self.bit_depth)


'''Api for adjusting setting for the peachy current_printer.
This API is still in active development and as is subject dramatic change'''
class ConfigurationAPI(object):
    def __init__(self, configuration_manager):
        self._configuration_manager = configuration_manager
        self._current_config = None
        self._audio_setup = AudioSetup()
        self._drip_detector = None
        self._marked_drips = None

    '''Returns the currently loaded printer name'''
    def current_printer(self):
        if self._current_config:
            return self._current_config.name
        else:
            logging.debug('Current config missing')
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
        logging.debug("Loaded config:\n%s" % self._current_config)
    
    '''Saves the currently selected config'''
    def save(self):
        self._configuration_manager.save(self._current_config)

    # ----------------------------------- Audio Setup ------------------------------------------
    _BEST_AUDIO_OUT_OPTIONS = [
        AudioSetting(48000, '16 bit'), 
        AudioSetting(48000, '24 bit'),
        AudioSetting(48000, '32 bit Floating Point'), 
        AudioSetting(44100, '16 bit'), 
        AudioSetting(44100, '32 bit'),
        AudioSetting(44100, '32 bit Floating Point'), 
        ]
        
    _BEST_AUDIO_IN_OPTIONS = [ 
        AudioSetting(48000, '16 bit'), 
        AudioSetting(44100, '16 bit')
        ]

    '''Lists all available audio options returning a list of AudioSetting. 
    Warning: due to a bug in a port audio this may list unusable audio types.'''
    def get_available_audio_options(self):
        options = self._audio_setup.get_valid_sampling_options()
        inputs  = [ AudioSetting(option['sample_rate'],option['depth']) for option in options['input' ]]
        outputs = [ AudioSetting(option['sample_rate'],option['depth']) for option in options['output']]
        self._set_recommend(inputs, 'inputs')
        self._set_recommend(outputs, 'outputs')
        self._set_currently_selected(inputs, 'inputs')
        self._set_currently_selected(outputs, 'outputs')
        return { 'inputs': self._sort_options(inputs) ,'outputs' : self._sort_options(outputs)}

    def _sort_options(self, options):
        options.sort(key = lambda option: (option.sample_frequency, option.bit_depth))
        return options

    def _set_recommend(self, audio_settings, io_type):
        options = self._BEST_AUDIO_IN_OPTIONS if io_type == 'inputs' else self._BEST_AUDIO_OUT_OPTIONS
        for option in options:
            for audio_setting in audio_settings:
                if option == audio_setting:
                    audio_setting.set_recommended()
                    return

    def _set_currently_selected(self, audio_settings, io_type):
        if io_type == 'inputs':
            sample_frequency = self._current_config.audio.input.sample_rate
            bit_depth = self._current_config.audio.input.bit_depth
        else:
            sample_frequency = self._current_config.audio.output.sample_rate
            bit_depth = self._current_config.audio.output.bit_depth
        for audio_setting in audio_settings:
            if sample_frequency == audio_setting.sample_frequency and bit_depth == audio_setting.bit_depth:
                audio_setting.set_current()
                return

    '''Sets the output audio based on the AudioSetting passed in'''
    def set_audio_output_options(self, audio_setting):
        #TODO JT 2014-04-30 - The modulation stuff may not belong here.
        if (audio_setting.sample_rate == 44100):
            self._current_config.audio.output.modulation_on_frequency = 11025
            self._current_config.audio.output.modulation_off_frequency = 2205
        else:
            self._current_config.audio.output.modulation_on_frequency = 12000
            self._current_config.audio.output.modulation_off_frequency = 2000
        self._current_config.audio.output.bit_depth = audio_setting.bit_depth
        self._current_config.audio.output.sample_rate = audio_setting.sample_frequency
        self.save()

    '''Sets the output audio based on the AudioSetting passed in'''
    def set_audio_input_options(self,audio_setting):
        self._current_config.audio.input.bit_depth = audio_setting.bit_depth
        self._current_config.audio.input.sample_rate = audio_setting.sample_frequency
        self.save()

    # ------------------------------- Drip Setup --------------------------------------

    '''Returns the current number of drips that have been counted'''
    def get_drips(self):
        return self._drip_detector.current_z_location_mm()

    '''Records the current of drips'''
    def mark_drips_at_target(self):
        if self._target_height != None:
            self._marked_drips = self.get_drips()
            self._current_config.dripper.drips_per_mm = self.get_drips_per_mm() 
        else:
            raise Exception("Target height must be specified before marking end point")

    '''Sets the target height that the drips will be marked at'''
    def set_target_height(self,height_mm):
        try:
            if float(height_mm) > 0.0:
                self._target_height = float(height_mm)
            else:
                raise Exception("Target height must be a positive numeric value")
        except:
            raise Exception("Target height must be a positive numeric value")

    '''Sets the drip count back to 0'''
    def reset_drips(self):
        self._drip_detector.reset(0)

    '''Does the math based on set_target_height and mark_drips_at_target to return the drips per mm'''
    def get_drips_per_mm(self):
        if self._marked_drips:
            return self._marked_drips / self._target_height
        else:
            return self._current_config.dripper.drips_per_mm

    '''Turns on the counting of drips. Stop must be called to end this.'''
    def start_counting_drips(self, drip_call_back = None):
        self._drip_detector = DripBasedZAxis(
            1,
            sample_rate = self._current_config.audio.input.sample_rate, 
            bit_depth = self._current_config.audio.input.bit_depth,
            drip_call_back = drip_call_back
            )
        self._drip_detector.start()

    '''Turns off the counting of drips if counting'''
    def stop_counting_drips(self):
        if self._drip_detector:
            self._drip_detector.stop()
            self._drip_detector = None

    # ----------------------------- Cure Test Setup ------------------------------------
    '''Returns a layer generator that can be used with the print API to print a cure test.'''
    def get_cure_test(self, base_height, total_height, start_speed, stop_speed):
        self._verify_cure_test_settings(base_height, total_height, start_speed, stop_speed)
        return CureTestGenerator(base_height, total_height, start_speed, stop_speed, self._current_config.options.sublayer_height_mm)

    '''Based on provided setting returns the speed the printer was going at the specified height'''
    def get_speed_at_height(self, base_height, total_height, start_speed, stop_speed, height):
        self._verify_cure_test_settings(base_height, total_height, start_speed, stop_speed)
        if (height < base_height or height > total_height):
            logging.warning('Height of ideal cure must be in range of cure test')
            raise Exception('Height of ideal cure must be in range of cure test')
        actual_height = total_height - base_height
        desired_height = height - base_height
        speed_delta = stop_speed -start_speed
        return start_speed + (speed_delta / actual_height * desired_height)

    def _verify_cure_test_settings(self,base_height, total_height, start_speed, stop_speed):
        try:
            float(base_height)
            float(total_height)
            float(start_speed)
            float(stop_speed)
        except ValueError:
            logging.warning('Entries for cure test settings must be numeric')
            raise Exception('Entries for cure test settings must be numeric')
        if(total_height <= base_height):
            logging.warning('total_height must be greater then base_height')
            raise Exception('total_height must be greater then base_height')
        if(start_speed > stop_speed):
            logging.warning('start_speed must be less then stop speed')
        if(total_height <= 0):
            logging.warning('total_height must be a positive number')
            raise Exception('start_speed must be less then stop speed')
        if(start_speed <= 0):
            logging.warning( 'start_speed must be positive')
            raise Exception( 'start_speed must be positive')
        if(stop_speed <= 0):
            logging.warning('stop_speed must be positive')
            raise Exception('stop_speed must be positive')
        if(stop_speed <= start_speed):
            logging.warning('stop_speed must faster the start_speed')
            raise Exception('stop_speed must faster the start_speed')
        if(base_height < 0):
            logging.warning('base_height cannot be negitive')
            raise Exception('base_height cannot be negitive')

    '''Save the maximum speed in mm per second in the configuration file'''
    def set_speed(self,mm_per_second):
        if (float(mm_per_second) > 0.0):
            self._current_config.options.draw_speed = float(mm_per_second)
            self.save()
        else:
            logging.warning('Specified speed if less then or equal to 0')
            raise Exception('Specified speed if less then or equal to 0')

    # ----------------------------- General Setup --------------------------------------

    '''Returns the current setting for laser thickness'''
    def get_laser_thickness_mm(self):
        return self._current_config.options.laser_thickness_mm

    '''Sets the laser thickness in mm'''
    def set_laser_thickness_mm(self, thickness_mm):
        if (type(thickness_mm) == types.FloatType  and thickness_mm > 0.0):
            self._current_config.options.laser_thickness_mm = thickness_mm
            self.save()
        else:
            raise Exception("Laser thickness must be a positive floating point number")

    '''Gets the Sublayer height sublayers are added between layers for grater definition'''
    def get_sublayer_height_mm(self):
        return self._current_config.options.sublayer_height_mm

    '''Sets the Sublayer height sublayers are added between layers for grater definition'''
    def set_sublayer_height_mm(self, thickness_mm):
        if (type(thickness_mm) == types.FloatType  and thickness_mm > 0.0):
            self._current_config.options.sublayer_height_mm = thickness_mm
            self.save()
        else:
            raise Exception("Sublayer height must be a positive floating point number")

    '''Gets the Max Lead Distance or the amount the z layer can be ahead before layers are skipped'''
    def get_max_lead_distance_mm(self):
        return self._current_config.dripper.max_lead_distance_mm

    '''Sets the Max Lead Distance or the amount the z layer can be ahead before layers are skipped'''
    def set_max_lead_distance_mm(self, lead_distance_mm):
        if (type(lead_distance_mm) == types.FloatType  and lead_distance_mm > 0.0):
            self._current_config.dripper.max_lead_distance_mm = lead_distance_mm
            self.save()
        else:
            raise Exception("Max lead distance height must be a positive floating point number")


    #----------------------------Advanced Setup---------------------------------------

    def get_serial_enabled(self):
        return self._current_config.serial.on

    def get_serial_port(self):
        return self._current_config.serial.port

    def get_serial_on_command(self):
        return self._current_config.serial.on_command

    def get_serial_off_command(self):
        return self._current_config.serial.off_command

    def set_serial_enabled(self, enabled):
        self._current_config.serial.on = enabled
        self.save()

    def set_serial_port(self, port):
        self._current_config.serial.port = port
        self.save()

    def set_serial_on_command(self, on_command):
        self._current_config.serial.on_command = on_command
        self.save()

    def set_serial_off_command(self, off_command):
        self._current_config.serial.off_command = off_command
        self.save()


