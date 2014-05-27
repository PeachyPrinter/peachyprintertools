import os
import hashlib
import config
import pickle
import types
import logging

from domain.configuration_manager import ConfigurationManager


class OptionsConfiguration(object):
    def __init__(self):
        self._draw_speed = None
        self._laser_offset = None
        self._sublayer_height_mm = None
        self._laser_thickness_mm = None

    @property
    def draw_speed(self):
        return self._draw_speed

    @draw_speed.setter
    def draw_speed(cls, value):
        _type = types.FloatType
        if type(value) == _type:
            cls._draw_speed = value
        else:
            raise ValueError("Draw Speed must be of %s" % (str(_type)))



class DripperConfiguration(object):
    def __init__(self):
        self.max_lead_distance_mm = None
        self.drips_per_mm = None


class CalibrationConfiguration(object):
    def __init__(self):
        self._scale = None
        self._data = None
        self.max_deflection = None


class SerialZAxisConfiguration(object):
    def __init__(self):
        self._on = None
        self._port = None
        self._on_command = None
        self._off_command = None


class AudioInputConfiguration(object):
    def __init__(self):
        self._bit_depth = None
        self._sample_rate = None


class AudioOutputConfiguration(object):
    def __init__(self):
        self._bit_depth = None
        self._sample_rate = None
        self._modulation_on_frequency = None
        self._modulation_off_frequency = None
    

class AudioConfiguration(object):
    def __init__(self):
        self._input = AudioInputConfiguration()
        self._output = AudioOutputConfiguration()

    @property
    def input():
        return self._input

    @property
    def output():
        return self._output

class Configuration(object):
    def __init__(self):
        self._name = "Peachy Printer"
        self._audio = AudioConfiguration()
        self._serial = SerialConfiguration()
        self._calibration = CalibrationConfiguration()
        self._dripper = DripperConfiguration()
        self._options = OptionsConfiguration()



class FileBasedConfigurationManager(ConfigurationManager):
    REQUIRED_FIELDS = {
        'name' : types.StringType ,
        'output_bit_depth': types.StringType ,
        'output_sample_frequency' : types.IntType ,
        'on_modulation_frequency': types.IntType ,
        'off_modulation_frequency': types.IntType ,
        'input_bit_depth': types.StringType ,
        'input_sample_frequency': types.IntType ,
        'sublayer_height_mm': types.FloatType,
        'laser_thickness_mm' : types.FloatType,
        'drips_per_mm':types.FloatType,
        'max_deflection' :types.FloatType,
        'calibration_data': types.DictType,
        'calibration_scale': types.FloatType,
        'draw_speed' : types.FloatType,
        'max_lead_distance_mm' : types.FloatType,
        'use_serial_zaxis' : types.BooleanType,
        'serial_port': types.StringType,
        'serial_on': types.StringType,
        'serial_off' : types.StringType,
        'laser_offset' : types.ListType,
    }
    
    CONFIGURATION_EXTENSION = '.cfg'

    def __init__(self):
        pass

    def list(self):
        printers = []
        if os.path.exists(config.PEACHY_PATH):
            for file_name in os.listdir(config.PEACHY_PATH):
                if file_name.endswith(self.CONFIGURATION_EXTENSION):
                    configuration = self._load_configuration(os.path.join(self._path(), file_name))
                    if configuration:
                        printers.append(configuration['name'])
        return printers

    def load(self, printer_name):
        logging.info('Loading configutation for "%s"' % printer_name)
        filename = self._get_file_name(printer_name)
        if not os.path.exists(filename):
            raise Exception("Printer file not found")
        configuration = self._load_configuration(filename)
        if configuration:
            return configuration
        else:
            raise Exception("Printer file corrupt or damaged")

    def _load_configuration(self, filename):
        with open(filename, 'r') as file_handle:
            configuration = pickle.load(file_handle)
            if self._valid(configuration):
                return configuration
            else:
                return None

    def save(self, configuration):
        if self._valid(configuration):
            filename = self._get_file_name(configuration['name'])
            with open(filename,'w') as file_handle:
                pickle.dump(configuration, file_handle)
        else:
            logging.error("Saving, Configuration Specified is invalid\n%s" % configuration)
            raise Exception("Configuration Specified is invalid\n%s" % configuration )

    def new(self, printer_name):
        new_printer = self.DEFAULTS.copy()
        new_printer['name'] = printer_name
        return new_printer

    def _valid(self, configuration):
        valid = True
        for (key, value) in self.REQUIRED_FIELDS.items():
            if not (configuration.has_key(key) and type(configuration[key]) == value):
                logging.warn('%s missing or invalid\n%s' % (key, configuration))
                valid = False
        return valid

    def _path(self):
        if not os.path.exists(config.PEACHY_PATH):
            os.makedirs(config.PEACHY_PATH)
        return config.PEACHY_PATH

    def _get_file_name(self, name):
        filename = hashlib.md5(name).hexdigest() + self.CONFIGURATION_EXTENSION
        return os.path.join(self._path(), filename)
