import logging
import time
from messages import ProtoBuffableMessage
import Queue as queue
from Queue import Empty
from peachyprinter.infrastructure.peachyusb import PeachyUSB, PeachyUSBException

logger = logging.getLogger('peachy')


class Communicator(object):
    def send(self, message):
        raise NotImplementedError()

    def register_handler(self, message_type, handler):
        raise NotImplementedError()


class MissingPrinterException(Exception):
    pass


class UsbPacketCommunicator(Communicator):
    def __init__(self, queue_size=500):
        self._handlers = {}
        self._device = None
        self.sent_bytes = 0
        self.last_sent_time = time.time()
        self.send_time = 0
        self._detached = False
        self._queue_size = queue_size

    def __del__(self):
        self.close()

    def start(self):
        logging.info("USING PEACHY USB")
        self._device = PeachyUSB(self._queue_size)
        self._device.set_read_callback(self._process)
        if not self._device:
            raise MissingPrinterException()

    def close(self):
        dev = self._device
        self._device = None
        del dev

    def _process(self, data, length):
        data = data[:length]
        message_type_id = ord(data[0])
        for (message, handlers) in self._handlers.items():
            if message.TYPE_ID == message_type_id:
                for handler in handlers:
                    handler(message.from_bytes(data[1:]))

    def send(self, message):
        if self._detached:
            raise MissingPrinterException(self._detached)
        self._send(message)

    def _send(self, message):
        if not self._device:
            return
        try:
            if message.TYPE_ID != 99:
                per_start_time = time.time()
                data = chr(message.TYPE_ID) + message.get_bytes()
                data = chr(len(data)) + data
                self._device.write(data)
                per_end_time = time.time() - per_start_time
                self.send_time = self.send_time + per_end_time
                self.sent_bytes += len(data)
                if self.sent_bytes > 100000:
                    seconds = time.time() - self.last_sent_time
                    real_time_per_byte = (seconds * 1000.0) / (self.sent_bytes / 1024)
                    cpu_time_per_byte = (self.send_time * 1000.0) / (self.sent_bytes / 1024)
                    bps = self.sent_bytes / seconds
                    self.last_sent_time = time.time()
                    self.send_time = 0
                    self.sent_bytes = 0
                    logger.info("Real Time   : %.2f uspKB" % real_time_per_byte)
                    logger.info("CPU Time    : %.2f uspKB" % cpu_time_per_byte)
                    logger.info("Bytes       : %.2f bps" % bps)
            else:
                time.sleep(1.0 / 2000.0)

        except (PeachyUSBException), e:
            if e.value == -1 or e.value == -4:
                logger.info("Printer missing or detached")
                self._detached = e
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
