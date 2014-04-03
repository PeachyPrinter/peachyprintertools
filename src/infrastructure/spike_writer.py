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
from controller import Controller
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

from domain.layer_generator import LayerGenerator

class SquareLayerGenerator(LayerGenerator):
    def __init__(self, radius = 1.0,speed = 1.0):
        self.radius = radius
        self.speed = speed
        self.pattern = [[-1.0,-1.0],[1.0,-1.0],[1.0,1.0],[-1.0,1.0]]
        self.last_xy = [0.0,0.0]

    def next(self):
        layer = Layer(0.0)
        for x,y in self.pattern:
            next_xy = [ x * self.radius, y * self.radius]
            layer.commands.append(LateralDraw(self.last_xy,next_xy,self.speed))
            self.last_xy = next_xy
        return layer

class SpikeRunner(object):
    bit_depth = 16
    freq = 48000
    onfreq = 12000
    offreq = 8000

    def __init__(self):
        self.writer = AudioWriter(self.freq,self.bit_depth)
        self.laser_control = AudioModulationLaserControl(self.freq, self.onfreq, self.offreq)
        self.path2audio = PathToAudio(self.laser_control.actual_samples_per_second, 4,4,0.5)
        self.layer_generator = SquareLayerGenerator()
        self.controller = Controller(self.laser_control, self.path2audio, self.writer,self.layer_generator)

    def go(self):
        self.controller.start()


if __name__ == '__main__':
    g = SpikeRunner()
    g.go()

