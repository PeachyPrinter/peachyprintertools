
from domain.commands import *
from domain.layer_generator import LayerGenerator

class StubLayerGenerator(LayerGenerator):
    def __init__(self, layers):
        self._layers = layers

    def next(self):
        if len(self._layers) == 0:
            raise StopIteration()
        return self._layers.pop(0)

class SinglePointGenerator(LayerGenerator):
    def __init__(self, starting_xy = [0.0,0.0]):
        self.xy = starting_xy
        self.speed = 1

    def set(self,xy):
        self.xy = xy

    def next(self):
        layer = Layer(0.0)
        layer.commands.append(LateralDraw(self.xy,self.xy,self.speed))
        return layer