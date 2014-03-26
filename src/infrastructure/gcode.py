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

    def __iter__(self):
        return self

    # Python 3 compatibility
    def __next__(self):
        return self.next()

    def next(self):
        layer = Layer(self.current_z)
        self.info("commands %s" % layer.commands)
        command = None
        running = True
        while running and type(command) != VerticalMove:
            try:
                line = self.file_object.next()
                self.line_number += 1
                self.info("%d: Processing: %s" % (self.line_number, line))
                command = self._parse(line.strip(), self.line_number)
                if command and type(command) != VerticalMove:
                    self.info("Adding: %s to layer" % str(command))
                    layer.commands.append(command)
            except StopIteration:
                self.info("EOF: Finalizing")
                running = False
                self.info(layer.commands)
                if layer.commands == []:
                    self.info("EOF: Stopping")
                    raise StopIteration
        self.info("Layer Complete" )
        return layer

    def _parse(self, line, line_number):
        if line[0] == (";"):
            return None
        commands = line.split(' ')
        if commands[0] in self._COMMAND_HANDLERS:
            return self._COMMAND_HANDLERS[commands[0]](self,line)
        self.errors.append('Unreconized Command %s: %s' % (line_number,line))
        return None

    def _command_draw(self, line):
        command_details = line.split(' ')
        x = None
        y = None
        z = None
        rate = None
        for detail in command_details[1:]:
            detail_type = detail[0]
            if detail_type == 'X':
                x = float(detail[1:])
            elif detail_type == 'Y':
                y = float(detail[1:])
            elif detail_type == 'Z':
                pass
            elif detail_type == 'F':
                rate = float(detail[1:])
            elif detail_type == 'E':
                pass
            else:
                return None
        return LateralDraw(x,y,rate)

    _COMMAND_HANDLERS = {
        'G01' : _command_draw,
        'G1' : _command_draw
    }