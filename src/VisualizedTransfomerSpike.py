import numpy as np
import numpy.random as rdm
from math import *
import sys,os
import time
from Tkinter import *
import logging

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
from infrastructure.simulator import *
from infrastructure.point_transformer import *
np.seterr(all='raise')

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
            [ 0.3, 0.3],[-0.3, 0.3],[ 0.3,-0.3],[-0.3, -0.3],
            [ 0.0, 0.3],[ 0.0, -0.3 ],[0.3,0.0],[-0.3,0.0],
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
           calibration_map.append((point, np.array(printer.write(point[0],point[1],z))[0].tolist()[:2] ))

        return PointTransformer(calibration_map)

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
        backs = [ self.transformer.transform((x,y,z)) for (x,y,z,w) in points ]
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

        for point in [ self.pp.write(point[0],point[1],-300)[0].tolist()[0] for point in self.deflection_points ]:
            self.canvas.create_line(
                    point[0] + (self.width - 10)  / 2,
                    point[1] + (self.height - 10)  / 2,
                    point[0] + bigness +(self.width - 10)  / 2,
                    point[1] + bigness +(self.height - 10)  / 2,
                    fill="red", width=bigness)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    app = Spike()
    app.mainloop()