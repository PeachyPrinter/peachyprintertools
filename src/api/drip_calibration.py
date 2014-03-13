

class DripCalibrationAPI(object):
    def __init__(self, drip_detector):
        self._drip_detector = drip_detector
        

    def get_drips(self):
        return self._drip_detector.current_z_location_mm()

    def set_drips_per_mm(self,drips):
        pass

    def reset_drips(self):
        self._drip_detector.reset(0)