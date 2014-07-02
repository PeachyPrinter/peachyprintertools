import numpy as np
from math import *
import sys,os
import time

np.seterr(all='raise')

class Laser(object):
    def __init__(self,position, point_at):
        self.position=position
        self.point_at=point_at

    def _current_y_slope(self):
        return  (self.position[0,1] - self.point_at[0,1]) / (self.position[0,2] - self.point_at[0,2]) 

    def _current_x_slope(self):
        return (self.position[0,0] - self.point_at[0,0]) /(self.position[0,2] - self.point_at[0,2])

    def fire(self,z):
        x =  self.position[0,0] - (self.position[0,2]  - z) * self._current_x_slope()
        y =  self.position[0,1] - (self.position[0,2]  - z) * self._current_y_slope()
        return np.matrix([x,y,z,1])

class Mirror(object):
    def __init__(self, base_point, resting_normal, axis, galvo_pos):
        #Although is is possible that the axis is not perpendicular to to normal NO!
        self._base_translation = np.append(np.matrix([[1.0, 0.0, 0.0, 0.0],[0.0,1.0,0.0, 0.0],[0.0,0.0,1.0, 0.0]]),base_point,0)
        self._resting_unit_normal = self._unit_vector(resting_normal)
        self._unit_axis = self._unit_vector(axis)
        self._galvo_pos = galvo_pos
    
    def _unit_vector(self,vector):
            return vector / np.linalg.norm(vector)

    def _get_reflection(self):
        return np.identity(4) - 2*np.outer(self._resting_unit_normal,self._resting_unit_normal)

    def _get_rotation_matrix(self, theta, axis):
        x,y,z,w = axis.tolist()[0]
        cos_theta = cos(theta)
        sin_theta = sin(theta)
        return np.matrix([
            [x*x*(1-cos_theta)+cos_theta,      y*x*(1-cos_theta)-z*sin_theta,    z*x*(1-cos_theta)+y*sin_theta,  0],
            [x*y*(1-cos_theta)+z*sin_theta,    y*y*(1-cos_theta)+cos_theta,      z*y*(1-cos_theta)-x*sin_theta,  0],
            [x*z*(1-cos_theta)-y*sin_theta,    y*z*(1-cos_theta)+x*sin_theta,    z*z*(1-cos_theta)+cos_theta,    0],
            [0,                0,                0,              1]
            ])

    def reflect(self, point, signal):
        angle = self._galvo_pos(signal)
        rotation_matrix = self._get_rotation_matrix(angle,self._unit_axis)

        base_point = point * np.linalg.inv(self._base_translation)* np.linalg.inv(rotation_matrix)
        base_reflection = (base_point * self._get_reflection())
        return (base_reflection * rotation_matrix * self._base_translation)

class Galvo(object):
    def __init__(self):
        pass

    def pos(self,signal):
        return signal * pi / 8

class PeachyPrinter(object):
    def __init__(self,mirror1,mirror2,real_laser):
        self._mirror1 = mirror1
        self._mirror2 = mirror2
        self._laser = real_laser

    def write(self,deflection1, deflection2, real_height_z):
        position_1 = self._mirror1.reflect(self._laser.position, deflection1)
        look_at_1 = self._mirror1.reflect(self._laser.point_at,deflection1)
        phantom_laser1 = Laser(position_1,look_at_1)

        position_2 = self._mirror2.reflect(phantom_laser1.position, deflection2)
        look_at_2 = self._mirror2.reflect(phantom_laser1.point_at, deflection2)
        phantom_laser2 = Laser(position_2,look_at_2)

        return phantom_laser2.fire(real_height_z)

class PeachyPrinterFactory(object):
    def __init__(self):
        pass

    def wrong(self,alist, millimeters=0.05):
        for i in range(len(alist)-1):
            alist[i] += millimeters*rdm.normal(1)

        return np.matrix(alist)

    def new_peachy_printer(self):
        galvo1 = Galvo()
        galvo2 = Galvo()
        mirror1 = Mirror(np.matrix([15.0,18.0,-70,1.0]),np.matrix([-1.0,1.0,0.0,0.0]),np.matrix([0.0,0.0,1.0,0.0]),galvo1.pos)
        mirror2 = Mirror(np.matrix([15.0,23.0,-70,1.0]),np.matrix([0.0,-1.0,-1.0,0.0]),np.matrix([1.0,0.0,0.0,0.0]),galvo2.pos)
        laser = Laser(np.matrix([-3.0,18.0,-70.0,1.0]), np.matrix([0.0,18.0,-70.0,1.0]))
        return PeachyPrinter(mirror1, mirror2, laser)

    def new_peachy_printer_with_err(self):
        galvo1 = Galvo()
        galvo2 = Galvo()
        mirror1 = Mirror(self.wrong([15.0,18.0,-70,1.0]),self.wrong([-1.0,1.0,0.0,0.0]),self.wrong([0.0,0.0,1.0,0.0]),galvo1.pos)
        mirror2 = Mirror(self.wrong([15.0,23.0,-70,1.0]),self.wrong([0.0,-1.0,-1.0,0.0]),self.wrong([1.0,0.0,0.0,0.0]),galvo2.pos)
        laser = Laser(self.wrong([-3.0,17.0,-70.0,1.0]), self.wrong([0.0,17.0,-70.0,1.0]))
        return PeachyPrinter(mirror1, mirror2, laser)