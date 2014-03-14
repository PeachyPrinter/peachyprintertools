

class DripCalibrationAPI(object):
    def __init__(self, drip_detector):
        self._drip_detector = drip_detector
        
    def get_drips(self):
        return self._drip_detector.current_z_location_mm()

    def mark_drips_at_target(self):
        if self._target_height != None:
            self._marked_drips = self.get_drips()
        else:
            raise Exception("Target height must be specified before marking end point")

    def set_target_height(self,height_mm):
        try:
            if float(height_mm) > 0.0:
                self._target_height = float(height_mm)
            else:
                raise Exception("Target height must be a positive numeric value")
        except:
            raise Exception("Target height must be a positive numeric value")

    def reset_drips(self):
        self._drip_detector.reset(0)

    def get_drips_per_mm(self):
        return self._marked_drips / self._target_height