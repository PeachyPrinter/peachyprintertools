import logging

from domain.commands import *
from domain.layer_generator import LayerGenerator, TestLayerGenerator

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
    def __init__(self, speed = 10.0):
        self._speed = speed

    def next(self):
        return Layer(0.0, commands = [LateralDraw([0.0,0.5],[1.0,0.5],self._speed),LateralDraw([1.0,0.5],[0.0,0.5],self._speed)])

class BlinkGenerator(TestLayerGenerator):
    def __init__(self, starting_xy = [0.0,0.0]):
        self.xy = starting_xy
        self.speed = 100.0
        self._state = True

    def set(self,xy):
        self.xy = xy

    def next(self):
        layer = Layer(0.0)
        if self._state:
            layer.commands.append(LateralDraw(self.xy,self.xy,self.speed))
        else:
            layer.commands.append(LateralMove(self.xy,self.xy,self.speed))
        self._state = not self._state
        return layer

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

class HilbertGenerator(TestLayerGenerator):
    def __init__(self, order = 4, speed = 150.0, radius = 40.0):
        self._order = order
        self._last_xy = [0.0,0.0]
        self.set_speed(speed)
        self.set_radius(radius)

    def next(self):
        self._pattern = self._get_hilbert(self._order, [-self._radius,-self._radius], [self._radius,self._radius])
        logging.debug('Pattern: %s' % self._pattern)
        layer = Layer(0.0)
        layer.commands.append(LateralMove(self._last_xy, self._pattern[0], self._speed))
        self._last_xy = self._pattern[0]
        for x,y in self._pattern[1:]:
            next_xy = [ x , y ]
            layer.commands.append(LateralDraw(self._last_xy,next_xy,self._speed))
            self._last_xy = next_xy
        return layer

    def _get_hilbert(self, order, lower_bounds, upper_bounds):
        [x0,y0] = lower_bounds
        [x1,y1] = upper_bounds
        [xi,yj] = [abs(x1-x0),abs(y1-y0)]
        self._points = []
        self._hilbert(x0,y0,xi,0.0,0.0,yj, order)
        return self._points

    def _hilbert(self,x0, y0, xi, xj, yi, yj, n, points = []) :
        if n <= 0:
            X = x0 + (xi + yi)/2
            Y = y0 + (xj + yj)/2
            self._points.append([X,Y])
        else:
            self._hilbert(x0,               y0,               yi/2, yj/2, xi/2, xj/2, n - 1)
            self._hilbert(x0 + xi/2,        y0 + xj/2,        xi/2, xj/2, yi/2, yj/2, n - 1)
            self._hilbert(x0 + xi/2 + yi/2, y0 + xj/2 + yj/2, xi/2, xj/2, yi/2, yj/2, n - 1)
            self._hilbert(x0 + xi/2 + yi,   y0 + xj/2 + yj,  -yi/2,-yj/2,-xi/2,-xj/2, n - 1)

class SquareGenerator(TestLayerGenerator):
    def __init__(self, speed = 100.0, radius = 20.0):
        self.set_speed(speed)
        self.set_radius(radius)

    def next(self):
        layer = Layer(0.0)
        layer.commands.append(LateralDraw([-self._radius, self._radius],[ self._radius, self._radius], self._speed))
        layer.commands.append(LateralDraw([ self._radius, self._radius],[ self._radius,-self._radius], self._speed))
        layer.commands.append(LateralDraw([ self._radius,-self._radius],[-self._radius,-self._radius], self._speed))
        layer.commands.append(LateralDraw([-self._radius,-self._radius],[-self._radius, self._radius], self._speed))
        return layer

import math
class CircleGenerator(TestLayerGenerator):
    def __init__(self, speed = 100.0, radius = 20.0, steps = 20):
        self.set_speed(speed)
        self.set_radius(radius)
        self._steps = steps
        self.last_xy = [0.0,0.0]

    def next(self):
        layer = Layer(0.0)
        for point in self.points():
            layer.commands.append(LateralDraw(self.last_xy,point, self._speed))
            self.last_xy = point
        return layer

    def points(self):
        angle_step =  (2 * math.pi / self._steps)
        for i in range(0,self._steps):
            theta =  angle_step * i
            x = math.sin(theta) * self._radius
            y = math.cos(theta) * self._radius
            yield [x,y]

class SpiralGenerator(TestLayerGenerator):
    def __init__(self, speed = 100.0, radius = 20.0, steps = 50, overlaps = 6):
        self.set_speed(speed)
        self.set_radius(radius)
        self._steps = steps
        self._overlaps = 10
        self.last_xy = [0.0,0.0]

    def next(self):
        layer = Layer(0.0)
        layer.commands.append(LateralMove(self.last_xy,[0.0,0.0], self._speed))
        self.last_xy = [0.0,0.0]
        for point in self.points():
            layer.commands.append(LateralDraw(self.last_xy,point, self._speed))
            self.last_xy = point
        return layer

    def points(self):
        inc = self._radius / (self._steps * self._overlaps)
        angle_step =  (2 * math.pi / self._steps)
        radius = 0.0
        for i in range(0,self._steps * self._overlaps):
            theta =  angle_step * i
            x = math.sin(theta) * radius
            y = math.cos(theta) * radius
            radius += inc
            yield [x,y]

class MemoryHourglassGenerator(TestLayerGenerator):
    def __init__(self, speed = 100.0, radius = 20.0):
        self.set_speed(speed)
        self.set_radius(radius)
        self.path =  [
                 [0.0 ,  0.0], [0.3 ,  0.0], [ 0.4,  0.1], [ 0.5,  0.0], [ 0.6, -0.1], [ 0.7,  0.0], [ 1.0,  0.0],
                 [0.0 ,  1.0], [0.0 ,  0.7], [-0.1,  0.6], [ 0.0,  0.5], [ 0.1,  0.4], [ 0.0,  0.3], [ 0.0,  0.0], 
                 [-0.3,  0.0], [-0.4, -0.1], [-0.5,  0.0], [-0.6,  0.1], [-0.7,  0.0], [-1.0,  0.0], [ 0.0, -1.0],
                 [0.0 , -0.7], [0.1 , -0.6], [ 0.0, -0.5], [-0.1, -0.4], [ 0.0, -0.3]
                ]

    def next(self):
        layer = Layer(0.0)
        last = [ a * self._radius for a in self.path[-1:][0] ]
        for point in self.path:
            scaled_point = [ a * self._radius for a in point ]
            layer.commands.append(LateralDraw(last,scaled_point, self._speed))
            last = scaled_point
        return layer

class CureTestGenerator(LayerGenerator):
    def __init__(self, base_height, total_height, start_speed, stop_speed, sublayer_height):
        base_height = float(base_height)
        total_height = float(total_height)
        self.start_speed = float(start_speed)
        stop_speed = float(stop_speed)
        self._sub_layer_height = float(sublayer_height)
        logging.info("Base Height: %s" % base_height)
        logging.info("Total Height: %s" % total_height)
        logging.info("Start Speed: %s" % self.start_speed)
        logging.info("Stop Speed: %s" % stop_speed)
        logging.info("Sublayer Height: %s" % self._sub_layer_height)

        self._base_layers = base_height / self._sub_layer_height
        self._number_of_layers = total_height / self._sub_layer_height
        logging.info("Total layer to print: %s" % self._number_of_layers)
        self._base_layer_speed = self.start_speed + ((stop_speed - self.start_speed) / 2.0) 
        self._speed_per_layer = (stop_speed - self.start_speed) / (self._number_of_layers - self._base_layers)
        self._current_layer = 0

    def next(self):
        if self._current_layer > self._number_of_layers:
            raise StopIteration

        if self._current_layer < self._base_layers:
            current_speed = self._base_layer_speed
        else:
            current_speed = (self._speed_per_layer * (self._current_layer - self._base_layers)) + self.start_speed

        logging.info("Speed : %s" % current_speed)
        commands = [
            LateralDraw([0,0],[10,0], current_speed),
            LateralDraw([10,0],[10,10], current_speed),
            LateralMove([10,10],[0,0], current_speed),
        ]
        layer = Layer(float(self._current_layer * self._sub_layer_height), commands = commands)
        self._current_layer += 1
        return layer
