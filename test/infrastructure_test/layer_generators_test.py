import unittest
import os
import sys
import logging
from mock import patch

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from infrastructure.layer_generators import *
from domain.commands import *
import test_helpers

# ----------------- Calibration Generators -----------------------------

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
    def test_next_returns__specified_command(self):
        layer_generator = CalibrationLineGenerator()
        expected = Layer(0.0, commands = [LateralDraw([0.0,0.5],[1.0,0.5],10.0),LateralDraw([1.0,0.5],[0.0,0.5],10.0)], )
        actual = layer_generator.next()
        self.assertLayerEquals(expected,actual)

# --------------  Test Generators  ----------------------------------------


class HilbertGeneratorTests(unittest.TestCase,test_helpers.TestHelpers):
    def test_can_call_next_and_get_specified_command(self):
        layer_generator = HilbertGenerator(order = 1, speed = 100.0, radius = 50.0)
        expected_commands = [
            LateralMove([0.0, 0.0],[-25.0, -25.0],100.0),
            LateralDraw([-25.0, -25.0],[25.0, -25.0],100.0),
            LateralDraw([25.0, -25.0],[25.0, 25.0],100.0),
            LateralDraw([25.0, 25.0],[-25.0, 25.0],100.0)
            ]
        expected = Layer(0.0, commands = expected_commands )
        actual = layer_generator.next()
        self.assertLayerEquals(expected,actual)

    def test_set_speed_changes_speed(self):
        speed = 34.8
        layer_generator = HilbertGenerator(order = 1, radius = 50.0)
        expected_commands = [
            LateralMove([0.0, 0.0],[-25.0, -25.0],speed),
            LateralDraw([-25.0, -25.0],[25.0, -25.0],speed),
            LateralDraw([25.0, -25.0],[25.0, 25.0],speed),
            LateralDraw([25.0, 25.0],[-25.0, 25.0],speed)
            ]
        expected = Layer(0.0, commands = expected_commands )

        layer_generator.set_speed(speed)
        actual = layer_generator.next()

        self.assertLayerEquals(expected,actual)
        
    def test_set_radius_changes_radius(self):
        radius = 20
        layer_generator = HilbertGenerator(order = 1, radius = 50, speed = 100.0)
        expected_commands = [
            LateralMove([0.0, 0.0],[-10.0, -10.0],100.0),
            LateralDraw([-10.0, -10.0],[10.0, -10.0],100.0),
            LateralDraw([10.0, -10.0],[10.0, 10.0],100.0),
            LateralDraw([10.0, 10.0],[-10.0, 10.0],100.0)
            ]
        expected = Layer(0.0, commands = expected_commands )

        layer_generator.set_radius(radius)
        actual = layer_generator.next()
        
        self.assertLayerEquals(expected,actual)



#---------------- Production Generators  -------------------------------------

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

#---------------- Cure Test Generators  -------------------------------------

class CureTestGeneratorTests(unittest.TestCase,test_helpers.TestHelpers):
    def test_total_height_must_exceed_base_height(self):
        with self.assertRaises(Exception):
            CureTestGenerator(10,1,1,1,0.1)

    def test_final_speed_exceeds_start_speed(self):
        with self.assertRaises(Exception):
            CureTestGenerator(1,10,10,1,0.1)

    def test_values_must_be_positive_non_0_numbers_for_all_but_base(self):
        with self.assertRaises(Exception):
            CureTestGenerator('a',10,10,1,0.1)
        with self.assertRaises(Exception):
            CureTestGenerator(1,'a',10,1,0.1)
        with self.assertRaises(Exception):
            CureTestGenerator(1,10,'a',1,0.1)
        with self.assertRaises(Exception):
            CureTestGenerator(1,10,10,'a',0.1)
        with self.assertRaises(Exception):
            CureTestGenerator(1,10,10,1,'a')
        with self.assertRaises(Exception):
            CureTestGenerator(-1,10,10,1,0.1)
        with self.assertRaises(Exception):
            CureTestGenerator(1,-10,10,1,0.1)
        with self.assertRaises(Exception):
            CureTestGenerator(1,10,-1,1,0.1)
        with self.assertRaises(Exception):
            CureTestGenerator(1,10,10,-1,0.1)
        with self.assertRaises(Exception):
            CureTestGenerator(1,10,10,1,-1)
        with self.assertRaises(Exception):
            CureTestGenerator(1,0,10,1,0.1)
        with self.assertRaises(Exception):
            CureTestGenerator(1,10,0,1,0.1)
        with self.assertRaises(Exception):
            CureTestGenerator(1,10,10,0,0.1)
        with self.assertRaises(Exception):
            CureTestGenerator(1,10,10,1,0)

    def test_next_must_yield_correct_layer_at_correct_speed(self):
        start_speed = 50
        stop_speed = 100
        genererator = CureTestGenerator(0,1,start_speed,stop_speed,1)
        expected_layer1 = Layer(0.0, commands = [
            LateralDraw([0,0],[1,0],start_speed),
            LateralDraw([1,0],[1,1],start_speed),
            LateralMove([1,1],[0,0], start_speed), 
            ])
        expected_layer2 = Layer(1.0, commands = [
            LateralDraw([0,0],[1,0],stop_speed),
            LateralDraw([1,0],[1,1],stop_speed),
            LateralMove([1,1], [0,0], stop_speed), 
            ])

        self.assertLayerEquals(expected_layer1, genererator.next())
        self.assertLayerEquals(expected_layer2, genererator.next())

    def test_next_should_print_base_if_specified(self):
        start_speed = 50
        stop_speed = 100
        genererator = CureTestGenerator(1,2,start_speed,stop_speed,1)
        expected_base = Layer(0.0, commands = [
            LateralDraw([0,0],[1,0],75),
            LateralDraw([1,0],[1,1],75),
            LateralMove([1,1],[0,0],75), 
            ])
        expected_layer1 = Layer(1.0, commands = [
            LateralDraw([0,0],[1,0],start_speed),
            LateralDraw([1,0],[1,1],start_speed),
            LateralMove([1,1], [0,0], start_speed), 
            ])

        self.assertLayerEquals(expected_base, genererator.next())
        self.assertLayerEquals(expected_layer1, genererator.next())

    def test_should_have_the_right_number_of_layers(self):
        start_speed = 50
        stop_speed = 100
        genererator = CureTestGenerator(3,6,start_speed,stop_speed,1)

        for i in range(0,7):
            genererator.next()

        with self.assertRaises(StopIteration):
            genererator.next()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='ERROR')
    unittest.main()