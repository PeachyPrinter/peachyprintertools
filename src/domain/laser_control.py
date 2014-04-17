import logging

class LaserControl:
    
    _laser_on = False

    def set_laser_on(self):
        logging.debug("Laser On")
        self._laser_on = True

    def set_laser_off(self):
        logging.debug("Laser Off")
        self._laser_on = False

    def laser_is_on(self):
        return self._laser_on