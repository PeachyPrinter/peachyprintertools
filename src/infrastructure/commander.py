import serial

class Commander(object):
    def send_command(self, command):
        raise NotImplementedError("This is not implemented")

class SerialCommander(Commander):
    def __init__(self, port, baud= 9600):
        self._connection = serial.Serial(port,baud)

    def send_command(self, command):
        self._connection.write(command)

class NullCommander(Commander):
    def __init__(self):
        pass

    def send_command(self, command):
        pass
