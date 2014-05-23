import math
import numpy
import logging
from fractions import gcd

from domain.laser_control import LaserControl


class AudioModulationLaserControl(LaserControl):
    _MODULATION_AMPLITUDE_RATIO = 0.25
    _SOURCE_AMPLITUDE_RATIO = 1.0 - _MODULATION_AMPLITUDE_RATIO

    def __init__(self, sampling_rate, on_frequency, off_frequency, offset=[0.0,0.0]):
        self._x_offset, self._y_offset = offset
        logging.info("Laser Control: Modulation On: %s" % on_frequency )
        logging.info("Laser Control: Modulation Off: %s" % off_frequency )
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
