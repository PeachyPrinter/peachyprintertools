
class ZAxis(object):

    def current_z_location_mm():
        raise NotImplementedError()

    def reset(z_height_mm = 0):
        raise NotImplementedError()

    def move_to_location(z_mm):
        raise NotImplementedError()


class ZAxisControl(object):
    
    def move_up(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()