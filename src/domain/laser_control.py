class LaserControl:
    
    _laser_on = False

    def set_laser_on(self):
        self._laser_on = True

    def set_laser_off(self):
        self._laser_on = False

    def laser_is_on(self):
        return self._laser_on