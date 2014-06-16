
class ZAxis(object):

    def current_z_location_mm():
        raise NotImplementedError('current_z_location_mm unimplmented')

    def reset(z_height_mm = 0):
        raise NotImplementedError('reset unimplmented')

    def set_call_back(self, call_back):
        raise NotImplementedError('set_call_back unimplmented')

    def move_to(self, height_mm):
        raise NotImplementedError('move_to unimplmented')