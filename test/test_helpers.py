import numpy
import unittest
from domain.commands import *

class TestHelpers(object):
    def assertNumpyArrayEquals(self,array1, array2):
        equal = numpy.array_equal(array1,array2)
        if not equal:
            self.fail("\n%s \ndid not equal \n%s" % (str(array1),str(array2)))

    def assertCommandsEqual(self, command1, command2):
        if type(command1) != type(command2):
            self.fail("Commands do not match\n %s\ndid not equal\n%s" % (layer1.commands, layer2.commands))
        if type(command1) == LateralDraw:
            if command1.x == command2.x and command1.y == command2.y and command1.rate == command2.rate:
                pass
            else:
                self.fail("Commands do not match\n %s\ndid not equal\n%s" % (layer1.commands, layer2.commands))
        else:
            self.fail("Test Helper Unsupported type: %s" % type(command1) )

    def assertLayerEquals(self,layer1,layer2):
        if layer1.z_posisition != layer2.z_posisition:
            self.fail("Z_posisition do not match %s did not equal %s" % (layer1.z_posisition, layer2.z_posisition))
        if len(layer1.commands) != len(layer2.commands):
            self.fail("Commands do not match\n %s\ndid not equal\n%s" % (layer1.commands, layer2.commands))
        for i in range(0, len(layer1.commands)):
            try:
                self.assertCommandsEqual(layer1.commands[i],layer2.commands[i])
            except Exception as ex:
                self.fail("Commands do not match\n %s\ndid not equal\n%s\nDetail: %s" % (layer1.commands, layer2.commands, ex.message))

    def assertLayersEquals(self,layers1,layers2):
        if len(layers1) != len(layers2):
            self.fail("Count of Layers do not match\n %s\ndid not equal\n%s" % (layers1, layers2))
        for i in range(len(layers1)):
            self.assertLayerEquals(layers1[i],layers2[i])
