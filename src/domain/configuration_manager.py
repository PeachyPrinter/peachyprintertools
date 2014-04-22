class ConfigurationManager(object):
    DEFAULTS = {
            'name' : "Unnamed Printer",
            'output_bit_depth' : '16 bit',
            'output_sample_frequency' : 48000,
            'on_modulation_frequency' : 12000,
            'off_modulation_frequency' : 8000,
            'input_bit_depth' : '16 bit',
            'input_sample_frequency' : 48000,
            'sublayer_height_mm' : 0.1,
            'drips_per_mm' : 1.0,
            'laser_thickness_mm' : 0.5,
            'max_deflection': 0.75,
            'calibration_data' : { 
                'height': 1, 
                'lower_points':{(1,1):(1,1),(1,0):(1,0),(0,0):(0,0),(0,1):(0,1),},
                'upper_points':{(1,1):(1,1),(1,0):(1,0),(0,0):(0,0),(0,1):(0,1),},
                },
            'calibration_scale' : 1.0,
            }

    def list(self):
        raise NotImplementedException("Abstract Class")

    def load(self, printer_name):
        raise NotImplementedException("Abstract Class")

    def save(self, configuration):
        raise NotImplementedException("Abstract Class")

    def new(self, printer_name):
        raise NotImplementedException("Abstract Class")

    def get_current_config(self):
        raise NotImplementedException("Abstract Class")

