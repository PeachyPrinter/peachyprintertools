import unittest
import os
import sys
import logging
from mock import patch

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from infrastructure.layer_generators import SinglePointGenerator, CalibrationLineGenerator, StubLayerGenerator, SubLayerGenerator
from domain.commands import *
import test_helpers

class SinglePointGeneratorTests(unittest.TestCase,test_helpers.TestHelpers):
    def test_can_call_next_and_get_specified_command(self):
        layer_generator = SinglePointGenerator([0.0,0.0])
        expected = Layer(0.0, commands = [LateralDraw([0.0,0.0],[0.0,0.0],100.0)])
        actual = layer_generator.next()
        self.assertLayerEquals(expected,actual)

    def test_can_call_next_after_updating_point(self):
        layer_generator = SinglePointGenerator([0.0,0.0])
        expected = Layer(0.0, commands = [LateralDraw([1.0,1.0],[1.0,1.0],100.0)])
        layer_generator.next()
        layer_generator.set([1.0,1.0])
        actual = layer_generator.next()
        self.assertLayerEquals(expected,actual)

class CalibrationLineGeneratorTests(unittest.TestCase,test_helpers.TestHelpers):
    def test_can_call_next_and_get_specified_command(self):
        layer_generator = CalibrationLineGenerator()
        expected = Layer(0.0, commands = [LateralDraw([-1.0,0.0],[1.0,0.0],10.0),LateralDraw([1.0,0.0],[-1.0,0.0],10.0)], )
        actual = layer_generator.next()
        self.assertLayerEquals(expected,actual)

class SublayerGeneratorTests(unittest.TestCase,test_helpers.TestHelpers):
    
    def test_if_sublayer_height_equal_to_layer_height_create_layer(self):
        layer1 = Layer(0.0,[ LateralDraw([0.0,0.0],[0.0,0.0],100.0) ])
        layer2 = Layer(1.0,[ LateralDraw([0.0,0.0],[0.0,0.0],100.0) ])

        inital_generator = StubLayerGenerator([layer1,layer2])

        sublayer_generator = SubLayerGenerator(inital_generator,1.0)

        self.assertLayerEquals(layer1,sublayer_generator.next())
        self.assertLayerEquals(layer2,sublayer_generator.next())

    def test_if_sublayer_height_greater_to_layer_height_create_layer(self):
        layer1 = Layer(0.0,[ LateralDraw([0.0,0.0],[0.0,0.0],100.0) ])
        layer2 = Layer(1.0,[ LateralDraw([0.0,0.0],[0.0,0.0],100.0) ])

        inital_generator = StubLayerGenerator([layer1,layer2])

        sublayer_generator = SubLayerGenerator(inital_generator,10.0)

        self.assertLayerEquals(layer1,sublayer_generator.next())
        self.assertLayerEquals(layer2,sublayer_generator.next())

    def test_if_sublayer_height_more_than_half_of_layer_height_create_layer(self):
        layer1 = Layer(0.0,[ LateralDraw([0.0,0.0],[0.0,0.0],100.0) ])
        layer2 = Layer(1.0,[ LateralDraw([0.0,0.0],[0.0,0.0],100.0) ])

        inital_generator = StubLayerGenerator([layer1,layer2])

        sublayer_generator = SubLayerGenerator(inital_generator,0.51)

        self.assertLayerEquals(layer1,sublayer_generator.next())
        self.assertLayerEquals(layer2,sublayer_generator.next())

    def test_if_sublayer_height_less_than_half_of_layer_height_create_extra_layer(self):
        layer1 = Layer(0.0,[ LateralDraw([0.0,0.0],[0.0,0.0],100.0) ])
        layer2 = Layer(1.0,[ LateralDraw([0.0,0.0],[0.0,0.0],100.0) ])

        inital_generator = StubLayerGenerator([layer1,layer2])

        expected_sublayer = Layer(0.5,[ LateralDraw([0.0,0.0],[0.0,0.0],100.0) ])
        sublayer_generator = SubLayerGenerator(inital_generator,0.5)

        self.assertLayerEquals(layer1,sublayer_generator.next())
        self.assertLayerEquals(expected_sublayer,sublayer_generator.next())
        self.assertLayerEquals(layer2,sublayer_generator.next())

    def test_if_sublayer_height_pt1_and_layer_height_1_create_extra_layers(self):
        layer1 = Layer(0.0,[ LateralDraw([0.0,0.0],[0.0,0.0],100.0) ])
        layer2 = Layer(1.0,[ LateralDraw([0.0,0.0],[0.0,0.0],100.0) ])
        layer3 = Layer(2.0,[ LateralDraw([0.0,0.0],[0.0,0.0],100.0) ])

        inital_generator = StubLayerGenerator([layer1,layer2,layer3])

        expected_sublayers = [ Layer(x / 10.0 ,[ LateralDraw([0.0,0.0],[0.0,0.0],100.0) ]) for x in range(0,21) ]
        sublayer_generator = SubLayerGenerator(inital_generator,0.1)

        for expected_layer in expected_sublayers:
            self.assertLayerEquals(expected_layer,sublayer_generator.next())

        with self.assertRaises(StopIteration):
            sublayer_generator.next()
        
    def test_sublayer_generator_should_shuffle_commands_on_each_layer(self):
        command1 = LateralDraw([0.0,0.0],[0.0,0.0],100.0)
        command2 = LateralDraw([0.0,0.0],[1.0,1.0],100.0)
        layer1 = Layer(0.0,[ command1, command2 ])
        layer2 = Layer(1.0,[ command1 ])
        sub_layer = Layer(0.5, [ command2, command1 ])

        expected_layers = (layer1,sub_layer,layer2)
        inital_generator = StubLayerGenerator([layer1,layer2])


        sublayer_generator = SubLayerGenerator(inital_generator,0.5)

        for expected_layer in expected_layers:
            self.assertLayerEquals(expected_layer,sublayer_generator.next())

        with self.assertRaises(StopIteration):
            sublayer_generator.next()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()