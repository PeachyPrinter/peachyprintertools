class ProtoBuffableMessage(object):
    message_id = 0

    def get_bytes(self):
        raise NotImplementedError()

    @classmethod
    def from_bytes(self, bytes):
        raise NotImplementedError()


class Move(ProtoBuffableMessage):
    message_id = 1
    def __init__(self, x_pos, y_pos, laser_power):
        self._x_pos = x_pos
        self._y_pos = y_pos
        self._laser_power = laser_power

    def get_bytes(self):
        raise NotImplementedError()

    @classmethod
    def from_bytes(self, bytes):
        raise NotImplementedError()