
class DataWriter(object):
    
    def write_chunk(self, chunk):
        raise NotImplementedError('write_chunk unimplmented')

    def next_layer(self, layer):
        raise NotImplementedError('next_layer unimplmented')

    def close(self):
        pass