import os
import hashlib
import config
import json
import types
import logging

from domain.configuration_manager import ConfigurationManager


class OptionsConfiguration(object):
    def __init__(self, souce_dict = {}):
        self._draw_speed = souce_dict.get(u'draw_speed', None)
        self._laser_offset = souce_dict.get(u'laser_offset', None)
        self._sublayer_height_mm = souce_dict.get(u'sublayer_height_mm', None)
        self._laser_thickness_mm = souce_dict.get(u'laser_thickness_mm', None)

    def toDict(self):
        return { 
        u'draw_speed': self._draw_speed,
        u'laser_offset' : self._laser_offset,
        u'sublayer_height_mm': self._sublayer_height_mm,
        u'laser_thickness_mm' : self._laser_thickness_mm,
        }

    @property
    def draw_speed(self):
        return self._draw_speed

    @draw_speed.setter
    def draw_speed(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._draw_speed = value
        else:
            raise ValueError("Draw Speed must be of %s" % (str(_type)))

    @property
    def laser_offset(self):
        return self._laser_offset

    @laser_offset.setter
    def laser_offset(self, value):
        _type = types.ListType
        _inner_type = types.FloatType
        if (type(value) == _type and 
            len(value) == 2 and 
            type(value[0]) == _inner_type and
            type(value[1]) == _inner_type):
            self._laser_offset = value
        else:
            raise ValueError("Laser Offset must be of %s" % (str(_type)))

    @property
    def sublayer_height_mm(self):
        return self._sublayer_height_mm

    @sublayer_height_mm.setter
    def sublayer_height_mm(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._sublayer_height_mm = value
        else:
            raise ValueError("Sublayer Height must be of %s" % (str(_type)))

    @property
    def laser_thickness_mm(self):
        return self._laser_thickness_mm

    @laser_thickness_mm.setter
    def laser_thickness_mm(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._laser_thickness_mm = value
        else:
            raise ValueError("Laser Thickness must be of %s" % (str(_type)))

class DripperConfiguration(object):
    def __init__(self, souce_dict = {}):
        self._max_lead_distance_mm = souce_dict.get(u'max_lead_distance_mm', None)
        self._drips_per_mm = souce_dict.get(u'drips_per_mm', None)

    def toDict(self):
        return { 
        u'max_lead_distance_mm': self._max_lead_distance_mm,
        u'drips_per_mm' : self._drips_per_mm,
        }

    @property
    def max_lead_distance_mm(self):
        return self._max_lead_distance_mm

    @max_lead_distance_mm.setter
    def max_lead_distance_mm(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._max_lead_distance_mm = value
        else:
            raise ValueError("Max Lead distance must be of %s" % (str(_type)))

    @property
    def drips_per_mm(self):
        return self._drips_per_mm

    @drips_per_mm.setter
    def drips_per_mm(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._drips_per_mm = value
        else:
            raise ValueError("Drips per mm must be of %s" % (str(_type)))

class CalibrationConfiguration(object):
    def __init__(self, souce_dict = {}):
        self._scale = souce_dict.get(u'scale', None)
        self._max_deflection = souce_dict.get(u'max_deflection', None)
        self._height = souce_dict.get(u'height', None)
        self._lower_points = dict([ ((l[0][0],l[0][1]), (l[1][0],l[1][1])) for l in souce_dict.get(u'lower_points', []) ] )
        self._upper_points = dict([ ((u[0][0],u[0][1]), (u[1][0],u[1][1])) for u in souce_dict.get(u'upper_points', []) ] )


    def toDict(self):
        return { 
        u'scale': self._scale,
            u'max_deflection': self._max_deflection,
            u'height' : self._height,
            u'lower_points' : self._lower_points.items(),
            u'upper_points' : self._upper_points.items(),
        }

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._scale = value
        else:
            raise ValueError("Scale must be of %s" % (str(_type)))

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._height = value
        else:
            raise ValueError("Height must be of %s" % (str(_type)))
    
    @property
    def lower_points(self):
        return self._lower_points

    @lower_points.setter
    def lower_points(self, value):
        _type = types.DictType
        if type(value) == _type:
            self._lower_points = value
        else:
            raise ValueError("Data must be of %s" % (str(_type)))
    
    @property
    def upper_points(self):
        return self._upper_points

    @upper_points.setter
    def upper_points(self, value):
        _type = types.DictType
        if type(value) == _type:
            self._upper_points = value
        else:
            raise ValueError("Data must be of %s" % (str(_type)))

    @property
    def max_deflection(self):
        return self._max_deflection

    @max_deflection.setter
    def max_deflection(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._max_deflection = value
        else:
            raise ValueError("Max Deflection must be of %s" % (str(_type)))

class SerialZAxisConfiguration(object):
    def __init__(self, souce_dict = {}):
        self._on = souce_dict.get(u'on', None)
        self._port = souce_dict.get(u'port', None)
        self._on_command = souce_dict.get(u'on_command', None)
        self._off_command = souce_dict.get(u'off_command', None)

    def toDict(self):
        return { 
        u'on': self._on,
        u'port' : self._port,
        u'on_command': self._on_command,
        u'off_command' : self._off_command
        }


    @property
    def on(self):
        return self._on

    @on.setter
    def on(self, value):
        _type = types.BooleanType
        if type(value) == _type:
            self._on = value
        else:
            raise ValueError("Bit depth must be of %s" % (str(_type)))

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        _type = types.StringType
        if type(value) == _type:
            self._port = value
        else:
            raise ValueError("Bit depth must be of %s" % (str(_type)))

    @property
    def on_command(self):
        return self._on_command

    @on_command.setter
    def on_command(self, value):
        _type = types.StringType
        if type(value) == _type:
            self._on_command = value
        else:
            raise ValueError("Bit depth must be of %s" % (str(_type)))

    @property
    def off_command(self):
        return self._off_command

    @off_command.setter
    def off_command(self, value):
        _type = types.StringType
        if type(value) == _type:
            self._off_command = value
        else:
            raise ValueError("Bit depth must be of %s" % (str(_type)))

class AudioInputConfiguration(object):
    def __init__(self, souce_dict = {}):
        self._bit_depth = souce_dict.get(u'bit_depth', None)
        self._sample_rate = souce_dict.get(u'sample_rate', None)


    def toDict(self):
        return { 
        u'bit_depth': self._bit_depth,
        u'sample_rate' : self._sample_rate
        }


    @property
    def bit_depth(self):
        return self._bit_depth

    @bit_depth.setter
    def bit_depth(self, value):
        _type = types.StringType
        if type(value) == _type:
            self._bit_depth = value
        else:
            raise ValueError("Bit depth must be of %s" % (str(_type)))

    @property
    def sample_rate(self):
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        _type = types.IntType
        if type(value) == _type:
            self._sample_rate = value
        else:
            raise ValueError("Sample Rate must be of %s" % (str(_type)))

class AudioOutputConfiguration(object):
    def __init__(self, souce_dict = {}):
        self._bit_depth = souce_dict.get(u'bit_depth', None)
        self._sample_rate = souce_dict.get(u'sample_rate', None)
        self._modulation_on_frequency = souce_dict.get(u'modulation_on_frequency', None)
        self._modulation_off_frequency = souce_dict.get(u'modulation_off_frequency', None)

    def toDict(self):
        return { 
        u'bit_depth': self._bit_depth,
        u'sample_rate' : self._sample_rate,
        u'modulation_on_frequency': self._modulation_on_frequency,
        u'modulation_off_frequency' : self._modulation_off_frequency
        }

    @property
    def bit_depth(self):
        return self._bit_depth

    @bit_depth.setter
    def bit_depth(self, value):
        _type = types.StringType
        if type(value) == _type:
            self._bit_depth = value
        else:
            raise ValueError("Bit depth must be of %s" % (str(_type)))

    @property
    def sample_rate(self):
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        _type = types.IntType
        if type(value) == _type:
            self._sample_rate = value
        else:
            raise ValueError("Sample Rate must be of %s" % (str(_type)))


    @property
    def modulation_on_frequency(self):
        return self._modulation_on_frequency

    @modulation_on_frequency.setter
    def modulation_on_frequency(self, value):
        _type = types.IntType
        if type(value) == _type:
            self._modulation_on_frequency = value
        else:
            raise ValueError("Modulation On Frequency must be of %s" % (str(_type)))


    @property
    def modulation_off_frequency(self):
        return self._modulation_off_frequency

    @modulation_off_frequency.setter
    def modulation_off_frequency(self, value):
        _type = types.IntType
        if type(value) == _type:
            self._modulation_off_frequency = value
        else:
            raise ValueError("Sample Rate must be of %s" % (str(_type)))

class AudioConfiguration(object):
    def __init__(self, souce_dict = {}):
        self._input = AudioInputConfiguration(souce_dict.get(u'input', {}))
        self._output = AudioOutputConfiguration(souce_dict.get(u'output', {}))

    def toDict(self):
        return { 
        u'input': self._input.toDict(),
        u'output' : self._output.toDict()
        }

    @property
    def input(self):
        return self._input

    @property
    def output(self):
        return self._output

class Configuration(object):
    def __init__(self, souce_dict = {}):
        self._name = souce_dict.get(u'name', None)
        self._audio = AudioConfiguration(souce_dict = souce_dict.get(u'audio', {}))
        self._serial = SerialZAxisConfiguration(souce_dict = souce_dict.get(u'serial', {}))
        self._calibration = CalibrationConfiguration(souce_dict = souce_dict.get(u'calibration', {}))
        self._dripper = DripperConfiguration(souce_dict = souce_dict.get(u'dripper', {}))
        self._options = OptionsConfiguration(souce_dict = souce_dict.get(u'options', {}))




    def toDict(self):
        return { 
        u'name': self._name,
        u'audio' : self._audio.toDict(),
        u'serial' : self._serial.toDict(),
        u'calibration' : self._calibration.toDict(),
        u'dripper' : self._dripper.toDict(),
        u'options' : self._options.toDict(),
        }

    def toJson(self):
        di = self.toDict()
        return json.dumps(di)

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
    def name(self, value):
        _type = types.StringType
        if type(value) == _type:
            self._name = value
        else:
            raise ValueError("Name must be of %s" % (str(_type)))

#TODO: JT 2014-05-28 Find out where this really lives
class ConfigurationGenerator(object):
    def default_configuration(self):
        configuration = Configuration()
        
        configuration.name                                 = "Peachy Printer"

        configuration.audio.output.bit_depth               = "16 bit"
        configuration.audio.output.sample_rate             = 48000
        configuration.audio.output.modulation_on_frequency = 8000
        configuration.audio.output.modulation_off_frequency= 2000
        configuration.audio.input.bit_depth                = "8 bit"
        configuration.audio.input.sample_rate              = 44100

        configuration.options.sublayer_height_mm           = 0.01
        configuration.options.laser_thickness_mm           = 0.5
        configuration.options.draw_speed                   = 200.0
        configuration.options.laser_offset                 = [0.0,0.0]

        configuration.dripper.drips_per_mm                 = 100.0
        configuration.dripper.max_lead_distance_mm         = 1.0

        configuration.calibration.max_deflection           = 0.75
        configuration.calibration.height                   = 40.0
        configuration.calibration.scale                    = 1.0
        configuration.calibration.lower_points             = {(1.0, 1.0):( 40.0,  40.0), ( 1.0, -1.0):( 40.0, -40.0), (-1.0, -1.0):( -40.0, -40.0), (-1.0, 1.0):(-40.0, 40.0)}
        configuration.calibration.upper_points             = {(1.0, 1.0):( 30.0,  30.0), ( 1.0, -1.0):( 30.0, -30.0), (-1.0, -1.0):( -30.0, -30.0), (-1.0, 1.0):(-30.0, 30.0)}

        configuration.serial.on                            = False
        configuration.serial.port                          = "COM2"
        configuration.serial.on_command                    = "1"
        configuration.serial.off_command                   = "0"

        return configuration

class FileBasedConfigurationManager(ConfigurationManager):
    
    CONFIGURATION_EXTENSION = '.cfg'

    def __init__(self):
        pass


    def list(self):
        printers = []
        if os.path.exists(config.PEACHY_PATH):
            for file_name in os.listdir(config.PEACHY_PATH):
                if file_name.endswith(self.CONFIGURATION_EXTENSION):
                    pth = os.path.join(self._path(), file_name)
                    configuration = self._load_configuration(pth)
                    if configuration:
                        printers.append(configuration.name)
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
            try:
                data = file_handle.read()
                conf = Configuration(json.loads(data))
                return conf
            except Exception as ex:
                logging.error("Error loading file: %s" % ex)
                return None


    def save(self, configuration):
        filename = self._get_file_name(configuration.name)
        with open(filename,'w') as file_handle:
            file_handle.write(configuration.toJson())
        
    def new(self, printer_name):
        new_printer_config = ConfigurationGenerator().default_configuration()
        new_printer_config.name = printer_name
        return new_printer_config

    def _path(self):
        if not os.path.exists(config.PEACHY_PATH):
            os.makedirs(config.PEACHY_PATH)
        return config.PEACHY_PATH

    def _get_file_name(self, name):
        safe_name = ''.join( l for l in name if l.isalnum() )
        filename = safe_name + self.CONFIGURATION_EXTENSION
        return os.path.join(self._path(), filename)

