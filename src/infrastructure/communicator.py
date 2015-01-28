import serial
import logging
import threading
import time

class Communicator(object):
    def send(self, message):
        raise NotImplementedError()

    def register_handler(self, type_id, handler):
        raise NotImplementedError()


class SerialCommunicator(Communicator, threading.Thread):
    def __init__(self, port, header, footer, escape):
        threading.Thread.__init__(self)
        self._port = port
        self._running = False
        self._header = header
        self._footer = footer
        self._escape = escape
        self._to_be_escaped = [self._header, self._footer, self._escape]

    def send(self, message):
        if not self._running:
            logging.error("attempt to send message before start")
            raise Exception("attempt to send message before start")
        out = [self._header]
        for c in (chr(message.TYPE_ID) + message.get_bytes()):
            if c in self._to_be_escaped:
                out.append(self._escape)
                out.append('%c' % ((~ord(c) & 0xFF),))
            else:
                out.append(c)
        out.append(self._footer)
        self._connection.write(''.join(out))

    def start(self):
        super(SerialCommunicator, self).start()
        while not self._running:
            time.sleep(0.01)

    def run(self):
        logging.info("Opening serial port: %s" % (self._port,))
        self._connection = serial.Serial(self._port)
        self._running = True
        while self._running:
            time.sleep(0.1)
        self._connection.close()

    def close(self):
        self._running = False
        while self.is_alive():
            time.sleep(0.01)


class NullCommunicator(Communicator):
    def send(self, message):
        pass
