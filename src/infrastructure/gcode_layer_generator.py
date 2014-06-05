import collections
from domain.commands import *
from domain.layer_generator import LayerGenerator
import logging
import sys

class GCodeReader(object):
    def __init__(self, file_object):
        self.file_object = file_object

    def check(self):
        layers = GCodeToLayerGenerator(self.file_object)
        for layer in layers:
            pass
        return layers.errors

    def get_layers(self):
        return GCodeToLayerGenerator(self.file_object)

class GCodeToLayerGenerator(LayerGenerator):
    def __init__(self, file_object):
        super(GCodeToLayerGenerator, self).__init__()
        self.errors = []
        self.warning = []
        self._file_object = file_object
        self._line_number = 0
        self._current_z = 0.0
        self._gcode_command_reader = GCodeCommandReader()
        self._command_queue = collections.deque()
        self._file_complete = False

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        return self._get_layer(None)

    def _populate_buffer(self):
        try:
            gcode_line = self._file_object.next()
            self._line_number +=1
            try:
                commands = self._gcode_command_reader.to_command(gcode_line.strip())
                for command in commands:
                    self._command_queue.append(command)
            except Exception as ex:
                logging.error("Error %s: %s" % (self._line_number, ex.message))
                self.errors.append("Error %s: %s" % (self._line_number, ex.message))
        except StopIteration:
            self._file_complete = True


    def _get_layer(self, layer = None):
        generating_layer = True
        while generating_layer:
            try:
                command = self._command_queue.popleft()
                if type(command) == VerticalMove:
                    if layer:
                        self._command_queue.appendleft(command)
                        return layer
                    else:
                        layer = Layer(command.end)
                else:
                    if layer:
                        layer.commands.append(command)
                    else:
                        layer = Layer(0.0, [ command ])
            except IndexError:
                if self._file_complete:
                    if layer:
                        return layer
                    else:
                        raise StopIteration
                else:
                    self._populate_buffer()

class GCodeCommandReader(object):
    _INCHES2MM = 25.4
    def __init__(self, verbose = False):
        super(GCodeCommandReader, self).__init__()
        self._mm_per_s = None
        self._current_xy = [0.0,0.0]
        self._current_z_pos = 0.0
        self._layer_height = None
        self._units = 'mm'

    def to_command(self, gcode):
        if self._can_ignore(gcode):
            return []
        commands = gcode.split(' ')
        if commands[0] in self._COMMAND_HANDLERS:
            return self._COMMAND_HANDLERS[commands[0]](self,gcode)
        logging.error('Unsupported Command: %s' % (gcode))
        raise Exception('Unsupported Command: %s' % (gcode))

    def _command_draw(self, line):
        command_details = line.split(' ')
        x_mm = None
        y_mm = None
        z_mm = None
        write = False

        for detail in command_details[1:]:
            detail_type = detail[0]
            if detail_type == 'X':
                x_mm = self._to_mm(float(detail[1:]))
            elif detail_type == 'Y':
                y_mm = self._to_mm(float(detail[1:]))
            elif detail_type == 'Z':
                z_mm = self._to_mm(float(detail[1:]))
            elif detail_type == 'F':
                self._mm_per_s = self._to_mm_per_second(float(detail[1:]))
            elif detail_type == 'E':
                write = float(detail[1:]) > 0.0
            else:
                logging.error("Warning gcode subcode [%s] not supported in command: [%s]" % (detail_type, line))

        if not self._mm_per_s:
            logging.error("Feed Rate Never Specified")
            raise Exception("Feed Rate Never Specified")
        if z_mm:
            if x_mm or y_mm:
                logging.warning("Vertically angled writes are not supported...yet")
                up = self._get_vertical_movement(z_mm,write)
                over = self._get_lateral_movement([x_mm,y_mm], write)
                return up + over
            return self._get_vertical_movement(z_mm,write)
        elif x_mm and y_mm:
            return self._get_lateral_movement([x_mm,y_mm], write)
        else:
            return []

    def _get_vertical_movement(self, z_mm, write):
        self._zaxis_change(z_mm)
        commands = [ ]
        if write:
            distance_to_traverse = z_mm - self._current_z_pos
            layers = int(distance_to_traverse / self._layer_height)
            commands = []
            for layer in range(0, layers + 1):
                next_layer_height = self._current_z_pos + self._layer_height
                commands.append(VerticalMove(self._current_z_pos, next_layer_height ,self._mm_per_s))
                commands.append(LateralDraw(self._current_xy,self._current_xy,self._mm_per_s))
                self._current_z_pos = next_layer_height
        else:
            commands.append(VerticalMove(self._current_z_pos,z_mm,self._mm_per_s))
        self._current_z_pos = z_mm
        return commands


    def _get_lateral_movement(self, xy_mm, write):
        command = []
        if write:
            command = [ LateralDraw(self._current_xy,xy_mm,self._mm_per_s) ]
        else:
            command = [ LateralMove(self._current_xy,xy_mm,self._mm_per_s) ]
        self._current_xy = xy_mm
        return command

    def _zaxis_change(self,z_mm):
        if self._current_z_pos and self._current_z_pos > z_mm:
            logging.error("Negitive Vertical Movement Unsupported")
            raise Exception("Negitive Vertical Movement Unsupported")
        else:
            self._update_layer_height(self._current_z_pos,z_mm)
    
    def _to_mm_per_second(self,value_per_minute):
        if self._units == 'inches':
            return value_per_minute * self._INCHES2MM / 60.0
        else:
            return value_per_minute / 60.0

    def _to_mm(self, value):
        if self._units == 'inches':
            return self._INCHES2MM * value
        else:
            return value


    def _update_layer_height(self, current_height, new_height):
        if current_height:
            this_layer_height = new_height - current_height
            if self._layer_height:
                if self._layer_height > this_layer_height:
                    self._layer_height = this_layer_height
            else:
                self._layer_height = this_layer_height

    def _can_ignore(self, command):
        if command in [ '\n', '' ]:
            return True
        for prefix in self._IGNORABLE_PREFIXES:
            if command.startswith(prefix):
                return True
        return False

    def _units_mm(self, line):
        self._units = 'mm'

    def _units_inches(self, line):
        self._units = 'inches'

    _COMMAND_HANDLERS = {
        'G01' : _command_draw,
        'G1'  : _command_draw,
        'G0'  : _command_draw,
        'G01' : _command_draw,
        'G21' : _units_mm,
        'G20' : _units_inches
    }

    _IGNORABLE_PREFIXES = [ 
    ';', # Comment
    'M', # Miscilanious / Machine Specific
    'O', # Title
    'G90', # Absolute Posisitioning Currently assumed
    ] 
