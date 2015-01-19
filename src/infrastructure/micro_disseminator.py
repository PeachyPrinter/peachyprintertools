import logging
import sys
from domain.disseminator import Disseminator
from infrastructure.messages import MoveMessage


class MicroDisseminator(Disseminator):
    def __init__(self, laser_control, comunication, data_rate):
        self._data_rate = data_rate
        self._laser_control = laser_control
        self._communication = comunication
        self._message_id = 0
        self.LASER_MAX = pow(2, 8) - 1
        
    def process(self, data):
        laser_power = int(self._laser_control.laser_power() * self.LASER_MAX)
        for (x, y) in data:
            data = MoveMessage(self._message_id, int(x), int(y), laser_power)
            self._communication.send(data)
            self._message_id_plus()

    def _message_id_plus(self):
        if self._message_id + 1 > sys.maxint:
            self._message_id = 0
        else:
            self._message_id += 1

    def next_layer(self, height):
        pass

    @property
    def samples_per_second(self):
        return self._data_rate

    def close(self):
        pass
