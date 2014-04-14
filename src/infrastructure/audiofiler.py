import logging
import numpy
from scipy.spatial import distance_matrix

class PathToAudio(object):
    def __init__(self, samples_per_second, transformer, laser_size):
        self.samples_per_second = samples_per_second
        self._transformer = transformer
        self.laser_size = laser_size
        logging.info("Audio Converter Starting up with samples: %s, laser_size: %s" % (self.samples_per_second, self.laser_size))

    def _distance(self, a, b): 
        return distance_matrix([a],[b])[0][0]

    def _get_points(self, start, end, points):
        start = self._transformer.transform(start)
        end = self._transformer.transform(end)
        x_points = numpy.linspace(start[0], end[0], num=points)
        y_points = numpy.linspace(start[1], end[1], num=points)
        return numpy.column_stack((x_points, y_points))

    def process(self, start, end, speed):
        distance  = self._distance(start, end)
        if distance == 0:
            distance = self.laser_size
        seconds = distance / speed
        samples = self.samples_per_second * seconds

        return self._get_points(start,end,samples)