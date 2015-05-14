import libusb1
import usb1
import logging
import threading
import time
from messages import ProtoBuffableMessage

logger = logging.getLogger('peachy')


class Communicator(object):
    def send(self, message):
        raise NotImplementedError()

    def register_handler(self, message_type, handler):
        raise NotImplementedError()


class MissingPrinterException(Exception):
    pass


class UsbPacketCommunicator(Communicator, threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._handlers = {}
        self._usbContext = None
        self._device = None
        self._devHandle = None
        self._keepRunning = False
        self._isRunning = False

    def start(self):
        self._usbContext = usb1.USBContext()
        self._device = self._usbContext.getByVendorIDAndProductID(0x16d0, 0xaf3)
        if not self._device:
            raise MissingPrinterException()
        self._devHandle = self._device.open()
        self._devHandle.claimInterface(0)
        self._isRunning = True
        self._keepRunning = True
        super(UsbPacketCommunicator, self).start()

    def close(self):
        self._keepRunning = False
        while self._isRunning:
            time.sleep(0.1)

    def run(self):
        while self._keepRunning:
            data = None
            try:
                data = self._devHandle.bulkRead(3, 64, timeout=100)
            except (libusb1.USBError,), e:
                if e.value == -7:  # timeout
                    continue
                if e.value == -1 or e.value == -4:
                    logger.info("Printer missing or detached")
                    raise MissingPrinterException(e)
                raise
            if not data:
                continue
            logger.info("Received %d bytes from device" % (len(data),))
            self._process(data)
        self._devHandle.close()
        self._isRunning = False

    def _process(self, data):
        message_type_id = ord(data[0])
        for (message, handlers) in self._handlers.items():
            if message.TYPE_ID == message_type_id:
                for handler in handlers:
                    handler(message.from_bytes(data[1:]))

    def send(self, message):
        if not self._keepRunning:
            return
        try:
            data = chr(message.TYPE_ID) + message.get_bytes()
            self._devHandle.bulkWrite(2, data, timeout=1000)
        except (libusb1.USBError,), e:
            if e.value == -1 or e.value == -4:
                logger.info("Printer missing or detached")
                raise MissingPrinterException(e)

    def register_handler(self, message_type, handler):
        if not issubclass(message_type, ProtoBuffableMessage):
            logger.error("ProtoBuffableMessage required for message type")
            raise Exception("ProtoBuffableMessage required for message type")
        if message_type in self._handlers:
            self._handlers[message_type].append(handler)
        else:
            self._handlers[message_type] = [handler]


class NullCommunicator(Communicator):
    def send(self, message):
        pass

    def register_handler(self, message_type, handler):
        pass
