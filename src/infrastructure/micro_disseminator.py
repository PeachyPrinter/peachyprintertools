import logging
from domain.disseminator import Disseminator


class MicroDisseminator(Disseminator):
    def __init__(self, laser_control, comunication, data_rate):
        self._data_rate = data_rate
        self._laser_control = laser_control
        self._communication = comunication

    def process(self, data):
        raise NotImplementedError()

    def next_layer(self, height):
        pass

    @property
    def samples_per_second(self):
        return self._data_rate

    def close(self):
        pass