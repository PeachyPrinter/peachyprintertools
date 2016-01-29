import logging
logger = logging.getLogger('peachy')
import os
import re
from glob import glob



class FirmwareAPI(object):
    version_regex = '''.*-([0-9]*[.][0-9]*[.][0-9]*).bin'''

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
        pass

    def update_firmware(self):
        pass
