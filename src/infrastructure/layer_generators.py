import logging

from domain.commands import *
from domain.layer_generator import LayerGenerator, TestLayerGenerator
import math

# -----------Testing Generators ----------------

class StubLayerGenerator(LayerGenerator):
    def __init__(self, layers):
        self._layers = layers

    def next(self):
        if len(self._layers) == 0:
            raise StopIteration()
        return self._layers.pop(0)

# -----------Pattern  Generators ----------------

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
    def __init__(self, starting_xy = [0.0,0.0],radius = 0.5 ,speed = 0.5,steps = 80):
        self.xy = starting_xy
        self._state = True
        self.set_speed(speed)
        self.set_radius(radius)
        self._steps = steps
        self.last_xy = [0.0,0.0]
        self._points = list(self.points())

    def next(self):
        layer = Layer(0.0)
        for point in self._points:
            if self._state:
                layer.commands.append(LateralDraw(self.last_xy,point, self._speed))
            else:
                layer.commands.append(LateralMove(self.last_xy,point, self._speed))
            self._state = not self._state
            self.last_xy = point
        return layer

    def points(self):
        angle_step =  (2 * math.pi / self._steps)
        for i in range(0,self._steps):
            theta =  angle_step * i
            x = math.sin(theta) * self._radius + 0.5
            y = math.cos(theta) * self._radius + 0.5
            yield [x,y]

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

class DampingTestGenerator(TestLayerGenerator):
    def __init__(self, speed = 100.0, radius = 20.0):
        self.set_speed(speed)
        self.set_radius(radius)

    def next(self):
        layer = Layer(0.0)
        layer.commands.append(LateralMove([ 0.0         , self._radius ],[ -self._radius,  self._radius ], self._speed))
        layer.commands.append(LateralMove([-self._radius, self._radius ],[ -self._radius,  0.0          ], self._speed * 100))
        layer.commands.append(LateralDraw([-self._radius, 0.0          ],[  self._radius,  0.0          ], self._speed))
        layer.commands.append(LateralMove([ self._radius, 0.0          ],[  self._radius, -self._radius ], self._speed))
        layer.commands.append(LateralMove([ self._radius,-self._radius ],[  0.0         , -self._radius ], self._speed * 100))
        layer.commands.append(LateralDraw([ 0.0         ,-self._radius ],[  0.0         ,  self._radius ], self._speed))
        return layer

class CircleGenerator(TestLayerGenerator):
    def __init__(self, speed = 100.0, radius = 20.0, steps = 20):
        self.set_speed(speed)
        self.set_radius(radius)
        self._steps = steps
        self.last_xy = [0.0,0.0]
        self.height = 0.0

    def next(self):
        self.height += 0.1
        layer = Layer(self.height)
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

class TwitchGenerator(TestLayerGenerator):
    def __init__(self, speed = 100.0, radius = 20.0):
        self.set_speed(speed)
        self.set_radius(radius)
        self.path =  [
                 [ 0.625 ,  1.000 ], [  0.625 ,  0.500 ], [  0.125,  0.125 ], [  0.625, -0.500 ], [  0.625, -1.000 ], 
                 [ 1.000,  -0.625 ], [  0.500,  -0.625 ], [ -0.125, -0.125 ], [ -0.500, -0.625 ], [ -1.000, -0.625 ], 
                ]

    def next(self):
        layer = Layer(0.0)
        last = [ a * self._radius for a in self.path[-1:][0] ]
        for point in self.path:
            scaled_point = [ a * self._radius for a in point ]
            layer.commands.append(LateralDraw(last,scaled_point, self._speed))
            last = scaled_point
        return layer

class NESWGenerator(TestLayerGenerator):
    def __init__(self, speed = 100.0, radius = 20.0):
        self.set_speed(speed)
        self.set_radius(radius)
        self.path =  [
                 ('m',[-0.1, 0.8]),('d',[-0.1, 1.0]),('d',[ 0.1, 0.8]),('d',[ 0.1, 1.0]),   #N
                 ('m',[ 1.0, 0.1]),('d',[ 0.8, 0.1]),('d',[ 0.8, 0.0]),('d',[ 0.9, 0.0]),('d',[ 0.8, 0.0]),('d',[ 0.8,-0.1]),('d',[ 1.0,-0.1]),   #E
                 ('m',[ 0.1,-0.8]),('d',[-0.1,-0.8]),('d',[-0.1,-0.9]),('d',[ 0.1,-0.9]),('d',[ 0.1,-1.0]),('d',[-0.1,-1.0]),   #S
                 ('m',[-0.8, 0.1]),('d',[-0.8,-0.1]),('d',[-0.9, 0.0]),('d',[-1.0,-0.1]),('d',[-1.0, 0.1])   #W
                ]

    def next(self):
        layer = Layer(0.0)
        last = [ a * self._radius for a in self.path[1][-1:][0] ]
        for (k, point) in self.path:
            scaled_point = [ a * self._radius for a in point ]
            if k == 'd':
                layer.commands.append(LateralDraw(last,scaled_point, self._speed))
            else:
                layer.commands.append(LateralMove(last,scaled_point, self._speed))
            last = scaled_point
        return layer

# -----------Cure Generators ----------------

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

    def commands(self,base):
        if base:
            return [
                LateralDraw([0,0],[10,0], self._base_layer_speed),
                LateralDraw([10,0],[10,10], self._base_layer_speed),
                LateralDraw([10,10],[0,0], self._base_layer_speed),
            ]
        else:
            current_speed = (self._speed_per_layer * (self._current_layer - self._base_layers)) + self.start_speed
            logging.info("Speed : %s" % current_speed)
            return [
                LateralDraw([0,0],[10,0], current_speed),
                LateralDraw([10,0],[10,10], current_speed),
                LateralMove([10,10],[0,0], current_speed),
            ]

    def next(self):
        if self._current_layer > self._number_of_layers:
            raise StopIteration
        base_layer = self._current_layer < self._base_layers

        layer = Layer(float(self._current_layer * self._sub_layer_height), commands = self.commands(base_layer))
        self._current_layer += 1
        return layer

# -----------Augmenting Generators ----------------

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
    def __init__(self,layer_generator):
        self._layer_generator = layer_generator
        self._shuffle_point = 0

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        return self._shuffle(self._layer_generator.next())

    def _shuffle(self, layer):
        if self._shuffle_point >= len(layer.commands):
            self._shuffle_point = 0
        layer.commands = layer.commands[self._shuffle_point:] + layer.commands[:self._shuffle_point]
        self._shuffle_point +=1
        return layer

    def _load_layer(self):
        try:
            self._next = self._layer_generator.next()
        except StopIteration:
            self._running = False

class OverLapGenerator(LayerGenerator):
    def __init__(self,layer_generator, overlap_mm = 1.0):
        self._layer_generator = layer_generator
        self._tollerance = 0.01
        self.overlap_mm = overlap_mm

    def __iter__(self):
        return self

    def __next__(self):
        return  self.next()

    def _same_spot(self,pos1,pos2):
        return (abs(pos1[0] - pos2[0]) < self._tollerance) and (abs(pos1[0] - pos2[0]) < self._tollerance)

    def _2d_unit_vector(self,start,end):
        x = end[0] - start[0]
        y = end[1] - start[1]
        magnatude = math.sqrt(x**2 + y**2)
        vector = [x / magnatude, y / magnatude]
        return direction

    def _overlap_command(self,command, amount):
        x = command.end[0] - command.start[0]
        y = command.end[1] - command.start[1]
        magnatude = math.sqrt(x**2 + y**2)
        if magnatude == 0.0:
            return ([], amount)
        elif magnatude >= amount:
            vector = [(x / magnatude) * amount, (y / magnatude) * amount]
            end_pos = [command.start[0] + vector[0], command.start[1] + vector[1]] 
            return ([LateralDraw(command.start,end_pos,command.speed)], 0.0)
        else:
            return ([LateralDraw(command.start,command.end,command.speed)], amount - magnatude)
           

    def _overlap_layer(self, layer, threshold = 0.001):
        new_commands = []
        index = 0
        remainder = self.overlap_mm
        while remainder > threshold: # almost
            if len(layer.commands) < index:
                break
            if type(layer.commands[index]) == LateralMove:
                break
            new_command, remainder = self._overlap_command(layer.commands[index], remainder)
            new_commands = new_commands + new_command
            index += 1
        commands = layer.commands + new_commands
        return Layer(layer.z, commands = commands)

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
