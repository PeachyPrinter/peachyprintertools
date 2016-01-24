import logging
logger = logging.getLogger('peachy')
try:
    from messages_pb2 import Move, DripRecorded, SetDripCount, MoveToDripCount, IAm, EnterBootloader
except Exception as ex:
    logger.error(
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
            logger.error("Protobuf Message encoding incomplete. Did the spec change? Have you compiled your proto files?")
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
            logger.error("Protobuf Message encoding incomplete. Did the spec change? Have you compiled your proto files?")
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


class SetDripCountMessage(ProtoBuffableMessage):
    TYPE_ID = 4

    def __init__(self, drips):
        self._drips = drips

    @property
    def drips(self):
        return self._drips

    def get_bytes(self):
        encoded = SetDripCount()
        encoded.drips = self._drips
        if encoded.IsInitialized():
            return encoded.SerializeToString()
        else:
            logger.error("Protobuf Message encoding incomplete. Did the spec change? Have you compiled your proto files?")
            raise Exception("Protobuf Message encoding incomplete")

    @classmethod
    def from_bytes(cls, proto_bytes):
        decoded = SetDripCount()
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


class MoveToDripCountMessage(ProtoBuffableMessage):
    TYPE_ID = 5

    def __init__(self, drips):
        self._drips = drips

    @property
    def drips(self):
        return self._drips

    def get_bytes(self):
        encoded = MoveToDripCount()
        encoded.drips = self._drips
        if encoded.IsInitialized():
            return encoded.SerializeToString()
        else:
            logger.error("Protobuf Message encoding incomplete. Did the spec change? Have you compiled your proto files?")
            raise Exception("Protobuf Message encoding incomplete")

    @classmethod
    def from_bytes(cls, proto_bytes):
        decoded = MoveToDripCount()
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


class IdentifyMessage(ProtoBuffableMessage):
    TYPE_ID = 7

    def get_bytes(self):
        return ""

    @classmethod
    def from_bytes(cls, proto_bytes):
        return cls()


class IAmMessage(ProtoBuffableMessage):
    TYPE_ID = 8

    def __init__(self, swrev, hwrev, sn, dataRate):
        self._swrev = swrev
        self._hwrev = hwrev
        self._sn = sn
        self._dataRate = dataRate

    @property
    def swrev(self):
        return self._swrev
    
    @property
    def hwrev(self):
        return self._hwrev

    @property
    def sn(self):
        return self._sn

    @property
    def dataRate(self):
        return self._dataRate

    def get_bytes(self):
        encoded = IAm()
        encoded.swrev = self._swrev
        encoded.hwrev = self._hwrev
        encoded.sn = self._sn
        encoded.dataRate = self._dataRate
        if encoded.IsInitialized():
            return encoded.SerializeToString()
        else:
            logger.error("Protobuf Message encoding incomplete. Did the spec change? Have you compiled your proto files?")
            raise Exception("Protobuf Message encoding incomplete")

    @classmethod
    def from_bytes(cls, proto_bytes):
        decoded = IAm()
        decoded.ParseFromString(proto_bytes)
        return cls(str(decoded.swrev), str(decoded.hwrev), str(decoded.sn), decoded.dataRate)

    def __eq__(self, other):
        if (self.__class__ == other.__class__ and
            self._swrev == other._swrev and
            self._hwrev == other._hwrev and
            self._sn == other._sn and
            self._dataRate == other._dataRate
            ):
            return True
        else:
            return False

    def __repr__(self):
        return "Serial Number: {}\n Sofware Revision: {}\nHardware Revision: {}\nData Rate: {}".format(self._sn, self._swrev, self._hwrev, self._dataRate)


class EnterBootloaderMessage(ProtoBuffableMessage):
    TYPE_ID = 10

    def get_bytes(self):
        return ""

    @classmethod
    def from_bytes(cls, proto_bytes):
        return cls()

    def __eq__(self, other):
        return type(other) == type(self)
