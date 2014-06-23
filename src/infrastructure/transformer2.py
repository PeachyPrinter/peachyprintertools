import numpy as np
np.seterr(all='raise')

class Laser(object):
    def __init__(self,laser_posisition, point_at):
        self._laser_posisition=laser_posisition
        self._point_at=point_at

    def _current_y_slope(self):
        return  (self._laser_posisition[0,1] - self._point_at[0,1]) / (self._laser_posisition[0,2] - self._point_at[0,2]) 

    def _current_x_slope(self):
        return (self._laser_posisition[0,0] - self._point_at[0,0]) /(self._laser_posisition[0,2] - self._point_at[0,2])

    def fire(self,z):
        x =  self._laser_posisition[0,0] - (self._laser_posisition[0,2]  - z) * self._current_x_slope()
        y =  self._laser_posisition[0,1] - (self._laser_posisition[0,2]  - z) * self._current_y_slope()

        return np.matrix([x,y,z,1])


class Mirror(object):
    def __init__(self, base_point, normal):
        self._base_translation = np.append(np.matrix([[1.0, 0.0, 0.0, 0.0],[0.0,1.0,0.0, 0.0],[0.0,0.0,1.0, 0.0]]),base_point,0)
        self._normal_unit = normal

    def _get_reflection(self):
        return np.identity(4) - 2*np.outer(self._normal_unit,self._normal_unit)

    def reflect(self, point):
        base_point = point * np.linalg.inv(self._base_translation)
        base_reflection = (base_point * self._get_reflection())
        return (base_reflection * self._base_translation)

