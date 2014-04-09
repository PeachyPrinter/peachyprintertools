import numpy as np

class Transformer(object):
    def transform(self, xyz):
        raise NotImplementedException

class OneToOneTransfomer(Transformer):
    def transform(self, xyz):
        x,y,z = xyz
        return [x,y,z]