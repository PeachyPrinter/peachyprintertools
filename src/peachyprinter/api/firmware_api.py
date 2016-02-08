import logging
import os
import re
from glob import glob
import threading
import firmware as firmware_manager_factory

from peachyprinter.infrastructure.communicator import UsbPacketCommunicator
from peachyprinter.infrastructure.messages import EnterBootloaderMessage

logger = logging.getLogger('peachy')


class FirmwareAPI(object):
    version_regex = '''.*-([0-9]*[.][0-9]*[.][0-9]*).bin'''

    def __init__(self):
        self.firmware_manager = firmware_manager_factory.get_firmware_updater(logger)
        self._required_version = None
        self._firmware_update = FirmwareUpdate(self._bin_file(), self.firmware_manager)

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
            logger.error("Package missing required firmware")
            raise Exception("Package missing required firmware")
        if len(bin_file) > 1:
            logger.error("Unexpected firmware files")
            raise Exception("Unexpected firmware files")
        return bin_file[0]

    def make_ready(self):
        self._firmware_update.prepare()

    def is_ready(self):
        return self.firmware_manager.check_ready()

    def update_firmware(self, complete_call_back=None):
        if self.is_ready():
            logger.info("Starting external update")
            self._firmware_update.start(complete_call_back)
        else:
            logger.error("Peachy Printer not ready for update")
            raise Exception("Peachy Printer not ready for update")


class FirmwareUpdate(threading.Thread):
    def __init__(self, file, firmware_updater, complete_call_back=None):
        threading.Thread.__init__(self)
        self.file = file
        self.firmware_manager = firmware_updater

    def start(self, complete_call_back):
        self.complete_call_back = complete_call_back
        threading.Thread.start(self)

    def run(self):
        # import traceback
        # try:
            logger.info("Starting firmware update")
            result = self.firmware_manager.update(self.file)
            self.complete_call_back(result)
            logger.info("Firmware update {}".format("succeeded" if result else "failed"))
        # except Exception as ex:
            
        #     traceback.print_last()
        #     logger.error(ex.message)
        #     self.complete_call_back(False)

    def prepare(self):
        usb_communicator = UsbPacketCommunicator(0)
        usb_communicator.start()
        usb_communicator.send(EnterBootloaderMessage())
        usb_communicator.close()
