import logging
logger = logging.getLogger('peachy')

from peachyprinter.domain.commands import *
from peachyprinter.domain.layer_generator import LayerGenerator, TestLayerGenerator
import math
from math import pi, sin, cos, asin
from threading import Lock

# -----------Testing Generators ----------------


class StubLayerGenerator(LayerGenerator):
    def __init__(self, layers=Layer(0.0), repeat=False):
        self._original = layers
        self._layers = list(self._original)
        self._repeat = repeat

    def next(self):
        if len(self._layers) == 0:
            if self._repeat:
                self._layers = list(self._original)
            else:
                raise StopIteration()
        return self._layers.pop(0)

# -----------Pattern  Generators ----------------


class SinglePointGenerator(LayerGenerator):
    def __init__(self, starting_xy=[0.0, 0.0]):
        self.xy = starting_xy
        self.speed = 100.0
        self.lock = Lock()

    def set(self, xy):
        logging.warning("set")
        with self.lock:
            self.xy = xy

    def next(self):
        layer = Layer(0.0)
        with self.lock:
            layer.commands.append(LateralDraw(self.xy, self.xy, self.speed))
        return layer


class CalibrationLineGenerator(LayerGenerator):
    def __init__(self, speed=30.0):
        self._speed = speed

    def next(self):
        return Layer(0.0, commands=[LateralDraw([0.0, 0.5], [1.0, 0.5], self._speed), LateralDraw([1.0, 0.5], [0.0, 0.5], self._speed)])


class OrientationGenerator(LayerGenerator):
    def __init__(self, speed=1.0):
        self._speed = speed
        self._commands = [
                        LateralDraw([0.40, 0.20], [0.40, 0.60], self._speed),
                        LateralDraw([0.40, 0.60], [0.50, 0.58], self._speed),
                        LateralDraw([0.50, 0.58], [0.55, 0.54], self._speed),
                        LateralDraw([0.55, 0.54], [0.60, 0.50], self._speed),
                        LateralDraw([0.60, 0.50], [0.55, 0.46], self._speed),
                        LateralDraw([0.55, 0.46], [0.50, 0.42], self._speed),
                        LateralDraw([0.50, 0.42], [0.40, 0.40], self._speed),
                        LateralMove([0.40, 0.40], [0.40, 0.20], self._speed),
                    ]

    def next(self):
        return Layer(0.0, commands=self._commands)


class BlinkGenerator(TestLayerGenerator):
    def __init__(self, starting_xy=[0.0, 0.0], radius=0.5, speed=0.5, steps=50):
        self._current_height = 0.0
        self.xy = starting_xy
        self._state = True
        self.set_speed(speed)
        self.set_radius(radius)
        self._steps = steps
        self.last_xy = [0.0, 0.0]
        self._points = list(self.points())

    def next(self):
        layer = Layer(self._current_height)
        for point in self._points:
            if self._state:
                layer.commands.append(LateralDraw(self.last_xy, point, self._speed))
            else:
                layer.commands.append(LateralMove(self.last_xy, point, self._speed))
            self._state = not self._state
            self.last_xy = point
        return layer

    def points(self):
        angle_step = (2 * math.pi / self._steps)
        for i in range(0, self._steps):
            theta = angle_step * i
            x = math.sin(theta) * self._radius + 0.5
            y = math.cos(theta) * self._radius + 0.5
            yield [x, y]


class HilbertGenerator(TestLayerGenerator):
    def __init__(self, order=4, speed=150.0, radius=40.0):
        self._current_height = 0.0
        self._order = order
        self._last_xy = [0.0, 0.0]
        self.set_speed(speed)
        self.set_radius(radius)

    def next(self):
        self._pattern = self._get_hilbert(self._order, [-self._radius, -self._radius], [self._radius, self._radius])
        # logger.debug('Pattern: %s' % self._pattern)
        layer = Layer(self._current_height)
        layer.commands.append(LateralMove(self._last_xy, self._pattern[0], self._speed))
        self._last_xy = self._pattern[0]
        for x, y in self._pattern[1:]:
            next_xy = [x, y]
            layer.commands.append(LateralDraw(self._last_xy, next_xy, self._speed))
            self._last_xy = next_xy
        return layer

    def _get_hilbert(self, order, lower_bounds, upper_bounds):
        [x0, y0] = lower_bounds
        [x1, y1] = upper_bounds
        [xi, yj] = [abs(x1-x0), abs(y1-y0)]
        self._points = []
        self._hilbert(x0, y0, xi, 0.0, 0.0, yj, order)
        return self._points

    def _hilbert(self, x0, y0, xi, xj, yi, yj, n, points=[]):
        if n <= 0:
            X = x0 + (xi + yi)/2
            Y = y0 + (xj + yj)/2
            self._points.append([X, Y])
        else:
            self._hilbert(x0, y0, yi/2, yj/2, xi/2, xj/2, n - 1)
            self._hilbert(x0 + xi/2, y0 + xj/2, xi/2, xj/2, yi/2, yj/2, n - 1)
            self._hilbert(x0 + xi/2 + yi/2, y0 + xj/2 + yj/2, xi/2, xj/2, yi/2, yj/2, n - 1)
            self._hilbert(x0 + xi/2 + yi,  y0 + xj/2 + yj, -yi/2, -yj/2, -xi/2, -xj/2, n - 1)


class SquareGenerator(TestLayerGenerator):
    def __init__(self, speed=100.0, radius=20.0):
        self._current_height = 0.0
        self.set_speed(speed)
        self.set_radius(radius)

    def next(self):
        layer = Layer(self._current_height)
        layer.commands.append(LateralDraw([-self._radius, self._radius], [self._radius, self._radius], self._speed))
        layer.commands.append(LateralDraw([self._radius, self._radius], [self._radius, -self._radius], self._speed))
        layer.commands.append(LateralDraw([self._radius, -self._radius], [-self._radius, -self._radius], self._speed))
        layer.commands.append(LateralDraw([-self._radius, -self._radius], [-self._radius, self._radius], self._speed))
        return layer


class DampingTestGenerator(TestLayerGenerator):
    def __init__(self, speed=100.0, radius=20.0):
        self._current_height = 0.0
        self.set_speed(speed)
        self.set_radius(radius)

    def next(self):
        layer = Layer(self._current_height)
        layer.commands.append(LateralMove([0.0, self._radius], [-self._radius, self._radius], self._speed))
        layer.commands.append(LateralMove([-self._radius, self._radius], [-self._radius, 0.0], self._speed * 100))
        layer.commands.append(LateralDraw([-self._radius, 0.0], [self._radius, 0.0], self._speed))
        layer.commands.append(LateralMove([self._radius, 0.0], [self._radius, -self._radius], self._speed))
        layer.commands.append(LateralMove([self._radius, -self._radius], [0.0, -self._radius], self._speed * 100))
        layer.commands.append(LateralDraw([0.0, -self._radius], [0.0, self._radius], self._speed))
        return layer


class CircleGenerator(TestLayerGenerator):
    def __init__(self, speed=100.0, radius=20.0, steps=180):
        self._current_height = 0.0
        self.set_speed(speed)
        self.set_radius(radius)
        self._steps = steps
        self.last_xy = [0.0, 0.0]
        self._last_radius = None
        self.active_points = list(self.points())

    def next(self):
        if self._last_radius != self._radius:
            self._last_radius == self._radius
            self.active_points = list(self.points())
        layer = Layer(self._current_height)
        for point in self.active_points:
            layer.commands.append(LateralDraw(self.last_xy, point, self._speed))
            self.last_xy = point
        return layer

    def points(self):
        angle_step = (2 * math.pi / self._steps)
        for i in range(0, self._steps):
            theta = angle_step * i
            x = math.sin(theta) * self._radius
            y = math.cos(theta) * self._radius
            yield [x, y]


class SpiralGenerator(TestLayerGenerator):
    def __init__(self, speed=100.0, radius=20.0, steps=50, overlaps=6):
        self._current_height = 0.0
        self.set_speed(speed)
        self.set_radius(radius)
        self._steps = steps
        self._overlaps = 10
        self.last_xy = [0.0, 0.0]

    def next(self):
        layer = Layer(self._current_height)
        layer.commands.append(LateralMove(self.last_xy, [0.0, 0.0], self._speed))
        self.last_xy = [0.0, 0.0]
        for point in self.points():
            layer.commands.append(LateralDraw(self.last_xy, point, self._speed))
            self.last_xy = point
        return layer

    def points(self):
        inc = self._radius / (self._steps * self._overlaps)
        angle_step = (2 * math.pi / self._steps)
        radius = 0.0
        for i in range(0, self._steps * self._overlaps):
            theta = angle_step * i
            x = math.sin(theta) * radius
            y = math.cos(theta) * radius
            radius += inc
            yield [x, y]


class MemoryHourglassGenerator(TestLayerGenerator):
    def __init__(self, speed=100.0, radius=20.0):
        self._current_height = 0.0
        self.set_speed(speed)
        self.set_radius(radius)
        self.path = [
                 [0.0, 0.0], [0.3, 0.0], [0.4, 0.1], [0.5, 0.0], [0.6, -0.1], [0.7, 0.0], [1.0, 0.0],
                 [0.0, 1.0], [0.0, 0.7], [-0.1, 0.6], [0.0, 0.5], [0.1, 0.4], [0.0, 0.3], [0.0, 0.0],
                 [-0.3, 0.0], [-0.4, -0.1], [-0.5, 0.0], [-0.6, 0.1], [-0.7, 0.0], [-1.0, 0.0], [0.0, -1.0],
                 [0.0, -0.7], [0.1, -0.6], [0.0, -0.5], [-0.1, -0.4], [0.0, -0.3]
                ]

    def next(self):
        layer = Layer(self._current_height)
        last = [a * self._radius for a in self.path[-1:][0]]
        for point in self.path:
            scaled_point = [a * self._radius for a in point]
            layer.commands.append(LateralDraw(last, scaled_point, self._speed))
            last = scaled_point
        return layer


class TwitchGenerator(TestLayerGenerator):
    def __init__(self, speed=100.0, radius=20.0):
        self._current_height = 0.0
        self.set_speed(speed)
        self.set_radius(radius)
        self.path = [([-0.500, -1.000], 1), ([-0.500, 1.000], 1)]
        for r in range(1, 100):
            xd = 0.5 * (((r % 2) * 2) - 1)
            yd = 1.0 - float(r) * 2.0 / 100.0
            self.path.append(([xd, yd], float(r) / 4))

    def next(self):
        layer = Layer(self._current_height)
        last = [a * self._radius for a in self.path[-1:][0][0]]
        for (point, s) in self.path:
            scaled_point = [a * self._radius for a in point]
            layer.commands.append(LateralDraw(last, scaled_point, self._speed * s))
            last = scaled_point
        return layer


class NESWGenerator(TestLayerGenerator):
    def __init__(self, speed=100.0, radius=20.0):
        self._current_height = 0.0
        self.set_speed(speed)
        self.set_radius(radius)
        self.path = [
                 ('m', [-0.1, 0.8]), ('d', [-0.1, 1.0]), ('d', [0.1, 0.8]), ('d', [0.1, 1.0]),
                 ('m', [1.0, 0.1]), ('d', [0.8, 0.1]), ('d', [0.8, 0.0]), ('d', [0.9, 0.0]), ('d', [0.8, 0.0]), ('d', [0.8, -0.1]), ('d', [1.0, -0.1]),
                 ('m', [0.1, -0.8]), ('d', [-0.1, -0.8]), ('d', [-0.1, -0.9]), ('d', [0.1, -0.9]), ('d', [0.1, -1.0]), ('d', [-0.1, -1.0]),
                 ('m', [-0.8, 0.1]), ('d', [-0.8, -0.1]), ('d', [-0.9, 0.0]), ('d', [-1.0, -0.1]), ('d', [-1.0, 0.1])
               ]

    def next(self):
        layer = Layer(self._current_height)
        last = [a * self._radius for a in self.path[1][-1:][0]]
        for (k, point) in self.path:
            scaled_point = [a * self._radius for a in point]
            if k == 'd':
                layer.commands.append(LateralDraw(last, scaled_point, self._speed))
            else:
                layer.commands.append(LateralMove(last, scaled_point, self._speed))
            last = scaled_point
        return layer

# -----------Cure Generators ----------------


class CureTestGenerator(LayerGenerator):
    def __init__(self, base_height, total_height, start_speed, stop_speed, sublayer_height, base_speed=None):
        base_height = float(base_height)
        total_height = float(total_height)
        self.start_speed = float(start_speed)
        stop_speed = float(stop_speed)
        self._sub_layer_height = float(sublayer_height)
        logger.info("Base Height: %s" % base_height)
        logger.info("Total Height: %s" % total_height)
        logger.info("Start Speed: %s" % self.start_speed)
        logger.info("Stop Speed: %s" % stop_speed)
        logger.info("Sublayer Height: %s" % self._sub_layer_height)

        self._base_layers = base_height / self._sub_layer_height
        self._number_of_layers = total_height / self._sub_layer_height
        logger.info("Total layer to print: %s" % self._number_of_layers)
        if base_speed:
            self._base_layer_speed = base_speed
        else:
            self._base_layer_speed = self.start_speed + ((stop_speed - self.start_speed) / 2.0)
        self._speed_per_layer = (stop_speed - self.start_speed) / (self._number_of_layers - self._base_layers)
        self._current_layer = 0

    def commands(self, base):
        if base:
            return [
                LateralDraw([0, 0], [10, 0], self._base_layer_speed),
                LateralDraw([10, 0], [10, 10], self._base_layer_speed),
                LateralDraw([10, 10], [0, 0], self._base_layer_speed),
                ]
        else:
            current_speed = (self._speed_per_layer * (self._current_layer - self._base_layers)) + self.start_speed
            logger.info("Speed : %s" % current_speed)
            return [
                LateralDraw([0, 0], [10, 0], current_speed),
                LateralDraw([10, 0], [10, 10], current_speed),
                LateralMove([10, 10], [0, 0], current_speed),
                ]

    def next(self):
        if self._current_layer > self._number_of_layers:
            raise StopIteration
        base_layer = self._current_layer < self._base_layers

        layer = Layer(float(self._current_layer * self._sub_layer_height), commands=self.commands(base_layer))
        self._current_layer += 1
        return layer


class AdvancedCureTestGenerator(LayerGenerator):
    def __init__(
        self,
        base_height,
        total_height,
        start_speed,
        stop_speed,
        sublayer_height,
        radius=30.0,
        curves=10,
        curve_change=0.2,
        curve_spacing=0.05,
        polys_per=20
            ):
            base_height = float(base_height)
            total_height = float(total_height)
            self.start_speed = float(start_speed)
            stop_speed = float(stop_speed)
            self._sub_layer_height = float(sublayer_height)
            logger.info("Base Height: %s" % base_height)
            logger.info("Total Height: %s" % total_height)
            logger.info("Start Speed: %s" % self.start_speed)
            logger.info("Stop Speed: %s" % stop_speed)
            logger.info("Sublayer Height: %s" % self._sub_layer_height)

            self._base_layers = base_height / self._sub_layer_height
            self._number_of_layers = total_height / self._sub_layer_height
            logger.info("Base layers to print: %s" % self._base_layers)
            logger.info("Total layer to print: %s" % self._number_of_layers)
            self._base_layer_speed = self.start_speed + ((stop_speed - self.start_speed) / 2.0)
            self._speed_per_layer = (stop_speed - self.start_speed) / (self._number_of_layers - self._base_layers)
            self._current_layer = 0

            self._radius = radius
            self.curves = curves
            self.curve_change = curve_change
            self.curve_spacing = curve_spacing
            self.polys_per = polys_per
            self.current_curve = 0
            self.direction = True
            self.curve_points = self.get_curves(curves)
            self.last_xy = [0.0, 0.0]

    def point(self, x, vertex_x, vertex_y,curve):
        y = curve * math.pow((x + vertex_x), 2) + vertex_y
        if y > 1.0:
            y = 1.0
        return [x, y]

    def points(self, vertex_x, vertex_y, curve):
        change_amount = 1.0 / (self.polys_per * 1.0)
        points = []
        if self.direction:
            start = -self.polys_per
            end = self.polys_per + 1
            inc = 1
        else:
            start = self.polys_per
            end = -self.polys_per - 1
            inc = -1
        for i in range(start, end, inc):
            points.append(self.point(change_amount * i, vertex_x, vertex_y, curve))
        self.direction = not self.direction
        return points

    def get_curves(self, number_of_curves):
        grouped_curves = []
        for i in range(0, number_of_curves):
            vertex_y = -1.0 + (self.curve_spacing * i)
            vertex_x = 0
            curvature = i * self.curve_change
            grouped_curves.append(self.points(vertex_x, vertex_y, curvature))
        return grouped_curves

    def add_path(self, layer, speed):
        next_xy = (-1.0 * self._radius, -1.0 * self._radius, )
        layer.commands.append(LateralMove([0.0, 0.0], next_xy, speed))
        self.last_xy = next_xy
        for curve in self.curve_points:
            for point in curve:
                next_xy = (point[0] * self._radius, point[1] * self._radius, )
                layer.commands.append(LateralDraw(self.last_xy, next_xy, speed))
                self.last_xy = next_xy
        return layer

    def next(self):
        if self._current_layer > self._number_of_layers:
            raise StopIteration
        height = float(self._current_layer * self._sub_layer_height)
        if (self._current_layer < self._base_layers):
            layer = self.add_path(Layer(height), self._base_layer_speed)
        else:
            current_speed = (self._speed_per_layer * (self._current_layer - self._base_layers)) + self.start_speed
            layer = self.add_path(Layer(height), current_speed)
        self._current_layer += 1
        return layer

# -----------Augmenting Generators ----------------


class SubLayerGenerator(LayerGenerator):
    def __init__(self, layer_generator, sub_layer_height, tollerance=0.001):
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
                # logger.debug('%f8' % distance_to_next_layer)
                if distance_to_next_layer / 2.0 >= self._sub_layer_height - self._tollerance:
                    current_z = self._current_layer.z
                    self._current_layer.z = current_z + self._sub_layer_height
                    self._current_layer = self._current_layer
                else:
                    self._current_layer = self._next
                    self._load_layer()
            else:
                self._current_layer = self._next
                self._load_layer()
            return self._current_layer
        else:
            raise StopIteration

    def _load_layer(self):
        try:
            self._next = self._layer_generator.next()
        except StopIteration:
            self._running = False


class ShuffleGenerator(LayerGenerator):
    def __init__(self, layer_generator, amount):
        self._layer_generator = layer_generator
        self._amount = amount
        self._shuffle_point = 0

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        return self._shuffle(self._layer_generator.next())

    def _shuffle(self, layer):
        shuffle_amount = int(self._shuffle_point) % len(layer.commands)
        layer.commands = layer.commands[shuffle_amount:] + layer.commands[:shuffle_amount]
        self._shuffle_point += self._amount
        return layer

    def _load_layer(self):
        try:
            self._next = self._layer_generator.next()
        except StopIteration:
            self._running = False


class OverLapGenerator(LayerGenerator):
    def __init__(self, layer_generator, overlap_mm=1.0):
        self._layer_generator = layer_generator
        self._tollerance = 0.01
        self.overlap_mm = overlap_mm

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def _same_spot(self, pos1, pos2):
        return (abs(pos1[0] - pos2[0]) < self._tollerance) and (abs(pos1[0] - pos2[0]) < self._tollerance)

    def _overlap_command(self, command, amount):
        x = command.end[0] - command.start[0]
        y = command.end[1] - command.start[1]
        magnatude = math.sqrt(x**2 + y**2)
        if magnatude == 0.0:
            return ([], amount)
        elif magnatude >= amount:
            vector = [(x / magnatude) * amount, (y / magnatude) * amount]
            end_pos = [command.start[0] + vector[0], command.start[1] + vector[1]]
            return ([LateralDraw(command.start, end_pos, command.speed)], 0.0)
        else:
            return ([LateralDraw(command.start, command.end, command.speed)], amount - magnatude)

    def _overlap_layer(self, layer, threshold=0.001):
        new_commands = []
        index = 0
        remainder = self.overlap_mm
        while remainder > threshold:  # almost
            if len(layer.commands) < index:
                break
            if type(layer.commands[index]) == LateralMove:
                break
            new_command, remainder = self._overlap_command(layer.commands[index], remainder)
            new_commands = new_commands + new_command
            index += 1
        commands = layer.commands + new_commands
        return Layer(layer.z, commands=commands)

    def _should_overlap(self, layer):
        first_command = layer.commands[0]
        last_command = layer.commands[-1]
        return (
            self._same_spot(last_command.end, first_command.start) and
            type(first_command) == LateralDraw and
            type(last_command) == LateralDraw
            )

    def next(self):
        next_layer = self._layer_generator.next()
        if self._should_overlap(next_layer):
            return self._overlap_layer(next_layer)
        else:
            return next_layer
