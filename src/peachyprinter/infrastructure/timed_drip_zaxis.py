import threading
import time
import math
from peachyprinter.domain.zaxis import ZAxis
import logging
logger = logging.getLogger('peachy')


class TimedDripZAxis(ZAxis, threading.Thread):
    def __init__(self,
                 drips_per_mm,
                 starting_height,
                 call_back=None,
                 calls_back_per_second=15,
                 drips_per_second=1.0
                 ):
        ZAxis.__init__(self, starting_height)
        threading.Thread.__init__(self)

        self._drips_per_mm = drips_per_mm
        self._drips_per_second = drips_per_second
        self.shutdown = False
        self.running = False
        self.start_time = 0
        self._call_back = call_back
        self._time_to_wait = 1.0 / (calls_back_per_second * 1.0)
        self._drips_history = 0.0
        self._height_history = self._starting_height

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
        if self.running:
            current_time = time.time() - self.start_time
            height = (current_time * self._drips_per_second) / self._drips_per_mm
            return self._height_history + height
        else:
            return self._height_history

    def update_data(self):
        if self._call_back:
            current_time = time.time() - self.start_time
            drips = current_time * self._drips_per_second
            height = drips / self._drips_per_mm
            self._call_back(math.ceil(self._drips_history + drips), self._height_history + height, self._drips_per_second)

    def start(self):
        threading.Thread.start(self)
        while self.start_time == 0:
            time.sleep(0.1)

    def run(self):
        self.running = True
        self.start_time = time.time()
        while self.running:
            start = time.time()
            self.update_data()
            delta = time.time() - start
            time.sleep(max(0, self._time_to_wait - delta))
        self.shutdown = True

    def move_to(self, height_mm):
        logger.info('Ignoring move to %s' % height_mm)

    def close(self):
        if self.running:
            self.running = False
            while not self.shutdown:
                time.sleep(0.1)
        self.join()


class PhotoZAxis(ZAxis):
    def __init__(self, starting_height, height_change_delay=1.0, call_back=None):
        super(PhotoZAxis, self).__init__(starting_height)
        self._current_height = self._starting_height
        self._next_height = None
        self._time_of_change = None
        self._next_change = 0
        self._height_change_delay = height_change_delay
        self._call_back = call_back

    def start(self):
        self.move_to(0)

    def close(self):
        pass

    def current_z_location_mm(self):
        if (self._next_height is not None):
            if (self._time_of_change and self._time_of_change <= time.time()):
                self._current_height = self._next_height
                self._next_height = None
                self._time_of_change = None
                self.callback()
        return self._current_height

    def set_call_back(self, call_back):
        self._call_back = call_back

    def callback(self):
        if self._call_back:
            self._call_back(0, self._current_height, 0)

    def move_to(self, height_mm):
        self._time_of_change = time.time() + self._height_change_delay
        self._next_height = height_mm
