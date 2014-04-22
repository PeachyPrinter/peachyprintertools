import numpy as np

from domain.transformer import Transformer

class OneToOneTransformer(Transformer):
    def transform(self, xyz):
        x,y,z = xyz
        return [x,y,z]

'Takes Values from -1.0 to 1.0 on both axis and returns a scaled version'
class TuningTransformer(Transformer):
    def __init__(self,scale = 1.0):
        if scale > 0.0 and scale <= 1.0:
            self._scale = scale
        else:
            raise Exception("Scale must be between 0.0 and 1.0")

    def transform(self, xyz):
        x,y,z = xyz
        if abs(x) > 1.0 or abs(y) > 1.0:
            raise Exception("Points out of bounds")
        x = self._transform(x)
        y = self._transform(y)
        return [x,y]

    def _transform(self, axis):
        return ((axis * self._scale) + 1.0) / 2.0

class HomogenousTransformer(Transformer):
    def __init__(self, parameters, scale = 1.0):
        self._scale = scale
        self._parameters = parameters

    def transform(self, xyz):
        x,y,z = xyz
        x = self._transform(x)
        y = self._transform(y)
        return [x,y]

    def _transform(self, axis):
        return ((axis * self._scale) + 1.0) / 2.0