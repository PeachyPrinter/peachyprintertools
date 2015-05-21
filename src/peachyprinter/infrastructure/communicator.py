import libusb1
import usb1
import logging
import threading
import time
from messages import ProtoBuffableMessage
import Queue as queue
from Queue import Empty

logger = logging.getLogger('peachy')


class Communicator(object):
    def send(self, message):
        raise NotImplementedError()

    def register_handler(self, message_type, handler):
        raise NotImplementedError()


class MissingPrinterException(Exception):
    pass


class QueuedSender(threading.Thread):
    def __init__(self, send_method):
        self.qu = queue.Queue(maxsize=10)
        self._keepRunning = True
        self.running = False
        self._send = send_method
        super(QueuedSender, self).__init__()

    def queue(self, message):
        self.qu.put(message, True)
        # logger.info('Queue Length: %s' % self.qu.qsize())

    def run(self):
        self.running = True
        while self._keepRunning:
            try:
                message = self.qu.get(True, 0.1)
                self._send(message)
            except Empty:
                pass
        self.running = False

    def close(self):
        self._keepRunning = False
        while self.running is True:
            time.sleep(0.1)


class UsbPacketCommunicator(Communicator, threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._handlers = {}
        self._usbContext = None
        self._device = None
        self._devHandle = None
        self._keepRunning = False
        self._isRunning = False
        self.sent_bytes = 0
        self.last_sent_time = time.time()
        self.send_time = 0
        self.qu = QueuedSender(self._send)

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
        self.qu.close()
        self._keepRunning = False
        while self._isRunning:
            time.sleep(0.1)

    def run(self):
        self.qu.start()
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
        self.qu.queue(message)


    def _send(self, message):
        if not self._keepRunning:
            return
        try:
            if message.TYPE_ID != 99:
                per_start_time = time.time()
                data = chr(message.TYPE_ID) + message.get_bytes()
                self._devHandle.bulkWrite(2, data, timeout=1000)
                per_end_time = time.time() - per_start_time
                self.send_time = self.send_time + per_end_time
                self.sent_bytes += len(data)
                if self.sent_bytes > 100000:
                    seconds = time.time() - self.last_sent_time
                    bps = (seconds * 1000.0) / (self.sent_bytes / 1024)
                    time_per_byte = (self.send_time * 1000.0) / (self.sent_bytes / 1024)
                    self.last_sent_time = time.time()
                    self.send_time = 0
                    self.sent_bytes = 0
                    logger.info("Real Time   : %.2f uspKB" % bps)
                    logger.info("CPU Time    : %.2f uspKB" % time_per_byte)
            else:
                time.sleep(1.0 / 2000.0)

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
