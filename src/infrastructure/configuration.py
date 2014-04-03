class Configuration(object):
    def __init__(self):
        self.name = 
        self.output_bit_depth = 16
        self.output_sample_frequency = 48000
        self.on_modulation_frequency = 12000
        self.off_modulation_frequency = 8000
        self.input_bit_depth = 16
        self.input_sample_frequency = 48000
        self.sublayer_height_mm = 0.1
        self.configurationbounds_mm = [
                [1.0,1.0,0.0],[1.0,-1.0,0.0],[-1.0,-1.0,0.0],[-1.0,1.0,0.0],
                [1.0,1.0,1.0],[1.0,-1.0,1.0],[-1.0,-1.0,1.0],[-1.0,1.0,1.0]
            ]
