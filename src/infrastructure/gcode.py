class Command(object):
    pass

class Draw(Command):
    pass

class Move(Command):
    pass

class Layer(object):
    def get_commands():
        pass
        # yields commands

class GCodeError(object):
    def __init__(self,error):
        self.error = error

class GCodeReader(object):
    def __init__(self):
        pass

    def check(self, file_object, verbose = False):
        lines = [ line.strip() for line in file_object ]
        errors = []
        line_number = 0
        for line in lines:
            line_number += 1
            result = self._parse(line, line_number)
            if type(result) == GCodeError:
                errors.append(result.error)
        return errors

    def get_layers(self, file_object):
        # yields Layer
        pass

    def _parse(self, line, line_number):
        if line[0] == (";"):
            return None
        command = line.split(' ')
        if command[0] in self._COMMAND_HANDLERS:
            return None
        return GCodeError('Unreconized Command %s: %s' % (line_number,line))

    def _command_move(self, line):
        pass

    _COMMAND_HANDLERS = {
        'G01' : _command_move,
        'G1' : _command_move
    }
