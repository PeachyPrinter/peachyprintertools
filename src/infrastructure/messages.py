import move_pb2


class ProtoBuffMessage(object):
    def to_protobuf_bytes(self):
        raise NotImplementedError()

    @classmethod
    def from_protobuf_bytes(cls, proto_bytes):
        raise NotImplementedError()


class Move(ProtoBuffMessage):
    def __init__(self, identifier, x, y, laser_power):
        self.identifier = identifier
        self.x = x
        self.y = y
        self.laser_power = laser_power

    def to_protobuf_bytes(self):
        encoded = move_pb2.Move()
        encoded.id = self.identifier
        encoded.x = self.x
        encoded.y = self.y
        encoded.laserPower = self.laser_power
        return encoded.SerializeToString()

    @classmethod
    def from_protobuf_bytes(cls, proto_bytes):
        decoded = move_pb2.Move().ParseFromString(proto_bytes)
        return cls(decoded.id, decoded.x, decoded.y, decoded.laserPower)


class Ack(ProtoBuffMessage):
    def __init__(self, identifier):
        self.identifier = identifier

    def to_protobuf_bytes(self):
        encoded = move_pb2.Ack()
        encoded.id = self.identifier
        return encoded.SerializeToString()

    @classmethod
    def from_protobuf_bytes(cls, proto_bytes):
        decoded = move_pb2.Ack().ParseFromString(proto_bytes)
        return cls(decoded.id)


class Nack(ProtoBuffMessage):
    def __init__(self, identifier, reason):
        self.identifier = identifier
        self.reason = reason

    def to_protobuf_bytes(self):
        encoded = move_pb2.Nack()
        encoded.id = self.identifier
        encoded.reason = self.reason
        return encoded.SerializeToString()

    @classmethod
    def from_protobuf_bytes(cls, proto_bytes):
        decoded = move_pb2.Nack().ParseFromString(proto_bytes)
        return cls(decoded.id, decoded.reason)
