import logging
import os
import re
from glob import glob
import threading
import firmware as firmware_manager

logger = logging.getLogger('peachy')


class FirmwareAPI(object):
    version_regex = '''.*-([0-9]*[.][0-9]*[.][0-9]*).bin'''

    def __init__(self):
        self.firmware_updater = firmware_manager.get_firmware_updater(logger)
        self._required_version = None

    @property
    def required_version(self):
        if self._required_version is None:
            bin_file = self._bin_file()
            self._required_version = re.match(self.version_regex, bin_file).group(1)
        return self._required_version

    def is_firmware_valid(self, current_firmware):
        return self.required_version == current_firmware

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
        if self.is_ready():
            FirmwareUpdate(self._bin_file(), self.firmware_updater, complete_call_back).start()
        else:
            logger.error("Peachy Printer not ready for update")
            raise Exception("Peachy Printer not ready for update")


class FirmwareUpdate(threading.Thread):
    def __init__(self, file, firmware_updater, complete_call_back=None):
        threading.Thread.__init__(self)
        self.file = file
        self.firmware_updater = firmware_updater
        self.complete_call_back = complete_call_back

    def run(self):
        logger.info("Starting firmware update")
        result = self.firmware_updater.update(self.file)
        self.complete_call_back(result)
        logger.info("Firmware update {}".format("succeeded" if result else "failed"))

