import logging
from domain.layer_generator import LayerGenerator
from domain.commands import LateralDraw, Layer
from math import pi, sin, cos, sqrt


class HalfVaseTestGenerator(LayerGenerator):
    name = "Half Vase With A Twist"

    def __init__(self, height, width, layer_height, speed=100):
        self._height = float(height)
        self._max_radius = float(width) / 2.0
        self._layer_height = float(layer_height)
        self._speed = speed
        self._current_height = 0.0
        self._steps_in_half = 100
        self._rad_per_step = pi / float(self._steps_in_half)
        self._layers = self._height / self._layer_height
        logging.info("Half vase height: %s" % self._height)
        logging.info("Half vase radius: %s" % self._max_radius)
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
        out = (self._max_radius * 0.75) + (factor * (self._max_radius * 0.25))
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


class SimpleVaseTestGenerator(LayerGenerator):
    name = "Simple 5 Sided 180 Twist Vase (BETA)"

    def __init__(self, height, width, layer_height, speed=100):
        self._height = float(height)
        self._max_radius = float(width) / 2.0
        self._layer_height = float(layer_height)
        self._speed = speed
        self._current_height = 0.0
        self._steps = 5
        self._rad_per_step = 2 * pi / float(self._steps)
        self._layers = self._height / self._layer_height
        self._angle_varience = pi / self._layers
        self._last_point = [0, self._max_radius]
        self._last_angle = 0

        logging.info("Vase height: %s" % self._height)
        logging.info("Vase radius: %s" % self._max_radius)
        logging.info("Vase layer height: %s" % self._layer_height)
        logging.info("Vase speed: %s" % self._speed)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def _points(self, start_angle):
        points = []
        for step in range(0, self._steps + 1):
            angle = start_angle + (step * self._rad_per_step)
            x = sin(angle) * self._max_radius
            y = cos(angle) * self._max_radius
            points.append([x, y])
        return points

    def next(self):
        if self._current_height >= self._height:
            raise StopIteration
        points = self._points(self._last_angle)
        commands = [LateralDraw(points[index - 1], points[index], self._speed) for index in range(1, len(points))]
        layer = Layer(self._current_height, commands=commands)
        self._current_height = self._current_height + self._layer_height
        self._last_angle = self._last_angle + self._angle_varience
        return layer


class LollipopTestGenerator(LayerGenerator):
    name = "Lollipop (BETA)"

    def __init__(self, height, width, layer_height, speed=100):
        self._height = height
        self._current_height = 0
        self._layer_height = layer_height
        self._speed = speed
        self._base_height = float(height) / 3.0
        self._stick_radius = float(width) / 10.0
        remaining_height = height - self._base_height
        self._pop_radius = min(remaining_height / 2.0, float(width) / 2.0)
        self._pop_center_height = ((height - self._base_height) / 2.0) + self._base_height
        self._stick_complexity = 20
        self._pop_complexity = 100

        logging.info("Pop height: %s" % self._height)
        logging.info("Stick radius: %s" % width / 10.0)
        logging.info("Pop radius: %s" % width / 2.0)
        logging.info("Pop layer height: %s" % self._layer_height)
        logging.info("Pop speed: %s" % self._speed)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def _get_stick(self):
        points = []
        rad_per_step = (2 * pi) / self._stick_complexity
        for step in range(0, self._stick_complexity):
            angle = step * rad_per_step
            x = sin(angle) * self._stick_radius
            y = cos(angle) * self._stick_radius
            points.append([x, y])
        #fill
        points.append([self._stick_radius, 0])
        points.append([-self._stick_radius, 0])
        points.append([0, self._stick_radius])
        points.append([0, -self._stick_radius])
        points.append([self._stick_radius, 0])
        return points

    def _layer_from_points(self, points):
        commands = [LateralDraw(points[index - 1], points[index], self._speed) for index in range(1, len(points))]
        return Layer(self._current_height, commands=commands)

    def _get_pop(self, current_height):
        rad_per_step = (2 * pi) / self._pop_complexity
        distance_to_centre = abs(self._pop_center_height - current_height)
        radius = sqrt((self._pop_radius * self._pop_radius) - (distance_to_centre * distance_to_centre))
        points = []
        for step in range(0, self._pop_complexity):
            angle = step * rad_per_step
            x = sin(angle) * radius
            y = cos(angle) * radius
            points.append([x, y])
        return points

    def next(self):
        if self._current_height >= self._height:
            raise StopIteration
        if self._current_height <= self._base_height:
            layer = self._layer_from_points(self._get_stick())
        else:
            layer = self._layer_from_points(self._get_pop(self._current_height))
        self._current_height += self._layer_height
        return layer
