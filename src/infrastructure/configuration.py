import os
import hashlib
import config
import json
import types
import logging
import re


from domain.configuration_manager import ConfigurationManager

class ConfigurationBase(object):
    def get(self, source, key, default = None):
        if (key in source):
            value = source[key]
            if type(value) == types.UnicodeType:
                value = str(value)
            return value
        else:
            return default

    def toDict(self):
        d = {}
        for key, value in self.__dict__.items():
            if issubclass(value.__class__,ConfigurationBase):
                d[unicode(key)[1:]] = value.toDict()
            else:
                d[unicode(key)[1:]] = value
        return d

class CureRateConfiguration(ConfigurationBase):
    def __init__(self, source = {}):
        self._base_height    = self.get(source, u'base_height',  3.0)
        self._total_height   = self.get(source, u'total_height', 23.0)
        self._start_speed    = self.get(source, u'start_speed',  50.0)
        self._finish_speed   = self.get(source, u'finish_speed', 200.0)
        self._draw_speed     = self.get(source, u'draw_speed',   100.0)
        self._use_draw_speed = self.get(source, u'use_draw_speed', True)

    @property
    def base_height(self):
        return self._base_height

    @base_height.setter
    def base_height(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._base_height = value
        else:
            raise ValueError("Base Height must be of %s was %s" % (_type, type(value)))

    @property
    def total_height(self):
        return self._total_height

    @total_height.setter
    def total_height(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._total_height = value
        else:
            raise ValueError("Total Height must be of %s was %s" % (_type, type(value)))

    @property
    def start_speed(self):
        return self._start_speed

    @start_speed.setter
    def start_speed(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._start_speed = value
        else:
            raise ValueError("Start speed must be of %s was %s" % (_type, type(value)))

    @property
    def finish_speed(self):
        return self._finish_speed

    @finish_speed.setter
    def finish_speed(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._finish_speed = value
        else:
            raise ValueError("Finish Speed must be of %s was %s" % (_type, type(value)))

    @property
    def draw_speed(self):
        return self._draw_speed

    @draw_speed.setter
    def draw_speed(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._draw_speed = value
        else:
            raise ValueError("Draw Speed must be of %s was %s" % (_type, type(value)))

    @property
    def use_draw_speed(self):
        return self._use_draw_speed

    @use_draw_speed.setter
    def use_draw_speed(self, value):
        _type = types.BooleanType
        if type(value) == _type:
            self._use_draw_speed = value
        else:
            raise ValueError("Use draw Speed must be of %s was %s" % (_type, type(value)))


class EmailConfiguration(ConfigurationBase):
    def __init__(self, source = {}):
        self._on = self.get(source, u'on', False)
        self._port = self.get(source, u'port',25)
        self._host = self.get(source, u'host', 'some.smtp.server')
        self._sender = self.get(source, u'sender','senderemail@email.com')
        self._recipient = self.get(source, u'recipient','recipientemail@email.com')
        self._email_regex = r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b'

    def valid_email(self,potential_email):
        m = re.match(self._email_regex, potential_email,re.I)
        if m != None:
            return True
        return False

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
        _type = types.IntType
        if type(value) == _type:
            self._port = value
        else:
            raise ValueError("Port must be of %s was %s" % (_type, type(value)))

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        _type = types.StringType
        if type(value) == _type:
            self._host = value
        else:
            raise ValueError("Hostname must be %s" % (str(_type)))

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, value):
        _type = types.StringType
        if type(value) == _type and self.valid_email(value):
            self._sender = value
        else:
            raise ValueError("Sender must be %s" % (str(_type)))

    @property
    def recipient(self):
        return self._recipient

    @recipient.setter
    def recipient(self, value):
        _type = types.StringType
        if type(value) == _type and self.valid_email(value):
            self._recipient = value
        else:
            raise ValueError("Reciepient must be of %s" % (str(_type)))

class OptionsConfiguration(ConfigurationBase):
    def __init__(self, source = {}):
        self._shufflelayers_frequency = self.get(source, u'shufflelayers_frequency', 1.0)
        self._post_fire_delay = self.get(source, u'post_fire_delay', 5)
        self._laser_offset = self.get(source, u'laser_offset', [0.0,0.0])
        self._sublayer_height_mm = self.get(source, u'sublayer_height_mm', 0.01)
        self._laser_thickness_mm = self.get(source, u'laser_thickness_mm',0.5)
        self._scaling_factor = self.get(source, u'scaling_factor',1.0)
        self._overlap_amount = self.get(source, u'overlap_amount',1.0)
        self._use_shufflelayers = self.get(source, u'use_shufflelayers', True)

        self._use_sublayers = self.get(source, u'use_sublayers', False)
        self._use_overlap = self.get(source, u'use_overlap',True)
        self._print_queue_delay = self.get(source, u'print_queue_delay', 0.0)
        self._pre_layer_delay = self.get(source, u'pre_layer_delay',0.0)
        self._wait_after_move_milliseconds = self.get(source, u'wait_after_move_milliseconds',5)

    @property
    def post_fire_delay(self):
        return self._post_fire_delay

    @post_fire_delay.setter
    def post_fire_delay(self, value):
        _type = types.IntType
        if type(value) == _type:
            self._wait_after_move_milliseconds = value
        else:
            raise ValueError("Post Fire Delay must be of %s" % (str(_type)))

    @property
    def shufflelayers_frequency(self):
        return self._shufflelayers_frequency

    @shufflelayers_frequency.setter
    def shufflelayers_frequency(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._pre_layer_delay = value
        else:
            raise ValueError("Shuffle Layers must be of %s" % (str(_type)))

    @property
    def wait_after_move_milliseconds(self):
        return self._wait_after_move_milliseconds

    @wait_after_move_milliseconds.setter
    def wait_after_move_milliseconds(self, value):
        _type = types.IntType
        if type(value) == _type:
            self._wait_after_move_milliseconds = value
        else:
            raise ValueError("Wait after move milliseconds must be of %s" % (str(_type)))

    @property
    def pre_layer_delay(self):
        return self._pre_layer_delay

    @pre_layer_delay.setter
    def pre_layer_delay(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._pre_layer_delay = value
        else:
            raise ValueError("Pre Layer Delay must be of %s" % (str(_type)))


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

    @property
    def scaling_factor(self):
        return self._scaling_factor

    @scaling_factor.setter
    def scaling_factor(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._scaling_factor = value
        else:
            raise ValueError("Scaling Factor must be of %s" % (str(_type)))

    @property
    def overlap_amount(self):
        return self._overlap_amount

    @overlap_amount.setter
    def overlap_amount(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._overlap_amount = value
        else:
            raise ValueError("overlap_amount must be of %s" % (str(_type)))


    @property
    def use_shufflelayers(self):
        return self._use_shufflelayers

    @use_shufflelayers.setter
    def use_shufflelayers(self, value):
        _type = types.BooleanType
        if type(value) == _type:
            self._use_shufflelayers = value
        else:
            raise ValueError("Use use_shufflelayers must be of %s" % (str(_type)))


    @property
    def use_sublayers(self):
        return self._use_sublayers

    @use_sublayers.setter
    def use_sublayers(self, value):
        _type = types.BooleanType
        if type(value) == _type:
            self._use_sublayers = value
        else:
            raise ValueError("use_sublayers must be of %s" % (str(_type)))


    @property
    def use_overlap(self):
        return self._use_overlap

    @use_overlap.setter
    def use_overlap(self, value):
        _type = types.BooleanType
        if type(value) == _type:
            self._use_overlap = value
        else:
            raise ValueError("use_overlap must be of %s" % (str(_type)))


    @property
    def print_queue_delay(self):
        return self._print_queue_delay

    @print_queue_delay.setter
    def print_queue_delay(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._print_queue_delay = value
        else:
            raise ValueError("print_queue_delay must be of %s" % (str(_type)))

class DripperConfiguration(ConfigurationBase):
    def __init__(self, source = {}):
        self._max_lead_distance_mm = self.get(source, u'max_lead_distance_mm',1.0)
        self._drips_per_mm = self.get(source, u'drips_per_mm',100.0)
        self._dripper_type = self.get(source, u'dripper_type','audio')
        self._emulated_drips_per_second = self.get(source,u'emulated_drips_per_second',100.0)
        self._photo_zaxis_delay = self.get(source,u'photo_zaxis_delay',3.0)
    
    @property
    def photo_zaxis_delay(self):
        return self._photo_zaxis_delay
    
    @photo_zaxis_delay.setter
    def photo_zaxis_delay(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._photo_zaxis_delay = value
        else:
            raise ValueError("Photo ZAxis Delay must be of %s" % (str(_type)))

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
    def dripper_type(self):
        return self._dripper_type
    
    @dripper_type.setter
    def dripper_type(self, value):
        _type = types.StringType
        if type(value) == _type:
            self._dripper_type = value
        else:
            raise ValueError("Dripper Type must be of %s" % (str(_type)))
    
    @property
    def emulated_drips_per_second(self):
        return self._emulated_drips_per_second
    
    @emulated_drips_per_second.setter
    def emulated_drips_per_second(self, value):
        _type = types.FloatType
        if type(value) == _type:
            self._emulated_drips_per_second = value
        else:
            raise ValueError("Emulated Drips Per Second must be of %s" % (str(_type)))
    
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

class CalibrationConfiguration(ConfigurationBase):
    def __init__(self, source = {}):
        self._max_deflection = self.get(source, u'max_deflection', 0.95)
        self._height = self.get(source, u'height',40.0)
        self._lower_points = [ ((l[0][0],l[0][1]), (l[1][0],l[1][1])) for l in source.get(u'lower_points', [[[0.0, 1.0],[-40.0, 40.0]],[[1.0, 0.0],[40.0, -40.0]],[[0.0, 0.0],[-40.0, -40.0]], [[1.0, 1.0],[40.0, 40.0]]]) ]
        self._upper_points = [ ((u[0][0],u[0][1]), (u[1][0],u[1][1])) for u in source.get(u'upper_points', [[[0.0, 1.0],[-30.0, 30.0]],[[1.0, 0.0],[30.0, -30.0]],[[0.0, 0.0],[-30.0, -30.0]], [[1.0, 1.0],[30.0, 30.0]]]) ]

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
        return dict(self._lower_points)

    @lower_points.setter
    def lower_points(self, value):
        _type = types.DictType
        if type(value) == _type:
            self._lower_points = [ (k,v) for k,v in value.items() ]
        else:
            raise ValueError("Data must be of %s" % (str(_type)))
    
    @property
    def upper_points(self):
        return dict(self._upper_points)

    @upper_points.setter
    def upper_points(self, value):
        _type = types.DictType
        if type(value) == _type:
            self._upper_points = [ (k,v) for k,v in value.items() ]
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

class SerialConfiguration(ConfigurationBase):
    def __init__(self, source = {}):
        self._on = self.get(source, u'on', False)
        self._port = self.get(source, u'port','COM2')
        self._on_command = self.get(source, u'on_command','7')
        self._off_command = self.get(source, u'off_command','8')
        self._layer_started = self.get(source, u'layer_started','S')
        self._layer_ended = self.get(source, u'layer_ended','E')
        self._print_ended = self.get(source, u'print_ended','Z')


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
            raise ValueError("Port must be of %s was %s" % (_type, type(value)))

    @property
    def on_command(self):
        return self._on_command

    @on_command.setter
    def on_command(self, value):
        _type = types.StringType
        if type(value) == _type:
            self._on_command = value
        else:
            raise ValueError("On command must be %s" % (str(_type)))

    @property
    def off_command(self):
        return self._off_command

    @off_command.setter
    def off_command(self, value):
        _type = types.StringType
        if type(value) == _type:
            self._off_command = value
        else:
            raise ValueError("Off command must be %s" % (str(_type)))

    @property
    def layer_started(self):
        return self._layer_started

    @layer_started.setter
    def layer_started(self, value):
        _type = types.StringType
        if type(value) == _type:
            self._layer_started = value
        else:
            raise ValueError("Layer started command must be of %s" % (str(_type)))

    @property
    def layer_ended(self):
        return self._layer_ended

    @layer_ended.setter
    def layer_ended(self, value):
        _type = types.StringType
        if type(value) == _type:
            self._layer_ended = value
        else:
            raise ValueError("Layer ended command must be of %s" % (str(_type)))

    @property
    def print_ended(self):
        return self._print_ended

    @print_ended.setter
    def print_ended(self, value):
        _type = types.StringType
        if type(value) == _type:
            self._print_ended = value
        else:
            raise ValueError("Print ended command must be of %s" % (str(_type)))

class AudioInputConfiguration(ConfigurationBase):
    def __init__(self, source = {}):
        self._bit_depth = self.get(source, u'bit_depth', "16 bit")
        self._sample_rate = self.get(source, u'sample_rate', 44100)

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

class AudioOutputConfiguration(ConfigurationBase):
    def __init__(self, source = {}):
        self._bit_depth = self.get(source, u'bit_depth',"16 bit")
        self._sample_rate = self.get(source, u'sample_rate', 48000)
        self._modulation_on_frequency = self.get(source, u'modulation_on_frequency', 8000)
        self._modulation_off_frequency = self.get(source, u'modulation_off_frequency',2000)

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

class AudioConfiguration(ConfigurationBase):
    def __init__(self, source = {}):
        self._input = AudioInputConfiguration(source.get(u'input', {}))
        self._output = AudioOutputConfiguration(source.get(u'output', {}))

    @property
    def input(self):
        return self._input

    @property
    def output(self):
        return self._output

class Configuration(ConfigurationBase):
    def __init__(self, source = {}):
        self._name = self.get(source, u'name','Peachy Printer')
        self._audio = AudioConfiguration(source = source.get(u'audio', {}))
        self._serial = SerialConfiguration(source = source.get(u'serial', {}))
        self._calibration = CalibrationConfiguration(source = source.get(u'calibration', {}))
        self._dripper = DripperConfiguration(source = source.get(u'dripper', {}))
        self._options = OptionsConfiguration(source = source.get(u'options', {}))
        self._email = EmailConfiguration(source = source.get(u'email', {}))
        self._cure_rate = CureRateConfiguration(source = source.get(u'cure_rate', {}))

    def toJson(self):
        di = self.toDict()
        return json.dumps(di, sort_keys = True, indent =2)

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
    def email(self):
        return self._email

    @property
    def cure_rate(self):
        return self._cure_rate

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
        configuration.audio.input.bit_depth                = "16 bit"
        configuration.audio.input.sample_rate              = 44100

        configuration.options.sublayer_height_mm           = 0.01
        configuration.options.laser_thickness_mm           = 0.5
        configuration.options.laser_offset                 = [0.0,0.0]
        configuration.options.scaling_factor               = 1.0
        configuration.options.overlap_amount               = 1.0
        configuration.options.use_shufflelayers            = True
        configuration.options.use_sublayers                = False
        configuration.options.use_overlap                  = True
        configuration.options.print_queue_delay            = 0.0
        configuration.options.pre_layer_delay              = 0.0

        configuration.dripper.drips_per_mm                 = 100.0
        configuration.dripper.max_lead_distance_mm         = 1.0
        configuration.dripper.dripper_type                 = 'audio'
        configuration.dripper.emulated_drips_per_second    = 1.0
        configuration.dripper.photo_zaxis_delay            = 3.0

        configuration.calibration.max_deflection           = 0.95
        configuration.calibration.height                   = 40.0
        configuration.calibration.lower_points             = {(1.0, 1.0):( 40.0,  40.0), ( 1.0, 0.0):( 40.0, -40.0), (0.0, 0.0):( -40.0, -40.0), (0.0, 1.0):(-40.0, 40.0)}
        configuration.calibration.upper_points             = {(1.0, 1.0):( 30.0,  30.0), ( 1.0, 0.0):( 30.0, -30.0), (0.0, 0.0):( -30.0, -30.0), (0.0, 1.0):(-30.0, 30.0)}

        configuration.serial.on                            = False
        configuration.serial.port                          = "COM2"
        configuration.serial.on_command                    = "7"
        configuration.serial.off_command                   = "8"
        configuration.serial.layer_started                 = "S"
        configuration.serial.layer_ended                   = "E"
        configuration.serial.print_ended                   = "Z"

        configuration.email.on                             = False
        configuration.email.port                           = 25
        configuration.email.host                           = "some.smtp.server"
        configuration.email.sender                         = "senderemail@email.com"
        configuration.email.recipient                      = "recipientemail@email.com"

        configuration.cure_rate.base_height                = 3.0
        configuration.cure_rate.total_height               = 23.0
        configuration.cure_rate.start_speed                = 50.0
        configuration.cure_rate.finish_speed               = 200.0
        configuration.cure_rate.draw_speed                 = 100.0
        configuration.cure_rate.use_draw_speed             = True



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

