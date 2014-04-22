import numpy as np
import logging
from domain.transformer import Transformer

class OneToOneTransformer(Transformer):
    def transform(self, xyz):
        x,y,z = xyz
        return [x,y,z]

'Takes Values from -1.0 to 1.0 on both axis and returns a scaled version between 0 and 1'
class TuningTransformer(Transformer):
    def __init__(self,scale = 1.0):
        if scale > 0.0 and scale <= 1.0:
            self._scale = scale
        else:
            raise Exception("Scale must be between 0.0 and 1.0")

    def transform(self, xyz):
        x,y,z = xyz
        if abs(x) > 1.0 or abs(y) > 1.0:
            raise Exception("Points out of bounds")
        x = self._transform(x)
        y = self._transform(y)
        return [x,y]
 
    def _transform(self, axis):
        return ((axis * self._scale) + 1.0) / 2.0

class HomogenousTransformer(Transformer):
    def __init__(self, config, scale = 1.0):
        self._scale = scale
        logging.info(config)
        self._lower_transform = self._get_transformation_matrix(config['lower_points'])
        self._upper_transform = self._get_transformation_matrix(config['upper_points'])
        self._upper_height = config['height']
        self._cache = {}

    def _get_transformation_matrix(self,mappings):
        mapping_matrix = self._build_matrix(mappings)
        b = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
        solved_matrix = np.linalg.solve(mapping_matrix,b)
        forwards = np.matrix([solved_matrix[0:3], solved_matrix[3:6], solved_matrix[6:9]])
        inverse = forwards.I
        logging.debug("Transformation Matrix: %s " % inverse)
        return inverse

    def _build_matrix(self, points):
        builder = []
        index = 0
        for ((xp,yp),(xi,yi)) in points.items():
            augment = self._augment(index,xi,yi)
            builder.append([ xp, yp,  1,  0,  0,  0,  0,  0,  0] + augment[0])
            builder.append([  0,  0,  0, xp, yp,  1,  0,  0,  0] + augment[1])
            builder.append([  0,  0,  0,  0,  0,  0, xp, yp,  1] + augment[2])
            index += 1
        builder.append([  1,  1,  1,  1,  1,  1,  1,  1,  1,     0,   0,   0,   0])
        return np.array(builder)

    def _augment(self,index,xi,yi):
        augment = [[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for i in range(0,4):
            if i == index:
                augment[0][i] = -xi
                augment[1][i] = -yi
                augment[2][i] = -1
        return augment

    def _transforms_for_height(self, height):
        if height == 0:
            return self._lower_transform
        elif height == self._upper_height:
            return self._upper_transform
        elif height in self._cache.keys():
            logging.debug('Matrix cache hit')
            return self._cache[height]
        else:
            logging.debug('Calculating new transformation matrix')
            current = self._positional_transform(height)
            self._cache = { height : current}
            return current

    def _positional_transform(self,height):
        adjusted_height = height / self._upper_height
        return (adjusted_height * (self._upper_transform - self._lower_transform)) + self._lower_transform

    def transform(self,(x,y,z)):
        realworld = np.array([[x], [y], [1]])
        logging.debug('Z: %s M: %s' % (z, self._transforms_for_height(z)))
        computerland =  self._transforms_for_height(z) * realworld
        [kx, ky, k] = [computerland.item(i, 0) for i in range(3)]
        return (kx/k, ky/k)
       