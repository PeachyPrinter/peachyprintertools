import logging
import numpy
import math
from threading import Lock


class PathToAudio(object):
    def __init__(self, samples_per_second, transformer, laser_size):
        self.samples_per_second = samples_per_second
        self._transformer = transformer
        self.laser_size = laser_size
        logging.info("Audio Converter Starting up with samples: %s, laser_size: %s" % (self.samples_per_second, self.laser_size))
        self._lock = Lock()

    def _distance(self, a, b):
        a2 = math.pow((a[0] - b[0]), 2)
        b2 = math.pow((a[1] - b[1]), 2)
        return math.sqrt(a2 + b2)

    def _get_points(self, start, end, points):
        start = self._transformer.transform(start)
        end = self._transformer.transform(end)
        x_points = numpy.linspace(start[0], end[0], num=points)
        y_points = numpy.linspace(start[1], end[1], num=points)
        return numpy.column_stack((x_points, y_points))

    def process(self, start, end, speed):
        with self._lock:
            distance = self._distance(start, end)
            if distance == 0:
                distance = self.laser_size
            seconds = distance / speed
            samples = self.samples_per_second * seconds

            return self._get_points(start, end, samples)

    def set_transformer(self, transformer):
        with self._lock:
            self._transformer = transformer
