class LayerGenerator(object):
    def __next__(self):
        return self.next()

    def __iter__(self):
        return self

    def next(self):
        raise NotImplementedError()