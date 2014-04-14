import os
import hashlib
import pickle
import types
import logging

from domain.configuration_manager import ConfigurationManager

class FileBasedConfigurationManager(ConfigurationManager):
    PEACHY_PATH = '.peachyprintertools'
    REQUIRED_FIELDS = {
        'name' : types.StringType ,
        'output_bit_depth': types.StringType ,
        'output_sample_frequency' : types.IntType ,
        'on_modulation_frequency': types.IntType ,
        'off_modulation_frequency': types.IntType ,
        'input_bit_depth': types.StringType ,
        'input_sample_frequency': types.IntType ,
        'sublayer_height_mm': types.FloatType,
        'laser_thickness_mm' : types.FloatType,
        'configurationbounds_mm': types.ListType,
        'drips_per_mm':types.FloatType
    }
    CONFIGURATION_EXTENSION = '.cfg'

    def __init__(self):
        self._configuration_path = os.path.join(os.path.expanduser('~'), self.PEACHY_PATH)

    def list(self):
        printers = []
        if os.path.exists(self._configuration_path):
            for file_name in os.listdir(self._configuration_path):
                if file_name.endswith(self.CONFIGURATION_EXTENSION):
                    configuration = self._load_configuration(os.path.join(self._path(), file_name))
                    if configuration:
                        printers.append(configuration['name'])
        return printers

    def load(self, printer_name):
        logging.info("Loading configutation for %s" % printer_name)
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
            configuration = pickle.load(file_handle)
            if self._valid(configuration):
                return configuration
            else:
                return None

    def save(self, configuration):
        if self._valid(configuration):
            filename = self._get_file_name(configuration['name'])
            with open(filename,'w') as file_handle:
                pickle.dump(configuration, file_handle)
        else:
            logging.error("Saving, Configuration Specified is invalid\n%s" % configuration)
            raise Exception("Configuration Specified is invalid\n%s" % configuration )

    def new(self, printer_name):
        new_printer = self.DEFAULTS.copy()
        new_printer['name'] = printer_name
        return new_printer

    def _valid(self, configuration):
        valid = True
        for (key, value) in self.REQUIRED_FIELDS.items():
            if not (configuration.has_key(key) and type(configuration[key]) == value):
                print("%s is missing or not %s" % (key, value))
                valid = False
        return valid

    def _path(self):
        if not os.path.exists(self._configuration_path):
            os.makedirs(self._configuration_path)
        return self._configuration_path

    def _get_file_name(self, name):
        filename = hashlib.md5(name).hexdigest() + self.CONFIGURATION_EXTENSION
        return os.path.join(self._path(), filename)
