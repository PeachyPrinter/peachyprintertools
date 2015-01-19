import serial

class Communicator(object):
    def send(self, type_id, message):
        raise NotImplementedError()

    def recieve(self, type_id, handler):
        raise NotImplementedError()


class SerialCommunicator(object):
    def __init__(self, port, header, footer, escape):
        pass

    def send(self, type_id, message):
        pass
