import logging
from domain.layer_generator import LayerGenerator
from domain.commands import LateralDraw, Layer
from math import pi, sin, cos


class HalfVaseTestGenerator(LayerGenerator):
    name = "Half Vase With A Twist"

    def __init__(self, height, radius, layer_height, speed=100):
        self._height = float(height)
        self._radius = float(radius)
        self._layer_height = float(layer_height)
        self._speed = speed
        self._current_height = 0.0
        self._steps_in_half = 100
        self._rad_per_step = pi / float(self._steps_in_half)
        self._layers = self._height / self._layer_height
        logging.info("Half vase height: %s" % self._height)
        logging.info("Half vase radius: %s" % self._radius)
        logging.info("Half vase layer height: %s" % self._layer_height)
        logging.info("Half vase speed: %s" % self._speed)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def _points(self, radius, start_angle):
        points = [[0, 0]]
        for step in range(0, self._steps_in_half):
            angle = start_angle + (step * self._rad_per_step)
            x = sin(angle) * radius
            y = cos(angle) * radius
            points.append([x, y])
        points.append([0, 0])
        return points

    def _start_angle(self):
        percent_complete = self._current_height / self._height
        angle = pi * percent_complete
        return angle

    def _radius(self):
        percent_complete = self._current_height / self._height
        factor = (sin(percent_complete * 2.0 * pi * 2.0) + 1) / 2.0
        out = (self._radius * 0.75) + (factor * (self._radius * 0.25))
        return out

    def next(self):
        logging.info("Half vase height: %s" % self._height)
        logging.info("Half vase current height: %s" % self._current_height)
        if self._current_height >= self._height:
            raise StopIteration
        points = self._points(self._radius(), self._start_angle())
        commands = [LateralDraw(points[index - 1], points[index], self._speed) for index in range(1, len(points))]
        layer = Layer(self._current_height, commands=commands)
        self._current_height = self._current_height + self._layer_height
        return layer
