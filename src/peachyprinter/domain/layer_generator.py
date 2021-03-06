import logging
logger = logging.getLogger('peachy')


class LayerGenerator(object):

    def __next__(self):
        return self.next()

    def __iter__(self):
        return self

    def next(self):
        raise NotImplementedError()


class TestLayerGenerator(LayerGenerator):
    def _is_positive_float(self, value):
        try:
            number = float(value)
            if (number <= 0.0):
                return False
            else:
                return True
        except ValueError:
            return False

    def _is_zero_or_positive(self, value):
        try:
            number = float(value)
            if (number < 0.0):
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

    def set_radius(self, radius):
        logger.info("New %s Radius: %s" % (self.__class__.__name__, radius))
        if (self._is_positive_float(radius)):
            self._radius = radius
        else:
            raise AttributeError("Radius must be a positive number")

    def set_current_height(self, current_height):
        logger.info("New current_height: %s" % current_height)
        if (self._is_zero_or_positive(current_height)):
            self._current_height = abs(current_height)
        else:
            raise AttributeError("Height must be zero or greater")