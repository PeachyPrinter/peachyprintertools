import pyaudio
import time
import numpy
import math
import itertools
import os,sys

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))

from laser_control import AudioModulationLaserControl
from audiofiler import PathToAudio
from audio_writer import AudioWriter
from domain.commands import *

class SpikeController(object):
    def __init__(self):
        self.current_pos = [0.0,0.0]
        self.writer = AudioWriter(48000,16)
        self.modulator = AudioModulationLaserControl(48000, 12000, 8000)
        self.path2audio = PathToAudio(self.modulator.actual_samples_per_second, 4,4,0.5)

    def process(self, commands):
        self.modulator.set_laser_on()
        for command in commands:
            if type(command) == LateralDraw:
                path = self.path2audio.process(self.current_pos,(command.x, command.y),command.speed)
                modulated = self.modulator.modulate(transformed_path)
                self.writer.write_chunk(modulated)
                self.current_pos = [command.x,command.y]

    def go(self):
        square = [[-1.0,-1.0],[1.0,-1.0],[1.0,1.0],[-1.0,1.0]]
        zero = [[0.0,0.0]]
        for points in itertools.cycle(square):
            self.process([LateralDraw(points[0],points[1], 0.5)])
        self.writer.close()

if __name__ == '__main__':
    g = SpikeController()
    g.go()

