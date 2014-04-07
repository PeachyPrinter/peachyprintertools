import os
import hashlib
import json
import types

from domain.configuration_manager import ConfigurationManager

class FileBasedConfigurationManager(ConfigurationManager):
    PEACHY_PATH = '.peachyprintertools'
    REQUIRED_FIELDS = {
        u'name' : types.UnicodeType ,
        u'output_bit_depth': types.IntType ,
        u'output_sample_frequency' : types.IntType ,
        u'on_modulation_frequency': types.IntType ,
        u'off_modulation_frequency': types.IntType ,
        u'input_bit_depth': types.IntType ,
        u'input_sample_frequency': types.IntType ,
        u'sublayer_height_mm': types.FloatType,
        u'configurationbounds_mm': types.ListType,
    }
    CONFIGURATION_EXTENSION = '.cfg'

    def __init__(self):
        self._configuration_path = os.path.join(os.path.expanduser('~'), self.PEACHY_PATH)
        self._defaults = {
            u'name' : u"Unnamed Printer",
            u'output_bit_depth' : 16,
            u'output_sample_frequency' : 48000,
            u'on_modulation_frequency' : 12000,
            u'off_modulation_frequency' : 8000,
            u'input_bit_depth' : 16,
            u'input_sample_frequency' : 48000,
            u'sublayer_height_mm' : 0.1,
            u'configurationbounds_mm' : [
                    [1.0,1.0,0.0],[1.0,-1.0,0.0],[-1.0,-1.0,0.0],[-1.0,1.0,0.0],
                    [1.0,1.0,1.0],[1.0,-1.0,1.0],[-1.0,-1.0,1.0],[-1.0,1.0,1.0]
                ],
            }

    def list(self):
        printers = []
        if os.path.exists(self._configuration_path):
            for file_name in os.listdir(self._configuration_path):
                if file_name.endswith(self.CONFIGURATION_EXTENSION):
                    configuration = self._load_configuration(file_name)
                    if configuration:
                        printers.append(configuration[u'name'])
        return printers

    def load(self, printer_name):
        filename = self._get_file_name(printer_name)
        if not os.path.exists(filename):
            raise Exception("Printer file not found")
        configuration = self._load_configuration(filename)
        if configuration:
            return configuration
        else:
            raise Exception("Printer file corrupt or damaged")

    def _load_configuration(self, filename):
        with open(filename, 'r') as file_handle:
            configuration = json.loads(''.join(file_handle.read()))
            if self._valid(configuration):
                return configuration
            else:
                return None

    def save(self, configuration):
        if self._valid(configuration):
            filename = self._get_file_name(configuration['name'])
            with open(filename,'w') as file_handle:
                file_handle.write(json.dumps(configuration))
        else:
            raise Exception("Configuration Specified is invalid")

    def new(self, printer_name):
        new_printer = self._defaults.copy()
        new_printer[u'name'] = unicode(printer_name)
        return new_printer

    def _valid(self, configuration):
        valid = True
        for (key, value) in self.REQUIRED_FIELDS.items():
            if not (configuration.has_key(key) and type(configuration[key]) == value):
                valid = False
        return valid

    def _path(self):
        if not os.path.exists(self._configuration_path):
            os.makedirs(self._configuration_path)
        return self._configuration_path

    def _get_file_name(self, name):
        filename = hashlib.md5(name).hexdigest() + self.CONFIGURATION_EXTENSION
        return os.path.join(self._path(), filename)
