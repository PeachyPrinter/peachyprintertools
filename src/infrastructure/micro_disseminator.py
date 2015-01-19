import logging
from domain.disseminator import Disseminator


class MicroDisseminator(Disseminator):
    def __init__(self, laser_control, comunication, data_rate):
        self._data_rate = data_rate
        pass

    def process(self, data):
        raise NotImplementedError()

    def next_layer(self, height):
        raise NotImplementedError()

    @property
    def samples_per_second(self):
        return self._data_rate

    def close(self):
        pass
