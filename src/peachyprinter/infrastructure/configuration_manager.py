import os
import json
import types
import logging
import time
logger = logging.getLogger('peachy')
import re

from peachyprinter.domain.configuration_manager import ConfigurationManager
import peachyprinter.config as config
from peachyprinter.infrastructure.communicator import UsbPacketCommunicator, MissingPrinterException
from peachyprinter.infrastructure.messages import IAmMessage, IdentifyMessage
from peachyprinter.infrastructure.configuration import ConfigurationGenerator, Configuration


class CircutSourcedConfigurationManager(ConfigurationManager):
    CONFIGURATION_EXTENSION = '.cfg'

    def __init__(self):
        self.printer_details = None

    def _ident_call_back(self, message):
        self.printer_details = message

    def load(self, printer_name=None):
        if printer_name is not None:
            raise Exception("Printer Configurtations Cannot be loaded manually Do not specify a printer")
        details = self._get_printer_details()
        configuration = self._load_or_create_configuration(details.sn)
        configuration.circut.serial_number = details.sn
        configuration.circut.hardware_revision = details.hwrev
        configuration.circut.software_revision = details.swrev
        configuration.circut.data_rate = details.dataRate
        self.save(configuration)
        return configuration

    def reset(self):
        details = self._get_printer_details()
        full_filepath = self._get_file_name(details.sn)
        os.remove(full_filepath)
        return self.load()

    def _load_or_create_configuration(self, serial_number):
        full_filepath = self._get_file_name(serial_number)
        if os.path.isfile(full_filepath):
            cfg = self._load_configuration(full_filepath)
        else:
            cfg = self._create_configuration(full_filepath, serial_number)
        return cfg

    def _create_configuration(self, filename, serial_number):
        new_printer_config = ConfigurationGenerator().default_configuration()
        new_printer_config.name = serial_number
        return new_printer_config

    def _load_configuration(self, filename):
        with open(filename, 'r') as file_handle:
            try:
                data = file_handle.read()
                conf = Configuration(json.loads(data))
                return conf
            except Exception as ex:
                logger.error("Error loading file: %s" % ex)
                return None

    def _path(self):
        if not os.path.exists(config.PEACHY_PATH):
            os.makedirs(config.PEACHY_PATH)
        return config.PEACHY_PATH

    def _get_file_name(self, name):
        safe_name = ''.join(l for l in name if l.isalnum())
        filename = safe_name + self.CONFIGURATION_EXTENSION
        return os.path.join(self._path(), filename)

    def _get_printer_details(self):
        communicator = UsbPacketCommunicator()
        communicator.register_handler(IAmMessage, self._ident_call_back)
        communicator.start()
        communicator.send(IdentifyMessage())
        until = time.time() + 5.0
        while (not self.printer_details and time.time() < until):
            time.sleep(0.1)
        communicator.close()
        details = self.printer_details
        self.printer_details = None
        return details

    def new(self, printer_name):
        raise Exception("Printer Configurtations Cannot be created manually")

    def save(self, configuration):
        full_filepath = self._get_file_name(configuration.name)
        with open(full_filepath, 'w') as file_handle:
            file_handle.write(configuration.toJson())
