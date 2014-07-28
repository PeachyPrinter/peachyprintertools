import logging

class LaserControl:
    _laser_on = False

    def set_laser_on(self):
        self._laser_on = True
        # logging.debug('Laser On')

    def set_laser_off(self):
        self._laser_on = False
        # logging.debug('Laser Off')

    def laser_is_on(self):
        return self._laser_on