from peachyprinter.infrastructure.communicator import UsbPacketCommunicator
from peachyprinter.infrastructure.messages import EnterBootloaderMessage

class FirmwareUpdate(object):
    def __init__(self):
        pass

    def start_update(self):
        usb_communicator = UsbPacketCommunicator(0)
        usb_communicator.start()
        usb_communicator.send(EnterBootloaderMessage())
        usb_communicator.close()
