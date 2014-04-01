import pyaudio
import time
import numpy
import math
import itertools
import os,sys

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))

from laser_control import AudioModulationLaserControl
from audiofiler import PathToAudio
from domain.commands import *

class SpikeWriter(object):
    MAX_S16 = (math.pow(2, 15) - 1.0) * 1.0

    def __init__(self):
        pa = pyaudio.PyAudio()
        self.outstream = pa.open(format=pa.get_format_from_width(2, unsigned=False),
                 channels=2,
                 rate=48000,
                 output=True,
                 frames_per_buffer=int(48000/8))
        self.outstream.start_stream()

    def write(self,inputstream):
        for values in inputstream:
            print (values)
            frameset = self.to_frame(values)
            da_buffer = self.outstream.get_write_available()
            while da_buffer < len(frameset):
                time.sleep(0.1)
                da_buffer = self.outstream.get_write_available()
            self.outstream.write(frameset)

    def to_frame(self, values):
        # print(values)
        values = numpy.rint( values * self.MAX_S16)
        mod = values.astype(numpy.dtype('<i2'))
        return mod.tostring()

    def close(self):
        self.outstream.stop_stream()
        self.outstream.close()

class SpikeController(object):
    def __init__(self):
        self.current_pos = [0.0,0.0]
        self.writer = SpikeWriter()
        self.modulator = AudioModulationLaserControl(48000, 12000, 8000)
        self.path2audio = PathToAudio(self.modulator.actual_samples_per_second, 2.0,2.0,0.5)

    def process(self, commands):
        self.modulator.set_laser_on()
        for command in commands:
            if type(command) == LateralDraw:
                path = self.path2audio.process(self.current_pos,(command.x, command.y),command.speed)
                modulated = self.modulator.modulate(path)
                self.writer.write(modulated)
                self.current_pos = [command.x,command.y]

    def go(self):
        square = [[-1.0,-1.0],[1.0,-1.0],[1.0,1.0],[-1.0,1.0]]
        zero = [[0.0,0.0]]
        for points in itertools.cycle(zero):
            self.process([LateralDraw(points[0],points[1], 0.5)])
        self.writer.close()

if __name__ == '__main__':
    g = SpikeController()
    g.go()

