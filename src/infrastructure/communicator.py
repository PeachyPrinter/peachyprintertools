import serial
import logging
import time

class Communicator(object):
    def send(self, message):
        raise NotImplementedError()

    def recieve(self, type_id, handler):
        raise NotImplementedError()

class SerialCommunicator(object):
    def __init__(self, port, header, footer, escape):
        logging.info("Opening serial port: %s" % (port,))
        self._serial = serial.Serial(port)
        self._header = header
        self._footer = footer
        self._escape = escape
        self._to_be_escaped = [self._header, self._footer, self._escape]
        self._start = time.time()
        self._sent = 0

    def send(self, message):
        out = [ self._header ]

        for c in (chr(message.TYPE_ID) + message.get_bytes()):
            if c in self._to_be_escaped:
                out.append(self._escape)
                out.append('%c' % ((~ord(c) & 0xFF),))
            else:
                out.append(c)
        out.append(self._footer)
        self._sent += len(out)
        self._serial.write(''.join(out))
        now = time.time()
        if self._sent > 50000 or (now - self._start) > 1:
            logging.info("Sent %d bytes (%d bytes/sec)" % (self._sent, self._sent/(now - self._start)))
            self._sent = 0
            self._start = now

    def close(self):
        self._serial.close()

class NullCommunicator(object):
    def send(self, message):
        pass
