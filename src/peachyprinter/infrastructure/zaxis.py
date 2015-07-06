import time
import logging
logger = logging.getLogger('peachy')
from math import ceil
from peachyprinter.domain.zaxis import ZAxis
from peachyprinter.infrastructure.messages import DripRecordedMessage, SetDripCountMessage, MoveToDripCountMessage


class SerialDripZAxis(ZAxis):
    def __init__(self, communicator, drips_per_mm, starting_height, drip_call_back=None,):
        super(SerialDripZAxis, self).__init__(starting_height)
        self._communicator = communicator
        self._drips_per_mm = drips_per_mm
        self._drips = 0
        self._drip_call_back = drip_call_back
        self._communicator.send(SetDripCountMessage(0))
        self._communicator.register_handler(DripRecordedMessage, self.drip_reported_handler)
        self._drip_history = []
        self._drips_in_average = 10

    def drip_reported_handler(self, drip_reported):

        drips_added = drip_reported.drips - self._drips
        self._drips = drip_reported.drips
        self._append_drip(drips_added)
        if self._drip_call_back:
            self._drip_call_back(self._drips, self.current_z_location_mm(), self.average_drips, self.drip_history)

    def _append_drip(self, drips_count):
        for i in range(0, drips_count):
            self._drip_history.append(time.time())
        if len(self._drip_history) > 100:
            self._drip_history = self._drip_history[-100:]

    @property
    def average_drips(self):
        if len(self._drip_history) >= self._drips_in_average:
            seconds = (self._drip_history[-1] - self._drip_history[-10])
            if seconds > 0:
                return 10.0 / seconds
        return 0.0

    @property
    def drip_history(self):
        return list(self._drip_history)

    def set_call_back(self, call_back):
        self._drip_call_back = call_back

    def reset(self):
        self._communicator.send(SetDripCountMessage(0))
        self._drips = 0
        self._drip_history = []

    def current_z_location_mm(self):
        return self._starting_height + (self._drips * 1.0 / self._drips_per_mm)

    def set_drips_per_mm(self, drips_per_mm):
        self._drips_per_mm = drips_per_mm

    def move_to(self, height_mm):
        wanted_drips = int(ceil(height_mm / self._drips_per_mm))
        self._communicator.send(MoveToDripCountMessage(wanted_drips))

    def close(self):
        logger.info("SerialDripZAxis shutdown successfully")
