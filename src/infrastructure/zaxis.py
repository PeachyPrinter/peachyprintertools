import time
import logging
from domain.zaxis import ZAxis
from infrastructure.messages import DripRecordedMessage


class SerialDripZAxis(ZAxis):
    def __init__(self, communicator, drips_per_mm, starting_height, drip_call_back=None,):
        super(SerialDripZAxis, self).__init__(starting_height)
        self._drips_per_mm = drips_per_mm
        self._drips = 0
        self._drip_call_back = drip_call_back
        communicator.register_handler(DripRecordedMessage, self.drip_reported_handler)
        self._drip_history = []
        self._drips_in_average = 10

    def drip_reported_handler(self, drip_reported):
        self._drips += 1
        self._append_drip()
        if self._drip_call_back:
            self._drip_call_back(self._drips, self.current_z_location_mm(), self.average_drips, self.drip_history)

    def _append_drip(self):
        self._drip_history.append(time.time())
        if len(self._drip_history) > 100:
            self._drip_history = self._drip_history[-100:]

    @property
    def average_drips(self):
        if len(self._drip_history) >= self._drips_in_average:
            return (self._drip_history[-1] - self._drip_history[-10]) / 10.0
        else:
            return 0.0

    @property
    def drip_history(self):
        return list(self._drip_history)

    def set_call_back(self, call_back):
        self._drip_call_back = call_back

    def reset(self):
        self._drips = 0

    def current_z_location_mm(self):
        return self._starting_height + (self._drips * 1.0 / self._drips_per_mm)

    def set_drips_per_mm(self, drips_per_mm):
        self._drips_per_mm = drips_per_mm

    def move_to(self, height_mm):
        pass

    def close(self):
        logging.info("SerialDripZAxis shutdown successfully")
