import logging
from domain.disseminator import Disseminator
from infrastructure.messages import Move


class MicroDisseminator(Disseminator):
    def __init__(self, laser_control, comunication, data_rate):
        self._data_rate = data_rate
        self._laser_control = laser_control
        self._communication = comunication

    def process(self, data):
        for (x, y) in data:
            data = Move(int(x), int(y), self._laser_control.laser_power())
            self._communication.send(data)

    def next_layer(self, height):
        pass

    @property
    def samples_per_second(self):
        return self._data_rate

    def close(self):
        pass
