
class Transformation(object):
    def __init__(self, polygon):
        self.polygon = polygon
        self.lr = polygon[0]
        self.ur = polygon[1]
        self.ul = polygon[2]
        self.ll = polygon[3]

    def translate(self, point):
        return point