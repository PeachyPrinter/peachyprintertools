class LayerGenerator(object):
    def __next__(self):
        return self.next()

    def __iter__(self):
        return self

    def next(self):
        raise NotImplementedError()


class TestLayerGenerator(LayerGenerator):
    def _is_positive_float(self,value):
        try:
            number = float(value)
            if (number <= 0.0):
                return False
            else:
                return True
        except ValueError:
            return False
            
    def set_speed(self, speed):
        if (self._is_positive_float(speed)):
            self._speed = speed
        else:
            raise AttributeError("Speed must be a positive number")
        
    def set_radius(self,radius):
        if (self._is_positive_float(radius)):
            self._radius = radius
        else:
            raise AttributeError("Radius must be a positive number")