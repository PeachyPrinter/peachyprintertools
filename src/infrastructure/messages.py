import logging
try:
    from messages_pb2 import Move, DripRecorded
except Exception as ex:
    logging.error(
        "\033[91m Cannot import protobuf classes, Have you compiled your protobuf files?\033[0m")
    raise ex


class ProtoBuffableMessage(object):
    TYPE_ID = 0

    def get_bytes(self):
        raise NotImplementedError()

    @classmethod
    def from_bytes(cls, proto_bytes):
        raise NotImplementedError()


class MoveMessage(ProtoBuffableMessage):
    TYPE_ID = 2

    def __init__(self, x_pos, y_pos, laser_power):
        self._x_pos = x_pos
        self._y_pos = y_pos
        self._laser_power = laser_power

    @property
    def x_pos(self):
        return self._x_pos

    @property
    def y_pos(self):
        return self._y_pos

    @property
    def laser_power(self):
        return self._laser_power

    def get_bytes(self):
        encoded = Move()
        encoded.x = self._x_pos
        encoded.y = self._y_pos
        encoded.laserPower = self._laser_power
        if encoded.IsInitialized():
            return encoded.SerializeToString()
        else:
            logging.error("Protobuf Message encoding incomplete. Did the spec change? Have you compiled your proto files?")
            raise Exception("Protobuf Message encoding incomplete")

    @classmethod
    def from_bytes(cls, proto_bytes):
        decoded = Move()
        decoded.ParseFromString(proto_bytes)
        return cls(decoded.x, decoded.y, decoded.laserPower)

    def __eq__(self, other):
        if (self.__class__ == other.__class__ and
                self._x_pos == other._x_pos and
                self._y_pos == other._y_pos and
                self._laser_power == other._laser_power):
            return True
        else:
            return False

    def __repr__(self):
        return "x:y={}:{}, laser_power={}".format(self._x_pos, self._y_pos, self._laser_power)


class DripRecordedMessage(ProtoBuffableMessage):
    TYPE_ID = 3

    def __init__(self, drips):
        self._drips = drips

    @property
    def drips(self):
        return self._drips

    def get_bytes(self):
        encoded = DripRecorded()
        encoded.drips = self._drips
        if encoded.IsInitialized():
            return encoded.SerializeToString()
        else:
            logging.error("Protobuf Message encoding incomplete. Did the spec change? Have you compiled your proto files?")
            raise Exception("Protobuf Message encoding incomplete")

    @classmethod
    def from_bytes(cls, proto_bytes):
        decoded = DripRecorded()
        decoded.ParseFromString(proto_bytes)
        return cls(decoded.drips)

    def __eq__(self, other):
        if (self.__class__ == other.__class__ and
                self._drips == other._drips):
            return True
        else:
            return False

    def __repr__(self):
        return "drips={}".format(self._drips)
