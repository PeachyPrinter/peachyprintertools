import unittest
import StringIO
import os
import sys
import time
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

import test_helpers
from mock import patch

from peachyprinter.infrastructure.gcode_layer_generator import GCodeReader, GCodeToLayerGenerator, GCodeCommandReader
from peachyprinter.infrastructure.layer_generators import *
from peachyprinter.infrastructure.transformer import *
from peachyprinter.domain.commands import * 

# class GcodeUnifiedPerformanceTest(unittest.TestCase):
#     def test_performanace_julia_vase_raw(self):
#         layer_times = []
#         afile = open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'test_data','julia.gcode'), 'r')
#         start_time = time.time()
#         layers = GCodeReader(afile).get_layers()
#         running = True
#         while running:
#             try:
#                 layer_start = time.time()
#                 layer = layers.next()
#                 for command in layer.commands:
#                     pass
#                 layer_times.append(time.time() - layer_start)
#             except StopIteration:
#                 running = False
#         total_time = time.time() - start_time
#         print("Raw")
#         print("Total Time: %s " % total_time)
#         print("Layers: %s" % len(layer_times))
#         print("Longest: %s" % max(layer_times))
#         print("Shortest: %s" % min(layer_times))
#         print("Mean: %s" % (sum(layer_times) / len(layer_times) * 1.0))
#         afile.close()

#     def test_performanace_julia_vase_shuffled(self):
#         layer_times = []
#         afile = open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'test_data','julia.gcode'), 'r')
#         start_time = time.time()
#         layers = GCodeReader(afile).get_layers()
#         layers = ShuffleGenerator(layers)
#         running = True
#         while running:
#             try:
#                 layer_start = time.time()
#                 layer = layers.next()
#                 for command in layer.commands:
#                     pass
#                 layer_times.append(time.time() - layer_start)
#             except StopIteration:
#                 running = False
#         total_time = time.time() - start_time
#         print("Shuffled")
#         print("Total Time: %s " % total_time)
#         print("Layers: %s" % len(layer_times))
#         print("Longest: %s" % max(layer_times))
#         print("Shortest: %s" % min(layer_times))
#         print("Mean: %s" % (sum(layer_times) / len(layer_times) * 1.0))
#         afile.close()
    
#     def test_performanace_julia_vase_overlaped(self):
#         layer_times = []
#         afile = open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'test_data','julia.gcode'), 'r')
#         start_time = time.time()
#         layers = GCodeReader(afile).get_layers()
#         layers = OverLapGenerator(layers, 1.0)
#         running = True
#         while running:
#             try:
#                 layer_start = time.time()
#                 layer = layers.next()
#                 for command in layer.commands:
#                     pass
#                 layer_times.append(time.time() - layer_start)
#             except StopIteration:
#                 running = False
#         total_time = time.time() - start_time
#         print("Overlaped")
#         print("Total Time: %s " % total_time)
#         print("Layers: %s" % len(layer_times))
#         print("Longest: %s" % max(layer_times))
#         print("Shortest: %s" % min(layer_times))
#         print("Mean: %s" % (sum(layer_times) / len(layer_times) * 1.0))
#         afile.close()

#     def test_performanace_julia_vase_sublayered(self):
#         layer_times = []
#         afile = open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'test_data','julia.gcode'), 'r')
#         start_time = time.time()
#         layers = GCodeReader(afile).get_layers()
#         layers = SubLayerGenerator(layers,0.01)
#         running = True
#         while running:
#             try:
#                 layer_start = time.time()
#                 layer = layers.next()
#                 for command in layer.commands:
#                     pass
#                 layer_times.append(time.time() - layer_start)
#             except StopIteration:
#                 running = False
#         total_time = time.time() - start_time
#         print("Sublayered")
#         print("Total Time: %s " % total_time)
#         print("Layers: %s" % len(layer_times))
#         print("Longest: %s" % max(layer_times))
#         print("Shortest: %s" % min(layer_times))
#         print("Mean: %s" % (sum(layer_times) / len(layer_times) * 1.0))
#         afile.close()

#     def test_performanace_julia_vase_all(self):
#         layer_times = []
#         afile = open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'test_data','julia.gcode'), 'r')
#         start_time = time.time()
#         layers = GCodeReader(afile).get_layers()
#         layers = OverLapGenerator(ShuffleGenerator(SubLayerGenerator(layers, 0.01)),1.0)
#         running = True
#         while running:
#             try:
#                 layer_start = time.time()
#                 layer = layers.next()
#                 for command in layer.commands:
#                     pass
#                 layer_times.append(time.time() - layer_start)
#             except StopIteration:
#                 running = False
#         total_time = time.time() - start_time
#         print("ALL")
#         print("Total Time: %s " % total_time)
#         print("Layers: %s" % len(layer_times))
#         print("Longest: %s" % max(layer_times))
#         print("Shortest: %s" % min(layer_times))
#         print("Mean: %s" % (sum(layer_times) / len(layer_times) * 1.0))
#         afile.close()

class HomogenousTransformerTest(unittest.TestCase):
    def get_layers(self):
        afile = open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'test_data','julia.gcode'), 'r')
        layers = GCodeReader(afile).get_layers()
        layer_list = list(layers)
        print("Layers: %s" % len(layer_list))
        return layer_list

    def get_points(self):
        points = []
        for layer in self.get_layers():
            for command in layer.commands:
                points.append((command.start[0],command.start[1],layer.z))
                points.append((command.end[0],command.end[1],layer.z))
        return points

    def test_performanace(self):
        print("Loading data into memeory")
        points = self.get_points()
        print("Data Loaded")
        point_times = []
        
        running = True

        height = 50.0  
        lower_points = { 
                (1.0, 1.0):( 600.0,  60.0),
                (0.0, 1.0):(-600.0,  60.0),
                (1.0, 0.0):( 600.0, -60.0),
                (0.0, 0.0):(-600.0, -60.0)
                }
        upper_points = { 
                (1.0, 1.0):( 50.0,  50.0),
                (0.0, 1.0):(-50.0,  50.0),
                (1.0, 0.0):( 50.0, -50.0),
                (0.0, 0.0):(-50.0, -50.0)
                }
        scale = 1.0
        transformer = HomogenousTransformer(scale,height,lower_points,upper_points)

        start_time = time.time()
        for point in points:
            point_start = time.time()
            transformer.transform(point)
            point_times.append(time.time() - point_start)
        total_time = time.time() - start_time
        print("Transformer Times")
        print("Total Time: %s " % total_time)
        print("Points: %s" % len(point_times))
        print("Longest: %s" % max(point_times))
        print("Shortest: %s" % min(point_times))
        print("Mean: %s" % (sum(point_times) / len(point_times) * 1.0))

# Total Time: 750.7529459 
# Points: 2268404
# Longest: 0.0162670612335
# Shortest: 0.000221014022827
# Mean: 0.000330474715383


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='ERROR')
    unittest.main()