class Disseminator(object):
    def process(self, data):
        raise NotImplementedError()

    def next_layer(self, height):
        raise NotImplementedError()

    @property
    def samples_per_second(self):
        raise NotImplementedError()

    def close(self):
        pass
