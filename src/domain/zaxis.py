
class ZAxis(object):
    def __init__(self, starting_height):
        self._starting_height = starting_height

    def current_z_location_mm():
        raise NotImplementedError('current_z_location_mm unimplmented')

    def reset(z_height_mm=0):
        raise NotImplementedError('reset unimplmented')

    def set_call_back(self, call_back):
        raise NotImplementedError('set_call_back unimplmented')

    def move_to(self, height_mm):
        raise NotImplementedError('move_to unimplmented')
