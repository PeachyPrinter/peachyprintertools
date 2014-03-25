import math
import numpy
from fractions import gcd

from domain.laser_control import LaserControl


class AudioModulationLaserControl(LaserControl):
    samples_per_second = None
    _MODULATION_AMPLITUDE_RATIO = 0.25
    _SOURCE_AMPLITUDE_RATIO = 1.0 - _MODULATION_AMPLITUDE_RATIO

    def __init__(self, sampling_rate, on_frequency, off_frequency):
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

    def _lcm(self, numbers):
        return reduce(lambda x, y: (x*y)/gcd(x,y), numbers, 1)

    def _get_cos_wave(self,steps, cycles):
        wave = []
        scale = 2.0 * math.pi
        for _ in range(0, cycles):
            for i in range(0,int(steps)):
                cos_wave = math.cos(i * 1.0 / steps * 1.0 * scale )
                shifted = (cos_wave + 1.0) / 2.0
                wave.append(shifted)
        return wave

    def modulate(self, data):
        pattern = self.on_laser_wave if self._laser_on else self.off_laser_wave
        for (left,right) in data:
            l = numpy.multiply( [ 0.25 + (left  * self._SOURCE_AMPLITUDE_RATIO)] , pattern)
            r = numpy.multiply( [ 0.25 + (right * self._SOURCE_AMPLITUDE_RATIO)] , pattern)
            yield numpy.column_stack((l, r))
