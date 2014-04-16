import logging

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
        self.speed = 100.0

    def set(self,xy):
        self.xy = xy

    def next(self):
        layer = Layer(0.0)
        layer.commands.append(LateralDraw(self.xy,self.xy,self.speed))
        return layer

class CalibrationLineGenerator(LayerGenerator):
    def __init__(self):
        pass

    def next(self):
        return Layer(0.0, commands = [LateralDraw([-1.0,0.0],[1.0,0.0],1),LateralDraw([1.0,0.0],[-1.0,0.0],1)])

class SubLayerGenerator(LayerGenerator):
    def __init__(self,layer_generator,sub_layer_height, tollerance = 0.001):
        self._layer_generator = layer_generator
        self._tollerance = tollerance
        self._sub_layer_height = sub_layer_height
        self._running = True
        self._load_layer()
        self._current_layer = None

    def next(self):
        if self._running:
            if self._current_layer:
                distance_to_next_layer = self._next.z - self._current_layer.z
                logging.debug('%f8' % distance_to_next_layer)
                if  distance_to_next_layer / 2.0 >= self._sub_layer_height - self._tollerance:
                    current_z = self._current_layer.z
                    self._current_layer.z = current_z + self._sub_layer_height
                    self._current_layer = self._shuffle(self._current_layer)
                else:
                    self._current_layer = self._next
                    self._load_layer()
            else:
                self._current_layer = self._next
                self._load_layer()
            return self._current_layer
        else:
            raise StopIteration

    def _shuffle(self, layer):
        commands = layer.commands[1:] + layer.commands[:1]
        layer.commands = commands
        return layer
       

    def _load_layer(self):
        try:
            self._next = self._layer_generator.next()
        except StopIteration:
            self._running = False
