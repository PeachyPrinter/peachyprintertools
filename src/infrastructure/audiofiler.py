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
        self._left_over_samples = 0.0
        self._left_over_start = None
        self._last_z = 0.0
        self._reported_small_warning = False

    def _distance(self, a, b):
        a2 = math.pow((a[0] - b[0]), 2)
        b2 = math.pow((a[1] - b[1]), 2)
        return math.sqrt(a2 + b2)

    def _get_points(self, start, end, points):
        start = self._transformer.transform(start)
        end = self._transformer.transform(end)
        x_points = numpy.linspace(start[0], end[0], num=points, endpoint=True)
        y_points = numpy.linspace(start[1], end[1], num=points, endpoint=True)
        return numpy.column_stack((x_points, y_points))

    def process(self, start, end, speed):
        with self._lock:
            if start[2] > self._last_z:
                self._left_over_samples = 0.0
                self._left_over_start = None
                self._last_z = start[2]
                self._reported_small_warning = False
            distance = self._distance(start, end)
            if distance == 0:
                distance = self.laser_size
            seconds = distance / speed
            samples = (self.samples_per_second * seconds) + self._left_over_samples
            if samples < 2.0:
                if not self._reported_small_warning:
                    logging.warning("The data in the model is too complex skipping vertex(s) at height %s mm" % start[2])
                    self._reported_small_warning = True
                if not self._left_over_start:
                    self._left_over_start = start
                self._left_over_samples = samples
                return numpy.column_stack(([], []))
            else:
                self._left_over_samples = 0.0
                if self._left_over_start:
                    points = self._get_points(self._left_over_start, end, samples)
                    self._left_over_start = None
                    return points
                else:
                    return self._get_points(start, end, samples)

    def set_transformer(self, transformer):
        with self._lock:
            self._transformer = transformer
