import numpy as np
import numpy.random as rdm
from math import *
import sys,os
import time
from Tkinter import *

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
from infrastructure.simulator import *
from domain.transformer import Transformer

np.seterr(all='raise')

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

class SpikeTransfomer(Transformer):
    def __init__(self, points):

        self._scale = 1.0
        self.MP = self._get_transform(points)
        print('matrix: %s' % self.MP)

        monomial = [
            lambda x,y : x**3,
            lambda x,y : x**2*y,
            lambda x,y : x*y**2,
            lambda x,y : y**3,
            lambda x,y : x**2,
            lambda x,y : x*y,
            lambda x,y : y**2,
            lambda x,y : x,
            lambda x,y : y,
            lambda x,y : 1
        ]
        
        xbend, ybend, coeffecient_vector_d1, coeffecient_vector_d2 = self._get_best_bends(points,monomial)

        transform_d1 = lambda x,y : sum( [ m * a(self._x_de_pincushion(self._x_fit(x,y),xbend),self._y_de_pincushion(self._y_fit(x,y),ybend) ) for (m,a) in zip(coeffecient_vector_d1, monomial)] )
        transform_d2 = lambda x,y : sum( [ m * a(self._x_de_pincushion(self._x_fit(x,y),xbend),self._y_de_pincushion(self._y_fit(x,y),ybend) ) for (m,a) in zip(coeffecient_vector_d2, monomial)] )

        self.transformit = lambda x,y : [ transform_d1(x,y), transform_d2(x,y) ]
        
        
    def _get_transform(self, points):
        return self._get_transformation_matrix(points)

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
        print("IN: %s" % points[:4])
        for ((xi,yi),(xp,yp)) in points[:4]:
            augment = self._augment(index,xi / self._scale, yi / 0.69)

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

    def no1_transform(self,(x,y)):
        realworld = np.array([[x], [y], [1]])
        computerland = self.MP * realworld
        [kx, ky, k] = [computerland.item(i, 0) for i in range(3)]
        x1,y1 = (kx/k, ky/k)
        return (x1, y1)
        if x1 >= -1.0 and x1 <= 1.0 and y1>= -1.0 and y1 <=1.0:
            return (x1, y1)
        else:
            print("Boom: %s,%s ::+> %s,%s" % (x,y,x1, y1))

    def _x_fit(self,x,y):
        return self.no1_transform((x,y))[0]

    def _y_fit(self,x,y):
        return self.no1_transform((x,y))[1]

    def _get_best_bends(self,points,monomial):
        best_bend = (0, 0, 0 , 0,99999999999999999999999999999999999.0)
        for y in range(-200, 200, 20):
            for x in range(-200,200,20):
                xbend = x / 100.0
                ybend = y / 100.0
                (coeffecient_vector_d1, error_d1), (coeffecient_vector_d2 , error_d2)= self._get_co_vectors(points, monomial,xbend,ybend )
                error = error_d1 + error_d2
                if best_bend[4] > error:
                    best_bend = (x /  100.0, y / 100.0, coeffecient_vector_d1,coeffecient_vector_d2, error)
        print("Best Bends: %s,%s" % (best_bend[0],best_bend[1]))
        return best_bend[:4]

    def _get_co_vectors(self, points, monomial, xbend,ybend):
        target_d1 = []
        target_d2 = []
        rows = []
        for ((x,y),(d1,d2)) in points:
            target_d1.append(d1)
            target_d2.append(d2)
            rows.append([ f(self._x_de_pincushion(self._x_fit(x,y),xbend),self._y_de_pincushion(self._y_fit(x,y),ybend)) for f in monomial ])

        coeffecient_matrix = np.matrix(rows)
        target_vector_d1 = np.array(target_d1)
        target_vector_d2 = np.array(target_d2)

        results_d1 = np.linalg.lstsq(coeffecient_matrix, target_vector_d1)[:2]
        results_d2 = np.linalg.lstsq(coeffecient_matrix, target_vector_d2)[:2]
        return (results_d1, results_d2)

    def _x_de_pincushion(self,x,bend):
        size = 0.3
        scale = 3.0*size
        return bend * (scale*atan((x)/scale)) + (1.0-bend) * x 

    def _y_de_pincushion(self,y,bend):
        size = 0.3
        scale = 3.0*size
        return bend * (scale*atan((y)/scale)) + (1.0-bend) * y

    def transform(self,xyz):
        return self.transformit(*xyz[:2])


class Spike(Tk):
    def __init__(self):
        Tk.__init__(self,None)
        self.ppf = PeachyPrinterFactory()
        self.width = 1000
        self.height = 1000
        self.canvas = Canvas(self, width=self.width, height=self.height, background='black')
        self.canvas.pack()
        for i in range(-self.width / 5,self.width / 5):
            self.canvas.create_line(0, self.height/2 + 10*i, self.width ,self.height / 2 + 10*i, fill="#333",width=1)
            self.canvas.create_line(self.width / 2+ 10*i, 0, self.width / 2 + 10*i,self.height, fill="#333",width=1)    
        self.canvas.create_line(0, self.height/2, self.width ,self.height / 2, fill="white",width=1)
        self.canvas.create_line(self.width / 2, 0, self.width / 2 ,self.height, fill="white",width=1)
        self.pp = self.ppf.new_peachy_printer()
        self.pp = self.ppf.new_peachy_printer_with_err()
        self.deflection_points = [
            [ 1.0, 1.0],[-1.0, 1.0],[ 1.0,-1.0],[-1.0, -1.0],
            [ 0.0, 1.0 ],[ 0.0, -1.0 ],[1.0,0.0],[-1.0,0.0],
            [ 0.8, 0.8],[-0.8, 0.8],[ 0.8,-0.8],[-0.8, -0.8],
            [ 0.0, 0.8],[ 0.0, -0.8 ],[0.8,0.0],[-0.8,0.0],
            # [0.0,0.0],
        ]
        self.transformer = self._get_transformer(self.pp)
        self.show_approximations()

    def _get_transformer(self, printer):
        z = -300
        calibration_map = []
        for point in self.deflection_points:
           calibration_map.append((np.array(printer.write(point[0],point[1],z))[0].tolist()[:2], point ))

        return SpikeTransfomer(calibration_map)

    def xscale(self,x):
        return x * (self.width / 3) + self.width  / 2 

    def yscale(self,y):
        return y * (self.height  / 3) + self.height  / 2

    def show_approximations(self):
        bigness = 3
        start = time.time()
        rangerx  = 20
        rangery  = 20
        xr = [x / (rangerx * 1.0)for x  in range(-rangerx,rangerx + 1)]
        yr = [y / (rangery * 1.0) for y in range(-rangery,rangery + 1)]
        for x in xr:
            for y in yr:
                there = self.pp.write(x,y,-300).tolist()[0]
                # self.canvas.create_line(self.xscale(x),         self.yscale(y),         self.xscale(x) + bigness,         self.yscale(y) + bigness,         fill="blue", width=bigness)
                back = self.transformer.transform(there)
                there_again = self.pp.write(back[0],back[1],-300).tolist()[0]
                self.canvas.create_line(
                    there[0] + (self.width - 10)  / 2,
                    there[1] + (self.height - 10)  / 2,
                    there[0] + bigness +(self.width - 10)  / 2,
                    there[1] + bigness +(self.height - 10)  / 2,
                    fill="green", width=bigness)
                self.canvas.create_line(
                    there_again[0] + (self.width - 10)  / 2,
                    there_again[1] + (self.height - 10)  / 2,
                    there_again[0] + bigness +(self.width - 10)  / 2,
                    there_again[1] + bigness +(self.height - 10)  / 2,
                    fill="yellow", width=bigness)
        for point in [ self.pp.write(point[0],point[1],-300)[0].tolist()[0] for point in self.deflection_points ]:
            self.canvas.create_line(
                    point[0] + (self.width - 10)  / 2,
                    point[1] + (self.height - 10)  / 2,
                    point[0] + bigness +(self.width - 10)  / 2,
                    point[1] + bigness +(self.height - 10)  / 2,
                    fill="red", width=bigness)

        print("took: %s" % (time.time()- start))


if __name__ == '__main__':
    app = Spike()
    app.mainloop()