import pyaudio
import time
import numpy
import math
import itertools
import os,sys

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))

from laser_control import AudioModulationLaserControl
from audiofiler import PathToAudio
from audio import AudioWriter
from controller import Controller
from transformer import TuningTransformer
from domain.commands import *
from domain.layer_generator import LayerGenerator
from configuration import FileBasedConfigurationManager
from layer_generators import SinglePointGenerator, CalibrationLineGenerator


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

    def __init__(self):
        config = FileBasedConfigurationManager().load('Test')
        self.writer = AudioWriter(config['output_sample_frequency'],config['output_bit_depth'])
        self.laser_control = AudioModulationLaserControl(config['output_sample_frequency'], config['on_modulation_frequency'], config['off_modulation_frequency'])
        self.transformer = TuningTransformer()
        self.path2audio = PathToAudio(self.laser_control.actual_samples_per_second, self.transformer,0.5)
        self.layer_generator = CalibrationLineGenerator()
        self.controller = Controller(self.laser_control, self.path2audio, self.writer,self.layer_generator)

    def go(self):
        self.controller.start()


if __name__ == '__main__':
    g = SpikeRunner()
    g.go()

