import logging
logger = logging.getLogger('peachy')
import os
import re
from glob import glob
import threading
import firmware


class FirmwareAPI(object):
    version_regex = '''.*-([0-9]*[.][0-9]*[.][0-9]*).bin'''
    def __init__(self):
        self.firmware_updater = firmware.get_firmware_updater(logger)


    def is_firmware_valid(self, current_firmware):
        bin_file = self._bin_file()
        available_version = re.match(self.version_regex, bin_file).group(1)
        return available_version == current_firmware

    def _bin_file(self):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dependancies', 'firmware'))
        bin_file = glob(os.path.join(path, 'peachyprinter-firmware-*.bin'))
        if not bin_file:
            raise Exception("Package missing required firmware")
        if len(bin_file) > 1:
            raise Exception("Unexpected firmware files")
        return bin_file[0]

    def make_ready(self):
        pass

    def is_ready(self):
        return self.firmware_updater.check_ready()

    def update_firmware(self, complete_call_back=None):
        pass


class FirmwareUpdate(threading.Thread):
    def __init__(self, file, firmware_updater, complete_call_back=None):
        pass

    def run(self):
        pass
