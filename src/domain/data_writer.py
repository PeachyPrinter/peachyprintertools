
class DataWriter(object):
    
    def write_chunk(self, chunk):
        raise NotImplementedError('write_chunk unimplmented')

    def next_layer(self, layer):
        pass

    def close(self):
        pass