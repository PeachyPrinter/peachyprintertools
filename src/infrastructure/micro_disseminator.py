import logging
import sys
from domain.disseminator import Disseminator
from infrastructure.messages import MoveMessage


class MicroDisseminator(Disseminator):
    def __init__(self, laser_control, comunication, data_rate):
        self._data_rate = data_rate
        self._laser_control = laser_control
        self._communication = comunication
        self.LASER_MAX = pow(2, 8) - 1
        self.DEFLECTION_MAX = pow(2, 16) - 1

    def process(self, data):
        laser_power = int(self._laser_control.laser_power() * self.LASER_MAX)
        for (x, y) in data:
            x_scaled = int(x * self.DEFLECTION_MAX)
            y_scaled = int(y * self.DEFLECTION_MAX)
            data = MoveMessage(x_scaled, y_scaled, laser_power)
            self._communication.send(data)

    def next_layer(self, height):
        pass

    @property
    def samples_per_second(self):
        return self._data_rate

    def close(self):
        self._communication.close()
