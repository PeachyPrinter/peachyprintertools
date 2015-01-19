

class LaserControl:
    def __init__(self, default_on_power=1.0):
        self._default_laser_power = default_on_power
        self._laser_power = 0.0

    def set_laser_on(self):
        self._laser_power = self._default_laser_power

    def set_laser_off(self):
        self._laser_power = 0.0

    def laser_is_on(self):
        return self._laser_power > 0.0

    def laser_power(self):
        return self._laser_power
