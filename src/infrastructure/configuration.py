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

    @property
    def laser_offset(self):
        return self._laser_offset

    @laser_offset.setter
    def laser_offset(cls, value):
        _type = types.ListType
        _inner_type = types.FloatType
        if (type(value) == _type and 
            len(value) == 2 and 
            type(value[0]) == _inner_type and
            type(value[1]) == _inner_type):
            cls._laser_offset = value
        else:
            raise ValueError("Laser Offset must be of %s" % (str(_type)))

    @property
    def sublayer_height_mm(self):
        return self._sublayer_height_mm

    @sublayer_height_mm.setter
    def sublayer_height_mm(cls, value):
        _type = types.FloatType
        if type(value) == _type:
            cls._sublayer_height_mm = value
        else:
            raise ValueError("Sublayer Height must be of %s" % (str(_type)))

    @property
    def laser_thickness_mm(self):
        return self._laser_thickness_mm

    @laser_thickness_mm.setter
    def laser_thickness_mm(cls, value):
        _type = types.FloatType
        if type(value) == _type:
            cls._laser_thickness_mm = value
        else:
            raise ValueError("Laser Thickness must be of %s" % (str(_type)))



class DripperConfiguration(object):
    def __init__(self):
        self._max_lead_distance_mm = None
        self._drips_per_mm = None

    @property
    def max_lead_distance_mm(self):
        return self._max_lead_distance_mm

    @max_lead_distance_mm.setter
    def max_lead_distance_mm(cls, value):
        _type = types.FloatType
        if type(value) == _type:
            cls._max_lead_distance_mm = value
        else:
            raise ValueError("Max Lead distance must be of %s" % (str(_type)))

    @property
    def drips_per_mm(self):
        return self._drips_per_mm

    @drips_per_mm.setter
    def drips_per_mm(cls, value):
        _type = types.FloatType
        if type(value) == _type:
            cls._drips_per_mm = value
        else:
            raise ValueError("Drips per mm must be of %s" % (str(_type)))


class CalibrationConfiguration(object):
    def __init__(self):
        self._scale = None
        self._data = None
        self._max_deflection = None

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(cls, value):
        _type = types.FloatType
        if type(value) == _type:
            cls._scale = value
        else:
            raise ValueError("Scale must be of %s" % (str(_type)))

    @property
    def data(self):
        return self._data

    @data.setter
    def data(cls, value):
        _type = types.DictType
        if type(value) == _type:
            cls._data = value
        else:
            raise ValueError("Data must be of %s" % (str(_type)))

    @property
    def max_deflection(self):
        return self._max_deflection

    @max_deflection.setter
    def max_deflection(cls, value):
        _type = types.FloatType
        if type(value) == _type:
            cls._max_deflection = value
        else:
            raise ValueError("Max Deflection must be of %s" % (str(_type)))


class SerialZAxisConfiguration(object):
    def __init__(self):
        self._on = None
        self._port = None
        self._on_command = None
        self._off_command = None

    @property
    def on(self):
        return self._on

    @on.setter
    def on(cls, value):
        _type = types.BooleanType
        if type(value) == _type:
            cls._on = value
        else:
            raise ValueError("Bit depth must be of %s" % (str(_type)))

    @property
    def port(self):
        return self._port

    @port.setter
    def port(cls, value):
        _type = types.StringType
        if type(value) == _type:
            cls._port = value
        else:
            raise ValueError("Bit depth must be of %s" % (str(_type)))

    @property
    def on_command(self):
        return self._on_command

    @on_command.setter
    def on_command(cls, value):
        _type = types.StringType
        if type(value) == _type:
            cls._on_command = value
        else:
            raise ValueError("Bit depth must be of %s" % (str(_type)))

    @property
    def off_command(self):
        return self._off_command

    @off_command.setter
    def off_command(cls, value):
        _type = types.StringType
        if type(value) == _type:
            cls._off_command = value
        else:
            raise ValueError("Bit depth must be of %s" % (str(_type)))

   

class AudioInputConfiguration(object):
    def __init__(self):
        self._bit_depth = None
        self._sample_rate = None

    @property
    def bit_depth(self):
        return self._bit_depth

    @bit_depth.setter
    def bit_depth(cls, value):
        _type = types.StringType
        if type(value) == _type:
            cls._bit_depth = value
        else:
            raise ValueError("Bit depth must be of %s" % (str(_type)))

    @property
    def sample_rate(self):
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(cls, value):
        _type = types.IntType
        if type(value) == _type:
            cls._sample_rate = value
        else:
            raise ValueError("Sample Rate must be of %s" % (str(_type)))


class AudioOutputConfiguration(object):
    def __init__(self):
        self._bit_depth = None
        self._sample_rate = None
        self._modulation_on_frequency = None
        self._modulation_off_frequency = None

    @property
    def bit_depth(self):
        return self._bit_depth

    @bit_depth.setter
    def bit_depth(cls, value):
        _type = types.StringType
        if type(value) == _type:
            cls._bit_depth = value
        else:
            raise ValueError("Bit depth must be of %s" % (str(_type)))

    @property
    def sample_rate(self):
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(cls, value):
        _type = types.IntType
        if type(value) == _type:
            cls._sample_rate = value
        else:
            raise ValueError("Sample Rate must be of %s" % (str(_type)))


    @property
    def modulation_on_frequency(self):
        return self._modulation_on_frequency

    @modulation_on_frequency.setter
    def modulation_on_frequency(cls, value):
        _type = types.IntType
        if type(value) == _type:
            cls._modulation_on_frequency = value
        else:
            raise ValueError("Modulation On Frequency must be of %s" % (str(_type)))


    @property
    def modulation_off_frequency(self):
        return self._modulation_off_frequency

    @modulation_off_frequency.setter
    def modulation_off_frequency(cls, value):
        _type = types.IntType
        if type(value) == _type:
            cls._modulation_off_frequency = value
        else:
            raise ValueError("Sample Rate must be of %s" % (str(_type)))
    

class AudioConfiguration(object):
    def __init__(self):
        self._input = AudioInputConfiguration()
        self._output = AudioOutputConfiguration()

    @property
    def input(self):
        return self._input

    @property
    def output(self):
        return self._output

class Configuration(object):
    def __init__(self):
        self._name = "Peachy Printer"
        self._audio = AudioConfiguration()
        self._serial = SerialZAxisConfiguration()
        self._calibration = CalibrationConfiguration()
        self._dripper = DripperConfiguration()
        self._options = OptionsConfiguration()

    @property
    def audio(self):
        return self._audio

    @property
    def serial(self):
        return self._serial
    
    @property
    def calibration(self):
        return self._calibration

    @property
    def dripper(self):
        return self._dripper

    @property
    def options(self):
        return self._options

    @property
    def name(self):
        return self._name
    @name.setter
    def name(cls, value):
        _type = types.StringType
        if type(value) == _type:
            cls._name = value
        else:
            raise ValueError("Name must be of %s" % (str(_type)))


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
