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

class BlinkGeneratorTests(unittest.TestCase,test_helpers.TestHelpers):
    def test_alernates_between_points(self):
        layer_generator = BlinkGenerator([0.0,0.0])
        expected_draw = True
        for command in layer_generator.next().commands:
            if expected_draw:
                self.assertEquals(type(command), LateralDraw)
            else:
                self.assertEquals(type(command), LateralMove)
            expected_draw = not expected_draw

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

class MemoryHourglassTests(unittest.TestCase,test_helpers.TestHelpers):
    def test_can_call_next_and_get_specified_command(self):
        layer_generator = MemoryHourglassGenerator(speed = 100.0, radius = 50.0)
        expected_commands = [
            LateralDraw([ 0.0, -15.0],[ 0.0,  0.0],100.0),
            LateralDraw([ 0.0,  0.0],[ 15.0, 0.0],100.0),
            LateralDraw([ 15.0, 0.0],[ 20.0, 5.0],100.0),
            LateralDraw([ 20.0, 5.0],[ 25.0, 0.0],100.0),
            LateralDraw([ 25.0, 0.0],[ 30.0, -5.0],100.0), 
            LateralDraw([ 30.0, -5.0],[ 35.0,  0.0],100.0), 
            LateralDraw([ 35.0,  0.0],[ 50.0,  0.0],100.0),
            LateralDraw([ 50.0,  0.0],[ 0.0,  50.0],100.0), 
            LateralDraw([ 0.0,  50.0],[ 0.0,  35.0],100.0), 
            LateralDraw([ 0.0,  35.0],[-5.0,  30.0],100.0), 
            LateralDraw([-5.0,  30.0],[ 0.0,  25.0],100.0), 
            LateralDraw([ 0.0,  25.0],[ 5.0,  20.0],100.0), 
            LateralDraw([ 5.0,  20.0],[ 0.0,  15.0],100.0), 
            LateralDraw([ 0.0,  15.0],[ 0.0,  0.0],100.0), 
            LateralDraw([ 0.0,  0.0],[-15.0,  0.0],100.0), 
            LateralDraw([-15.0,  0.0],[-20.0, -5.0],100.0), 
            LateralDraw([-20.0, -5.0],[-25.0,  0.0],100.0), 
            LateralDraw([-25.0,  0.0],[-30.0,  5.0],100.0), 
            LateralDraw([-30.0,  5.0],[-35.0,  0.0],100.0), 
            LateralDraw([-35.0,  0.0],[-50.0,  0.0],100.0), 
            LateralDraw([-50.0,  0.0],[ 0.0, -50.0],100.0),
            LateralDraw([ 0.0, -50.0],[ 0.0, -35.0],100.0), 
            LateralDraw([ 0.0, -35.0],[ 5.0, -30.0],100.0), 
            LateralDraw([ 5.0, -30.0],[ 0.0, -25.0],100.0), 
            LateralDraw([ 0.0, -25.0],[-5.0, -20.0],100.0), 
            LateralDraw([-5.0, -20.0],[ 0.0, -15.0],100.0),
            ]
        
        expected = Layer(0.0, commands = expected_commands )
        actual =   layer_generator.next() 
        self.assertLayerEquals(expected,actual)


#---------------- Augmented Generators  -------------------------------------

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

    def test_sublayer_generator_should_shuffle_commands_when_layers_same_as_sublayer_height(self):
        command1 = LateralDraw([0.0,0.0],[0.0,0.0],100.0)
        command2 = LateralDraw([0.0,0.0],[1.0,1.0],100.0)
        command3 = LateralDraw([0.0,0.0],[2.0,2.0],100.0)
        command4 = LateralDraw([0.0,0.0],[3.0,3.0],100.0)
        layer1 = Layer(0.0,[ command1, command2,command3, command4 ])
        layer2 = Layer(0.1,[ command1, command2,command3, command4 ])
        layer3 = Layer(0.2,[ command1, command2,command3, command4 ])
        layer4 = Layer(0.3,[ command1, command2,command3, command4 ])

        shuffled_layer2 = Layer(0.1,[ command2, command3, command4, command1, ])
        shuffled_layer3 = Layer(0.2,[ command3, command4, command1, command2, ])
        shuffled_layer4 = Layer(0.3,[ command4, command1, command2, command3, ])


        expected_layers = (layer1,shuffled_layer2,shuffled_layer3,shuffled_layer4)
        inital_generator = StubLayerGenerator([layer1,layer2,layer3,layer4])

        sublayer_generator = SubLayerGenerator(inital_generator,0.5)
        for expected_layer in expected_layers:
            l = sublayer_generator.next()
            self.assertLayerEquals(expected_layer,l)

        with self.assertRaises(StopIteration):
            sublayer_generator.next()

    def test_sublayer_generator_should_shuffle_commands_when_layers_have_fewer_commands(self):
        command1 = LateralDraw([0.0,0.0],[0.0,0.0],100.0)
        command2 = LateralDraw([0.0,0.0],[1.0,1.0],100.0)
        command3 = LateralDraw([0.0,0.0],[2.0,2.0],100.0)
        command4 = LateralDraw([0.0,0.0],[3.0,3.0],100.0)
        layer1 = Layer(0.0,[ command1, command2,command3, command4 ])
        layer2 = Layer(0.1,[ command1, command2,command3, command4 ])
        layer3 = Layer(0.2,[ command1 ])
        layer4 = Layer(0.3,[ command2 , command3])

        shuffled_layer2 = Layer(0.1,[ command2, command3, command4, command1, ])
        shuffled_layer3 = Layer(0.2,[ command1 ])
        shuffled_layer4 = Layer(0.3,[ command3, command2 ])


        expected_layers = (layer1,shuffled_layer2,shuffled_layer3,shuffled_layer4)
        inital_generator = StubLayerGenerator([layer1,layer2,layer3,layer4])

        sublayer_generator = SubLayerGenerator(inital_generator,0.5)
        for expected_layer in expected_layers:
            l = sublayer_generator.next()
            self.assertLayerEquals(expected_layer,l)

        with self.assertRaises(StopIteration):
            sublayer_generator.next()

class OverLapGeneratorTests(unittest.TestCase,test_helpers.TestHelpers):
    def test_next_should_return_input_when_single_command(self):
        expected_layer = Layer(0.0, commands = [LateralDraw([0.0,0.0],[1.0,1.0],100.0)])
        source = StubLayerGenerator([expected_layer])
        overlap_generator = OverLapGenerator(source)

        actual_layer = overlap_generator.next()

        self.assertLayerEquals(expected_layer,actual_layer)

    def test_next_should_return_input_when_command_start_and_end_not_congruent(self):
        expected_layer = Layer(0.0, commands = [
            LateralDraw([0.0,0.0],[1.0,1.0],100.0),
            LateralDraw([1.0,1.0],[2.0,2.0],100.0),
            ])
        source = StubLayerGenerator([expected_layer])
        overlap_generator = OverLapGenerator(source)

        actual_layer = overlap_generator.next()

        self.assertLayerEquals(expected_layer,actual_layer)

    def test_next_should_overlap_when_commands_congruent(self):
        source_layer = Layer(0.0, commands = [
            LateralDraw([0.0,0.0],[10.0,10.0],100.0),
            LateralDraw([10.0,10.0],[20.0,20.0],100.0),
            LateralDraw([20.0,20.0],[0.0,0.0],100.0),
            ])
        expected_layer = Layer(0.0, commands = [
            LateralDraw([0.0,0.0],[10.0,10.0],100.0),
            LateralDraw([10.0,10.0],[20.0,20.0],100.0),
            LateralDraw([20.0,20.0],[0.0,0.0],100.0),
            LateralDraw([0.0,0.0],[0.70710678118,0.70710678118], 100.0)
            ])
        source = StubLayerGenerator([source_layer])
        overlap_generator = OverLapGenerator(source)

        actual_layer = overlap_generator.next()

        self.assertLayerEquals(expected_layer,actual_layer)


    def test_next_should_handle_non_movment_commands(self):
        pass
        # not long enough
        # end begin in move


#---------------- Cure Test Generators  -------------------------------------

class CureTestGeneratorTests(unittest.TestCase,test_helpers.TestHelpers):

    def test_next_must_yield_correct_layer_at_correct_speed(self):
        start_speed = 50
        stop_speed = 100
        genererator = CureTestGenerator(0,1,start_speed,stop_speed,1)
        expected_layer1 = Layer(0.0, commands = [
            LateralDraw([0,0],[10,0],start_speed),
            LateralDraw([10,0],[10,10],start_speed),
            LateralMove([10,10],[0,0], start_speed), 
            ])
        expected_layer2 = Layer(1.0, commands = [
            LateralDraw([0,0],[10,0],stop_speed),
            LateralDraw([10,0],[10,10],stop_speed),
            LateralMove([10,10], [0,0], stop_speed), 
            ])

        self.assertLayerEquals(expected_layer1, genererator.next())
        self.assertLayerEquals(expected_layer2, genererator.next())

    def test_next_should_print_base_if_specified(self):
        start_speed = 50
        stop_speed = 100
        genererator = CureTestGenerator(1,2,start_speed,stop_speed,1)
        expected_base = Layer(0.0, commands = [
            LateralDraw([0,0],[10,0],75),
            LateralDraw([10,0],[10,10],75),
            LateralDraw([10,10],[0,0],75), 
            ])
        expected_layer1 = Layer(1.0, commands = [
            LateralDraw([0,0],[10,0],start_speed),
            LateralDraw([10,0],[10,10],start_speed),
            LateralMove([10,10], [0,0], start_speed), 
            ])

        self.assertLayerEquals(expected_base, genererator.next())
        self.assertLayerEquals(expected_layer1, genererator.next())

    def test_should_have_the_right_number_of_layers(self):
        start_speed = 50
        stop_speed = 100
        base_height = 3
        total_height = 6
        sublayers_size = 0.1
        expected_layers = int(total_height / 0.1)

        genererator = CureTestGenerator(base_height,total_height,start_speed,stop_speed,sublayers_size)

        for i in range(0,expected_layers +1):
            genererator.next()

        with self.assertRaises(StopIteration):
            genererator.next()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='ERROR')
    unittest.main()