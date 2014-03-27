from domain.commands import *

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
    
class ConsoleLog(object):
    def __init__(self,on):
        self.on = on

    def info(self, message):
        if self.on:
            print(message)

class GCodeToLayerGenerator(ConsoleLog):
    def __init__(self, file_object, verbose = False):
        super(GCodeToLayerGenerator, self).__init__(on = verbose)
        self.errors = []
        self.warning = []
        self.file_object = file_object
        self.line_number = 0
        self.current_z = 0.0
        self.gcode_command_reader = GCodeCommandReader()

    def __iter__(self):
        return self

    # Python 3 compatibility
    def __next__(self):
        return self.next()

    def next(self):
        layer = Layer(self.current_z)
        command = None
        running = True
        while running and type(command) != VerticalMove:
            try:
                line = self.file_object.next()
                self.line_number += 1
                self.info("%d: Processing: %s" % (self.line_number, line))
                try:
                    commands = self.gcode_command_reader.to_command(line.strip())
                    for command in commands:
                        if command and type(command) !=  VerticalMove:
                            self.info("Adding: %s to layer" % str(command))
                            layer.commands.append(command)
                        else:
                            self.current_z = command.z
                except Exception as ex:
                    self.info("Error %s: %s" % (self.line_number, ex.message))
                    self.errors.append("Error %s: %s" % (self.line_number, ex.message))
            except StopIteration:
                self.info("EOF: Finalizing")
                running = False
                if layer.commands == []:
                    self.info("EOF: Stopping")
                    raise StopIteration
        self.info("Layer Complete" )
        return layer

class GCodeCommandReader(ConsoleLog):
    def __init__(self, verbose = False):
        super(GCodeCommandReader, self).__init__(on = verbose)
        self._mm_per_s = None
        self._current_x_pos = 0.0
        self._current_y_pos = 0.0
        self._current_z_pos = 0.0
        self._layer_height = None

    def to_command(self, gcode):
        if self._can_ignore(gcode):
            return []
        commands = gcode.split(' ')
        if commands[0] in self._COMMAND_HANDLERS:
            return self._COMMAND_HANDLERS[commands[0]](self,gcode)
        raise Exception('Unreconized Command: %s' % (gcode))

    def _command_draw(self, line):
        command_details = line.split(' ')
        x_mm = None
        y_mm = None
        z_mm = None
        mm_per_s = None
        write = False
        layer_height = None
        for detail in command_details[1:]:
            detail_type = detail[0]
            if detail_type == 'X':
                x_mm = float(detail[1:])
            elif detail_type == 'Y':
                y_mm = float(detail[1:])
            elif detail_type == 'Z':
                z_mm = float(detail[1:])
            elif detail_type == 'F':
                self._mm_per_s = self._to_mm_per_second(float(detail[1:]))
            elif detail_type == 'E':
                if float(detail[1:]) <=0:
                    write = False
                else:
                    write = True
            else:
                return None

        if not self._mm_per_s:
            raise Exception("Feed Rate Never Specified")
        if z_mm:
            self._zaxis_change(z_mm)
            if write:
                distance_to_traverse = z_mm - self._current_z_pos
                layers = int(distance_to_traverse / self._layer_height)
                commands = []
                for layer in range(0, layers + 1):
                    commands.append(VerticalMove(self._current_z_pos + self._layer_height * (layer + 1),self._mm_per_s))
                    commands.append(LateralDraw(self._current_x_pos,self._current_y_pos,self._mm_per_s))
                self._current_z_pos = z_mm
                return commands
            else:
                self._current_z_pos = z_mm
                return [ VerticalMove(z_mm,self._mm_per_s) ]
        elif x_mm and y_mm:
            return self._get_lateral_movement(x_mm,y_mm, write)
        else:
            return []

    def _get_lateral_movement(self, x_mm, y_mm, write):
        self._current_x_pos = x_mm
        self._current_y_pos = y_mm
        if write:
            return [ LateralDraw(x_mm,y_mm,self._mm_per_s) ]
        else:
            return [ LateralMove(x_mm,y_mm,self._mm_per_s) ]

    def _zaxis_change(self,z_mm):
        if self._current_z_pos and self._current_z_pos > z_mm:
            raise Exception("Negitive Vertical Movement Unsupported")
        else:
            self._update_layer_height(self._current_z_pos,z_mm)
    
    def _to_mm_per_second(self,mm_per_minute):
        return mm_per_minute / 60.0

    def _update_layer_height(self, current_height, new_height):
        if current_height:
            this_layer_height = new_height - current_height
            if self._layer_height:
                if self._layer_height > this_layer_height:
                    self._layer_height = this_layer_height
            else:
                self._layer_height = this_layer_height

    def _can_ignore(self, command):
        for prefix in self._IGNORABLE_PREFIXES:
            if command.startswith(prefix):
                return True
        return False

    _COMMAND_HANDLERS = {
        'G01' : _command_draw,
        'G1'  : _command_draw,
        'G0'  : _command_draw,
        'G01' : _command_draw,
    }

    _IGNORABLE_PREFIXES = [ 
    ';', # Comment
    'M', # Miscilanious / Machine Specific
    'O', # Title
    'G90', # Absolute Posisitioning Currently assumed

    ] 