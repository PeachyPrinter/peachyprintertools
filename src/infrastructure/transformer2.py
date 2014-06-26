import numpy as np
from math import *
from math import atan as arctan
import sys,os

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))

from domain.transformer import Transformer


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
        

# --------------------   Spikes Start Here  --------------------------------
from Tkinter import *
import threading

class MagicPrinter(object):
    def __init__(self, parent):
        print(str(parent))
        # Tk.__init__(self,None)
        self.width = 1600
        self.height = 980
        # self.laser = laser_control
        self.pp = PeachyPrinterFactory().new_peachy_printer()
        t = Toplevel(parent)
        self.canvas = Canvas(t, width=self.width, height=self.height,)
        self.canvas.create_line(0, self.height / 2, self.width ,self.height / 2 , fill="white",width=1)
        self.canvas.create_line(self.width / 2, 0, self.width / 2 ,self.height, fill="white",width=1)
        self.canvas.pack()
        self.last = [0.0,0.0,0.0]
        
    def process(self,from_xyz,to_xyz,speed):
        if self.last[2] != to_xyz[2]:
            self.canvas.delete("all")
            self.canvas.create_line(0, self.height / 2, self.width ,self.height / 2 , fill="white",width=1)
            self.canvas.create_line(self.width / 2, 0, self.width / 2 ,self.height, fill="white",width=1)
        # print('%s : %s' % (from_xyz, to_xyz))
        _from = self.pp.write(self.last[0],self.last[1],self.last[2],).tolist()[0]
        _to = self.pp.write(to_xyz[0],to_xyz[1],to_xyz[2]).tolist()[0]

        x1 = _from[0]  + self.width / 2
        y1 = _from[1]  + self.height / 2
        x2 = _to[0]  + self.width / 2
        y2 = _to[1]  + self.height / 2
        # print('x: %s -> %s, y: %s -> %s' % (x1,y1,x2,y2))
        self.canvas.create_line(x1, y1, x2, y2, fill="red",width=2)
        self.canvas.pack()
        self.last = to_xyz

import numpy.random as rdm
class PeachyPrinterFactory(object):
    def __init__(self):
        pass

    def wrong(self,alist, millimeters=0.25):
        for i in range(len(alist)-1):
            alist[i] += millimeters*rdm.normal(1)

        return np.matrix(alist)

    def new_peachy_printer(self):
        galvo1 = Galvo()
        galvo2 = Galvo()
        mirror1 = Mirror(np.matrix([15.0,18.0,-70,1.0]),np.matrix([-1.0,1.0,0.0,0.0]),np.matrix([0.0,0.0,1.0,0.0]),galvo1.pos)
        mirror2 = Mirror(np.matrix([15.0,18.0,-70,1.0]),np.matrix([0.0,-1.0,-1.0,0.0]),np.matrix([1.0,0.0,0.0,0.0]),galvo2.pos)
        laser = Laser(np.matrix([-3.0,17.0,-70.0,1.0]), np.matrix([0.0,17.0,-70.0,1.0]))
        return PeachyPrinter(mirror1, mirror2, laser)

    def new_peachy_printer_with_err(self):
        galvo1 = Galvo()
        galvo2 = Galvo()
        mirror1 = Mirror(self.wrong([15.0,18.0,-70,1.0]),self.wrong([-1.0,1.0,0.0,0.0]),self.wrong([0.0,0.0,1.0,0.0]),galvo1.pos)
        mirror2 = Mirror(self.wrong([15.0,23.0,-70,1.0]),self.wrong([0.0,-1.0,-1.0,0.0]),self.wrong([1.0,0.0,0.0,0.0]),galvo2.pos)
        laser = Laser(self.wrong([-3.0,17.0,-70.0,1.0]), self.wrong([0.0,17.0,-70.0,1.0]))
        return PeachyPrinter(mirror1, mirror2, laser)

class SpikeTransfomer(Transformer):


    def __init__(self, points):
        self.calibration_points = points
        self.monomial = [
        lambda x,y : x**3,  lambda x,y : x**2*y,   lambda x,y : x*y**2,   lambda x,y : y**3,
        lambda x,y : x**2,  lambda x,y : x*y,       lambda x,y : y**2,
        lambda x,y : x,  lambda x,y : y,
        lambda x,y : 1
    ]
        print(np.array(points))
        target_d1 = []
        target_d2 = []
        rows = []
        for ((x,y),(d1,d2)) in self.calibration_points:
            target_d1.append(d1)
            target_d2.append(d2)
            rows.append([ f(x,y) for f in self.monomial ])

        coeffecient_matrix = np.matrix(rows)
        target_vector_d1 = np.array(target_d1)
        target_vector_d2 = np.array(target_d2)

        coeffecient_vector_d1 = np.linalg.lstsq(coeffecient_matrix, target_vector_d1)[0]
        coeffecient_vector_d2 = np.linalg.lstsq(coeffecient_matrix, target_vector_d2)[0]

        print(coeffecient_vector_d1)


        transform_d1 = lambda x,y : sum( [ m * a(x,y) for (m,a) in zip(coeffecient_vector_d1, self.monomial)] )
        transform_d2 = lambda x,y : sum( [ m * a(x,y) for (m,a) in zip(coeffecient_vector_d2, self.monomial)] )

        self.transformit = lambda x,y : [ transform_d1(x,y), transform_d2(x,y) ]

    def transform(self,xyz):
        return self.transformit(*xyz[:2])


class Spike(Tk):
    def __init__(self):
        Tk.__init__(self,None)
        self.ppf = PeachyPrinterFactory()
        self.width = 1200
        self.height = 800
        self.master = Tk()
        self.canvas = Canvas(self.master, width=1600, height=800, background='black')
        self.canvas.pack()
        self.canvas.create_line(0, 400, 1600 ,400, fill="white",width=1)
        self.canvas.create_line(800, 0, 800 ,800, fill="white",width=1)
        self.pp = self.ppf.new_peachy_printer()
        self.transformer = self._get_transformer(self.pp)
        self.show_approximations()


    def _get_transformer(self, printer):
        deflection_points = [
        # [-0.3,0.2],[-0.1,0.2],[0.1,0.2],[0.3,0.2],
        # [-0.3,0.0],[-0.1,0.0],[0.1,0.0],[0.3,0.0],
        # [-0.3,-0.2],[-0.1,-0.2],[0.1,-0.2],[0.3,-0.2],
        [ 0.3, 0.3 ],[-0.3,  0.3],[ -0.3,  -0.3], [0.3,  -0.3],
        [ 0.1, 0.3 ],[-0.1,  0.3],[ -0.1,  -0.3], [0.1,  -0.3],
        [ 0.3, 0.1 ],[-0.3,  0.1],[ -0.3,  -0.1], [0.3,  -0.1],
        [ 0.1, 0.1 ],[-0.1,  0.1],[ -0.1,  -0.1], [0.1,  -0.1],
        ]

        deflection_points = [ [x * 2.0 ,y * 2.0] for (x,y) in deflection_points ]
        # deflection_points = [ [rdm.normal(1) *0.6,rdm.normal(1) * 0.6] for i in range(0,12) ]

        for point in deflection_points:
            self.canvas.create_line(self.xscale(point[0]),self.yscale(point[1]),self.xscale(point[0]) + 1,self.yscale(point[1]) + 1,fill="green", width=5)

        calibration_map = [(np.array(printer.write(point[0],point[1],-300))[0].tolist()[:2], point ) for point in deflection_points ]
        return SpikeTransfomer(calibration_map)

    def xscale(self,x):
        return (x * ((self.width - 10)  / 2)) + (self.width + 10) / 2 

    def yscale(self,y):
        return (y * ((self.height - 10)  / 2)) + (self.height +10) / 2

    def show_approximations(self):
        rangerx  = 6
        rangery  = 6
        xr = [x / (rangerx * 1.0) for x in range(-rangerx,rangerx + 1)]
        yr = [y / (rangery * 1.0) for y in range(-rangery,rangery + 1)]
        for x in xr:
            for y in yr:
                there = self.pp.write(x,y,-300).tolist()[0]
                self.canvas.create_line(self.xscale(x),         self.yscale(y),         self.xscale(x) + 1,         self.yscale(y) + 1,         fill="blue", width=2)
                back = self.transformer.transform(there)
                print('%s :=> %s' % (str((x,y)), back))
                self.canvas.create_line(self.xscale(back[0]),   self.yscale(back[1]),   self.xscale(back[0]) + 1,   self.yscale(back[1]) + 1,   fill="red", width=2)


from Tkinter import *
if __name__ == '__main__':
    app = Spike()
    app.mainloop()