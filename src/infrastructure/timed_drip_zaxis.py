import threading
import time
import math
from domain.zaxis import ZAxis
import logging

class TimedDripZAxis(ZAxis, threading.Thread):
    def __init__(self, 
        drips_per_mm, 
        call_back = None, 
        calls_back_per_second = 15, 
        drips_per_second = 1.0
        ):
        threading.Thread.__init__(self)
        self._drips_per_mm = drips_per_mm
        self._drips_per_second = drips_per_second
        self.shutdown = False
        self.running = True
        self.start_time = 0
        self._call_back = call_back
        self._time_to_wait = 1.0 / (calls_back_per_second * 1.0)
        self._drips_history = 0.0
        self._height_history = 0.0

    def set_call_back(self, call_back):
        self._call_back = call_back

    def set_drips_per_second(self, dps):
        current_time = time.time() - self.start_time
        drips = current_time * self._drips_per_second
        self._drips_history = self._drips_history + drips
        self._height_history = self._height_history + (drips / self._drips_per_mm)
        self.start_time = time.time()
        self._drips_per_second = dps

    def get_drips_per_second(self):
        return self._drips_per_second

    def set_drips_per_mm(self, drips_per_mm):
        self._drips_per_mm = drips_per_mm

    def current_z_location_mm(self):
        current_time = time.time() - self.start_time
        height = (current_time * self._drips_per_second) / self._drips_per_mm
        return self._height_history + height

    def update_data(self):
        if self._call_back:
            current_time = time.time() - self.start_time
            drips =  current_time * self._drips_per_second
            height = drips / self._drips_per_mm
            self._call_back(math.ceil(self._drips_history + drips),self._height_history + height,self._drips_per_second)

    def run(self):
        self.start_time = time.time()
        while self.running:
            start = time.time()
            self.update_data()
            delta = time.time() - start
            time.sleep(max(0, self._time_to_wait - delta))
        self.shutdown = True

    def move_to(self, height_mm):
        logging.info('Ignoring move to %s' % height_mm)

    def stop(self):
        self.running = False
        while not self.shutdown:
            time.sleep(0.1)