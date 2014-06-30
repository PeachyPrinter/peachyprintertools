from domain.transformer import Transformer


class PointTransformer(Transformer):
    def __init__(self, calibration_points):
        raise Exception("Not Enough Points")

    def transform(self,xyz):
        return [0.0,0.0,0.0,0.0]
