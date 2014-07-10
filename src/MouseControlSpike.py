from Tkinter import *
from infrastructure.audio import *
from infrastructure.laser_control import *
import numpy


class Goer(Tk):
    def __init__(self):
        Tk.__init__(self,None)
        sampling_rate = 48000
        self.bind("<Motion>", self.showxy)
        self.bind("<Button-1>", self.clickxy)
        self.bind("<Key>", self.key)
        self.size = (1000,1000)
        self.geometry("%sx%s" % self.size)

        self.on_frequency = 12000
        self.off_frequency = 4000
        offset = [0,0]
        self.xy = (0.0,0.0)

        self.aw = AudioWriter(48000,'16 bit', 64)
        self.am = AudioModulationLaserControl(sampling_rate, self.on_frequency, self.off_frequency, offset)
        self.am.set_laser_on()

        self.after(100, self.write)

        Label(self,text="Q to quit").grid(column = 1, row = 1)
        self.grid()
        self.data = StringVar()
        self.data.set("")
        Label(self, textvariable = self.data).grid(column = 1, row = 2)
        
    def write(self):
        lst = []
        for i in range(0,48000 / self.on_frequency * 64 ):
            lst.append(self.xy)
        mod = self.am.modulate(numpy.array(lst))
        self.aw.write_chunk(mod)
        self.after(1000 / 128, self.write)

    def showxy(self, event):
        xm = event.x
        ym = event.y
        self.xy = (ym / float(self.size[1]),  xm / float(self.size[0]))
        str1 = "mouse at x=%d  y=%d" % (xm, ym)
        self.title(str1)

    def clickxy(self, event):
        self.data.set(self.data.get() + "%s,%s\n" % self.xy)
        print (self.xy)

    def key(self,event):
        print "pressed", repr(event.char)
        if event.char.lower() == 'q':
            self.aw.close()
            exit(0)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    app = Goer()
    app.mainloop()

