import pyaudio
import time
import numpy
import math
import itertools
import os,sys
import logging
from decimal import *

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
        config = FileBasedConfigurationManager().new('Beer')
        self.writer = AudioWriter(config['output_sample_frequency'],config['output_bit_depth'])
        self.laser_control = AudioModulationLaserControl(config['output_sample_frequency'], config['on_modulation_frequency'], config['off_modulation_frequency'])
        self.transformer = TuningTransformer(scale = 0.75)
        self.path2audio = PathToAudio(self.laser_control.actual_samples_per_second, self.transformer,0.5)
        self.layer_generator = SinglePointGenerator([1.00,0.0])
        self.controller = Controller(self.laser_control, self.path2audio, self.writer,self.layer_generator)

    def go(self):
        self.controller.start()

    def stop(self):
        self.controller.stop()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='WARNING')
    g = SpikeRunner()
    x = -1.05
    g.layer_generator.xy = [0.0, 0.0]
    g.go()
    print("X: %s " % 0.0)
    try:
        while x <= 1.0:
                k=raw_input()
                x = x + 0.05
                if x > 1.0 and x < 1.05:
                    x = 1.0
                print("X: %s " % x)
                g.layer_generator.xy = [x, 0.0]
    except KeyboardInterrupt:
        g.stop()
    g.stop()
    exit()
    


