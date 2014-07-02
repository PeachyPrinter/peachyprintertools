import numpy as np
import numpy.random as rdm
from math import *
import sys,os
import time
from Tkinter import *

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
from infrastructure.simulator import *
from domain.transformer import Transformer
from infrastructure.point_transformer import SquareTransform
np.seterr(all='raise')


class SpikeTransfomer(Transformer):
    def __init__(self, points):

        self._scale = 1.0
        self.squarer = SquareTransform([ (deflect,real) for (real, deflect) in points[:4]] )

        self.monomial = [
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
        
        self.xbend, self.ybend, self.coeffecient_vector_d1, self.coeffecient_vector_d2 = self._get_best_bends(points,self.monomial)

        # transform_d2 = lambda x,y : sum( [ m * a(self._x_de_pincushion(self._x_fit(x,y),xbend),self._y_de_pincushion(self._y_fit(x,y),ybend) ) for (m,a) in zip(coeffecient_vector_d2, monomial)] )

        self.transformit = lambda x,y : self.transforma(x,y)

    def transforma(self,x,y): 
            fit_xy = self.squarer.fit(x,y)
            pin_x = self._x_de_pincushion(fit_xy[0],self.xbend)
            pin_y = self._y_de_pincushion(fit_xy[1],self.ybend)
            transform_x = sum( [ m * a(pin_x,pin_y) for (m,a) in zip(self.coeffecient_vector_d1, self.monomial)] )
            transform_y = sum( [ m * a(pin_x,pin_y) for (m,a) in zip(self.coeffecient_vector_d2, self.monomial)] )
            return [ transform_x,transform_y ]

    def _get_best_bends(self,points,monomial):
        best_bend = (0, 0, 0 , 0,99999999999999999999999999999999999.0)
        for y in range(30, 60):
            for x in range(30,60):
                xbend = (x * 1.0) / 40.0
                ybend = (y * 1.0) / 40.0
                (coeffecient_vector_d1, error_d1), (coeffecient_vector_d2 , error_d2)= self._get_co_vectors(points, monomial,xbend,ybend )
                error = error_d1 + error_d2
                if best_bend[4] > error:
                    best_bend = (xbend, ybend, coeffecient_vector_d1,coeffecient_vector_d2, error)
        print("Best Bends: %s,%s" % (best_bend[0],best_bend[1]))
        return best_bend[:4]

    def _get_co_vectors(self, points, monomial, xbend,ybend):
        target_d1 = []
        target_d2 = []
        rows = []
        for ((x,y),(d1,d2)) in points:
            target_d1.append(d1)
            target_d2.append(d2)
            fit_xy = self.squarer.fit(x,y)
            pin_x = self._x_de_pincushion(fit_xy[0],xbend)
            pin_y = self._y_de_pincushion(fit_xy[1],ybend)
            rows.append([ f(pin_x,pin_y) for f in monomial ])

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
        
        self.deflection_points = [
            [ 1.0, 1.0],[-1.0, 1.0],[ 1.0,-1.0],[-1.0, -1.0],
            [ 0.0, 1.0 ],[ 0.0, -1.0 ],[1.0,0.0],[-1.0,0.0],
            [ 0.8, 0.8],[-0.8, 0.8],[ 0.8,-0.8],[-0.8, -0.8],
            [ 0.0, 0.8],[ 0.0, -0.8 ],[0.8,0.0],[-0.8,0.0],
            # [ 0.3, 0.3],[-0.3, 0.3],[ 0.3,-0.3],[-0.3, -0.3],
            # [ 0.0, 0.3],[ 0.0, -0.3 ],[0.3,0.0],[-0.3,0.0],
            # [0.0,0.0],
        ]

        self.pp = self.ppf.new_peachy_printer()
        # for i in range(0,100):
        # self.pp = self.ppf.new_peachy_printer_with_err()
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

    def test_points(self,x_range,y_range):
        for x in x_range:
            for y in y_range:
                yield self.pp.write(x,y,-300).tolist()[0]

    def show_approximations(self):
        bigness = 2
        start = time.time()
        rangerx  = 20
        rangery  = 20
        xr = [x / (rangerx * 1.0)for x  in range(-rangerx,rangerx + 1)]
        yr = [y / (rangery * 1.0) for y in range(-rangery,rangery + 1)]
        points = list(self.test_points(xr,yr))

        for there in points:
            self.canvas.create_line(
                    there[0] + (self.width - 10)  / 2,
                    there[1] + (self.height - 10)  / 2,
                    there[0] + bigness +(self.width - 10)  / 2,
                    there[1] + bigness +(self.height - 10)  / 2,
                    fill="green", width=bigness)

        start = time.time()
        backs = [ self.transformer.transform(there) for there in points ]
        total = time.time() - start

        print("processed %s points in %s seconds: avg: %s points per second" % (len(backs), total, (len(backs) / total)))
        for back in backs:
                there_again = self.pp.write(back[0],back[1],-300).tolist()[0]
                self.canvas.create_line(
                    there_again[0] + (self.width - 10)  / 2,
                    there_again[1] + (self.height - 10)  / 2,
                    there_again[0] + bigness +(self.width - 10)  / 2,
                    there_again[1] + bigness +(self.height - 10)  / 2,
                    fill="yellow", width=bigness)

        # for point in [ self.pp.write(point[0],point[1],-300)[0].tolist()[0] for point in self.deflection_points ]:
        #     self.canvas.create_line(
        #             point[0] + (self.width - 10)  / 2,
        #             point[1] + (self.height - 10)  / 2,
        #             point[0] + bigness +(self.width - 10)  / 2,
        #             point[1] + bigness +(self.height - 10)  / 2,
        #             fill="red", width=bigness)



if __name__ == '__main__':
    app = Spike()
    app.mainloop()