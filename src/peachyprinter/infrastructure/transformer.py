import numpy as np
import logging
logger = logging.getLogger('peachy')
from peachyprinter.domain.transformer import Transformer
import threading


class OneToOneTransformer(Transformer):
    def transform(self, xyz):
        x, y, z = xyz
        return [x, y, z]


'Takes Values from -1.0 to 1.0 on both axis and returns a scaled version between 0 and 1'


class TuningTransformer(Transformer):
    def __init__(self, scale=1.0):
        if scale > 0.0 and scale <= 1.0:
            self._scale = scale
        else:
            logger.error('Scale must be between 0.0 and 1.0 was %s' % scale)
            raise Exception('Scale must be between 0.0 and 1.0 was %s' % scale)

    def transform(self, xyz):
        x, y, z = [self._check_and_adjust(value) for value in xyz]
        x = self._transform(x)
        y = self._transform(y)
        return [x, y]

    def set_scale(self, new_scale):
        self._scale = new_scale

    def _check_and_adjust(self, value):
        if value > 1.0:
            value = 1.0
            logger.info("Adjusting Values")
        if value < 0.0:
            value = 0.0
            logger.info("Adjusting Values")
        return value

    def _transform(self, axis):
        return ((axis - 0.5) * self._scale) + 0.5


class HomogenousTransformer(Transformer):
    def __init__(self, scale, upper_height, lower_points, upper_points):
        self._lock = threading.Lock()
        self._scale = scale
        self._upper_height = upper_height

        lower_points = self._sort_points(lower_points)
        upper_points = self._sort_points(upper_points)

        deflection_scale = (
            (upper_points[0][0][0] - upper_points[2][0][0]) / (lower_points[0][0][0] - lower_points[2][0][0]),
            (upper_points[0][0][1] - upper_points[2][0][1]) / (lower_points[0][0][1] - lower_points[2][0][1])
            )

        self._lower_points = lower_points
        self._upper_points = [(self._scale_point(deflection, deflection_scale), distance) for (deflection, distance) in lower_points]

        self._get_transforms()
        self._cache = {}

    def _scale_point(self, point, scale):
        x, y = point
        dx = x * 2.0 - 1.0
        dy = y * 2.0 - 1.0
        rx = dx * scale[0]
        ry = dy * scale[1]
        tx = (rx + 1.0) / 2.0
        ty = (ry + 1.0) / 2.0
        return (tx, ty)

    def _sort_points(self, points):
        print points.items()
        distances = [distance for (deflection, distance) in points.items()]
        normals = [(int(x / abs(x)), int(y / abs(y))) for (x, y) in distances]
        print(normals)
        return [
            points.items()[normals.index(( 1,  1))],
            points.items()[normals.index(( 1, -1))],
            points.items()[normals.index((-1, -1))],
            points.items()[normals.index((-1,  1))],
            ]


    def _get_transforms(self):
        self._lock.acquire()
        try:
            self._lower_transform = self._get_transformation_matrix(self._lower_points)
            self._upper_transform = self._get_transformation_matrix(self._upper_points)
        finally:
            self._lock.release()

    def _get_transformation_matrix(self,mappings):
        mapping_matrix = self._build_matrix(mappings)
        b = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
        solved_matrix = np.linalg.solve(mapping_matrix,b)
        forwards = np.matrix([solved_matrix[0:3], solved_matrix[3:6], solved_matrix[6:9]])
        inverse = forwards.I
        return inverse

    def _build_matrix(self, points):
        builder = []
        index = 0
        for ((xp, yp), (xi, yi)) in points:
            augment = self._augment(index, xi / self._scale, yi / self._scale)
            builder.append([ xp, yp,  1,  0,  0,  0,  0,  0,  0] + augment[0])
            builder.append([  0,  0,  0, xp, yp,  1,  0,  0,  0] + augment[1])
            builder.append([  0,  0,  0,  0,  0,  0, xp, yp,  1] + augment[2])
            index += 1
        builder.append([  1,  1,  1,  1,  1,  1,  1,  1,  1,     0,   0,   0,   0])
        return np.array(builder)

    def _augment(self, index, xi, yi):
        augment = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        for i in range(0, 4):
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
            return self._cache[height]
        else:
            current = self._positional_transform(height)
            self._cache = {height: current}
            return current

    def _positional_transform(self, height):
        adjusted_height = height / self._upper_height
        return (adjusted_height * (self._upper_transform - self._lower_transform)) + self._lower_transform

    def transform(self, (x, y, z)):
        self._lock.acquire()
        try:
            realworld = np.array([[x], [y], [1]])
            computerland = self._transforms_for_height(z) * realworld
            [kx, ky, k] = [computerland.item(i, 0) for i in range(3)]
        finally:
            self._lock.release()
        x1, y1 = (kx/k, ky/k)
        if x1 >= 0.0 and x1 <= 1.0 and y1 >= 0.0 and y1 <= 1.0:
            return (x1, y1)
        else:
            logger.warning("Bounds of printer exceeded: %s,%s" % (x, y))
            adjusted_x = min(1.0, max(0.0, x1))
            adjusted_y = min(1.0, max(0.0, y1))
            return(adjusted_x, adjusted_y)

    def set_scale(self, new_scale):
        self._scale = new_scale
        self._get_transforms()
