import pyaudio
import time
import numpy
import math
import itertools
import os,sys
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))

from laser_control import AudioModulationLaserControl

class SpikeWriter(object):
    MAX_S16 = (math.pow(2, 15) - 1.0) * 1.0

    def __init__(self):
        pa = pyaudio.PyAudio()
        self.outstream = pa.open(format=pa.get_format_from_width(2, unsigned=False),
                 channels=2,
                 rate=48000,
                 output=True,
                 frames_per_buffer=int(48000/8))
        self.outstream.start_stream()

    def write(self,inputstream):
        for values in inputstream:
            frameset = self.to_frame(values)
            da_buffer = self.outstream.get_write_available()
            # print(da_buffer)
            while da_buffer < len(frameset):
                time.sleep(0.1)
                da_buffer = self.outstream.get_write_available()
            self.outstream.write(frameset)

    def to_frame(self, values):
        # print(values)
        values = numpy.rint( values * self.MAX_S16)
        mod = values.astype(numpy.dtype('<i2'))
        return mod.tostring()

    def close(self):
        self.outstream.stop_stream()
        self.outstream.close()

class Goer(object):
    def __init__(self):
        self.writer = SpikeWriter()
        self.modulator = AudioModulationLaserControl(48000, 12000, 8000)

    def line(self):
        maxi = int(math.pi * 24000)
        pre = [ (math.cos(n * 1.0 / 12000.0) + 1.0) / 2.0 for n in range(0,maxi) ]
        for n in itertools.cycle(range(0, maxi)):
            # print(pre[n])
            yield (pre[n], pre[n])
            yield 

    def go(self):
        ln = self.line()
        self.modulator.set_laser_on()
        data = self.modulator.modulate(ln)
        self.writer.write(data)
        self.modulator.set_laser_off()
        self.writer.close()

if __name__ == '__main__':
    g = Goer()
    g.go()

