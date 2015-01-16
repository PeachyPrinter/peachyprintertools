import math
import numpy
import logging
from fractions import gcd

from domain.laser_control import LaserControl
from messages import *

import serial


class HACKCON(object):
    HEADER = '@'
    FOOTER = 'A'
    ESCAPE = 'B'

    def __init__(self):
        self.conn = serial.Serial('/dev/ttyACM0')

    def register(self, type_id, handler):
        logging.info("REGISTERED: %s: %s" % (type_id, handler.__name__))

    def send(self, type_id, data):
        packet = self.HEADER + self.escape(chr(type_id) + data) + self.FOOTER
        self.conn.write(packet)
        logging.info("SENT: %s" % repr(packet))

    def escape(self, data):
        out = ''
        for character in data:
            if ord(character) in [self.HEADER, self.FOOTER, self.ESCAPE]:
                out += self.ESCAPE +'%c' % ((~ord(character)) & 0xFF)
            else:
                out += character
        return out


class SerialDataControl(LaserControl):
    NACK_ID = 0
    ACK_ID = 1
    MOVE_ID = 2

    def __init__(self, sampling_rate, on_frequency, off_frequency, offset, connection):
        self._x_offset, self._y_offset = offset

        self._connection = connection
        self._connection.register(self.NACK_ID, self.nackHandler)
        self._connection.register(self.ACK_ID, self.ackHandler)
        self._message_id = 0
        self.asdfscale = pow(2, 16) -1
        off_laser_steps = sampling_rate / off_frequency
        on_laser_steps = sampling_rate / on_frequency
        lcm = self._lcm([off_laser_steps, on_laser_steps])
        self.actual_samples_per_second = sampling_rate / lcm


    def _lcm(self, numbers):
        return reduce(lambda x, y: (x*y)/gcd(x,y), numbers, 1)

    def modulate(self, data):
        for (x, y) in data:
            out_x = int(x * self.asdfscale)
            out_y = int(y * self.asdfscale)
            logging.info(x)
            logging.info(out_x)
            if self.laser_is_on:
                laser = self.scale = pow(2, 8)
            message = Move(self._message_id, out_x, out_y, laser).to_protobuf_bytes()
            self._message_id += 1
            self._connection.send(self.MOVE_ID, message)
        return data

    def ackHandler(self, ack_data):
        pass

    def nackHandler(self, nack_data):
        pass

    def set_offset(self, offset):
        self._x_offset, self._y_offset = offset



class AudioModulationLaserControl(LaserControl):
    _MODULATION_AMPLITUDE_RATIO = 0.25
    _SOURCE_AMPLITUDE_RATIO = 1.0 - _MODULATION_AMPLITUDE_RATIO

    def __init__(self, sampling_rate, on_frequency, off_frequency, offset):
        self._x_offset, self._y_offset = offset
        logging.info("Laser Control: Modulation On: %s" % on_frequency )
        logging.info("Laser Control: Modulation Off: %s" % off_frequency )
        logging.info("Laser Offset: %2.3f, %2.3f" % (self._x_offset,self._y_offset))
        if sampling_rate % on_frequency != 0:
            raise Exception("The on_frequency must divide evenly into sampling_rate")
        if sampling_rate % off_frequency != 0:
            raise Exception("The off_frequency must divide evenly into sampling_rate")
        
        off_laser_steps = sampling_rate / off_frequency
        on_laser_steps = sampling_rate / on_frequency
        lcm = self._lcm([off_laser_steps, on_laser_steps])
        self.actual_samples_per_second = sampling_rate / lcm

        self.off_laser_wave = numpy.array(self._get_cos_wave(off_laser_steps, lcm / off_laser_steps))
        self.on_laser_wave = numpy.array(self._get_cos_wave(on_laser_steps, lcm / on_laser_steps))
        logging.info("Started audio modulation with On Frequency: %s and Off Frequency: %s" % (on_frequency,off_frequency))

    def _lcm(self, numbers):
        return reduce(lambda x, y: (x*y)/gcd(x,y), numbers, 1)

    def _get_cos_wave(self,steps, cycles):
        wave = []
        scale = 2.0 * math.pi
        for _ in range(0, cycles):
            for i in range(0,int(steps)):
                cos_wave = math.cos(i * 1.0 / steps * 1.0 * scale )
                wave.append(cos_wave)
        return wave

    def set_offset(self,offset):
        self._x_offset, self._y_offset = offset

    def modulate(self, data):
        if self._laser_on:
            pattern = self.on_laser_wave
            for (left,right) in data:
                l = numpy.multiply( [ self._MODULATION_AMPLITUDE_RATIO + (left * self._SOURCE_AMPLITUDE_RATIO)] , pattern)
                r = numpy.multiply( [ self._MODULATION_AMPLITUDE_RATIO + (right* self._SOURCE_AMPLITUDE_RATIO)] , pattern)
                yield numpy.column_stack((l, r))
        else:
            pattern = self.off_laser_wave
            for (left,right) in data:
                l = numpy.multiply( [ self._MODULATION_AMPLITUDE_RATIO + ((left  + self._x_offset) * self._SOURCE_AMPLITUDE_RATIO)] , pattern)
                r = numpy.multiply( [ self._MODULATION_AMPLITUDE_RATIO + ((right + self._y_offset) * self._SOURCE_AMPLITUDE_RATIO)] , pattern)
                yield numpy.column_stack((l, r))
