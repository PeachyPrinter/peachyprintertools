from domain.layer_generator import LayerGenerator

class StubLayerGenerator(LayerGenerator):
    def __init__(self, layers):
        self._layers = layers

    def next(self):
        if len(self._layers) == 0:
            raise StopIteration()
        return self._layers.pop(0)