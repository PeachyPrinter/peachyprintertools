
class ZAxis():

    def current_z_location_mm():
        raise NotImplementedError()

    def reset(z_height_mm = 0):
        raise NotImplementedError()

    def move_to_location(z_mm):
        raise NotImplementedError()