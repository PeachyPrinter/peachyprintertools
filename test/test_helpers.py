import numpy
import unittest

class TestHelpers(object):
    def assertNumpyArrayEquals(self,array1, array2):
        equal = numpy.array_equal(array1,array2)
        if not equal:
            self.fail("\n%s \ndid not equal \n%s" % (str(array1),str(array2)))