import time
import logging
from domain.zaxis import ZAxis


class SerialDripZAxis(ZAxis):
    def __init__(self, communicator, drips_per_mm, starting_height, drip_call_back=None,):
        super(SerialDripZAxis, self).__init__(starting_height)
        self._drips_per_mm = drips_per_mm
        self._drips = 0
        self._starting_height = starting_height
        self._drip_call_back = drip_call_back

    def _drip_reported_handler(self, drip_reported):
        pass
        # self._drip_call_back(drips, self.current_z_location_mm(), average_drips, drip_history)

    def set_call_back(self, call_back):
        pass

    def reset(self):
        pass

    def current_z_location_mm(self):
        return 0
        # return self._starting_height + (self._drips * 1.0 / self._drips_per_mm)

    def set_drips_per_mm(self, drips_per_mm):
        self._drips_per_mm = drips_per_mm

    def move_to(self, height_mm):
        pass

    def close(self):
        logging.info("SerialDripZAxis shutdown successfully")
