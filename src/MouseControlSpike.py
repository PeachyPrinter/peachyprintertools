from Tkinter import *
from infrastructure.audio import *
from infrastructure.laser_control import *
import numpy

# root = tk.Tk()


class Goer(Tk):
    def __init__(self):
        Tk.__init__(self,None)
        sampling_rate = 48000
        self.bind("<Motion>", self.showxy)
        self.on_frequency = 12000
        self.off_frequency = 4000
        offset = [0,0]
        self.xy = (0.0,0.0)
        self.size = (1000,1000)
        self.geometry("%sx%s" % self.size)
        self.aw = AudioWriter(48000,'16 bit', 64)
        self.am = AudioModulationLaserControl(sampling_rate, self.on_frequency, self.off_frequency, offset)
        self.am.set_laser_on()
        self.after(100, self.write)
        
    def write(self):
        lst = []
        for i in range(0,48000 / self.on_frequency * 32 ):
            lst.append(self.xy)
        mod = self.am.modulate(numpy.array(lst))
        self.aw.write_chunk(mod)
        self.after(1000 / 64, self.write)

    def showxy(self, event):
        xm = event.x
        ym = event.y
        # print(xm)
        # print(ym)
        self.xy = (ym / float(self.size[1]),  1.0 - xm / float(self.size[0]))
        # print(self.xy)
        str1 = "mouse at x=%d  y=%d" % (xm, ym)
        self.title(str1)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    app = Goer()
    app.mainloop()

