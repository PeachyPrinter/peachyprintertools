import os
import hashlib
import json
import types

class ConfigurationManager(object):
    PEACHY_PATH = '.peachyprintertools'
    REQUIRED_FIELDS = {
        'name' : types.StringType,
        'output_bit_depth': types.IntType ,
        'output_sample_frequency' : types.IntType,
        'on_modulation_frequency': types.IntType,
        'off_modulation_frequency': types.IntType,
        'input_bit_depth': types.IntType,
        'input_sample_frequency': types.IntType,
        'sublayer_height_mm':types.FloatType,
        'configurationbounds_mm':types.ListType,
    }

    def __init__(self):
        self._configuration_path = os.path.join(os.path.expanduser('~'), self.PEACHY_PATH)

    def list(self):
        printers = []
        if os.path.exists(self._configuration_path):
            for file_name in os.listdir(self._configuration_path):
                file_handle = open(os.path.join(self._configuration_path, file_name), 'r')
                data = json.loads(''.join(file_handle.readlines()))
                printers.append(data[u'name'])
        return printers

    def load(self):
        pass

    def save(self, configuration):
        self._verify_data(configuration)
        filename = self._get_file_name(configuration['name'])
        filepath = os.path.join(self._path(), filename)
        with open(filepath,'w') as out_file:
            out_file.write(json.dumps(configuration))

    def new(self):
        return {
            'name' : "Unnamed Printer",
            'output_bit_depth' : 16,
            'output_sample_frequency' : 48000,
            'on_modulation_frequency' : 12000,
            'off_modulation_frequency' : 8000,
            'input_bit_depth' : 16,
            'input_sample_frequency' : 48000,
            'sublayer_height_mm' : 0.1,
            'configurationbounds_mm' : [
                    [1.0,1.0,0.0],[1.0,-1.0,0.0],[-1.0,-1.0,0.0],[-1.0,1.0,0.0],
                    [1.0,1.0,1.0],[1.0,-1.0,1.0],[-1.0,-1.0,1.0],[-1.0,1.0,1.0]
                ],
            }

    def _verify_data(self, data):
        for (key, value) in self.REQUIRED_FIELDS.items():
            if not (data.has_key(key) and type(data[key]) == value):
                raise Exception("%s required and must be of type %s" % (key,value))

    
    def _path(self):
        if not os.path.exists(self._configuration_path):
            os.makedirs(self._configuration_path)
        return self._configuration_path


    def _get_file_name(self, name):
        return hashlib.md5(name).hexdigest() + '.cfg'

# class Configuration(object):
#     def __init__(self):
#         self.name = "Unnamed Printer"
#         self.output_bit_depth = 16
#         self.output_sample_frequency = 48000
#         self.on_modulation_frequency = 12000
#         self.off_modulation_frequency = 8000
#         self.input_bit_depth = 16
#         self.input_sample_frequency = 48000
#         self.sublayer_height_mm = 0.1
#         self.configurationbounds_mm = [
#                 [1.0,1.0,0.0],[1.0,-1.0,0.0],[-1.0,-1.0,0.0],[-1.0,1.0,0.0],
#                 [1.0,1.0,1.0],[1.0,-1.0,1.0],[-1.0,-1.0,1.0],[-1.0,1.0,1.0]
#             ]
