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

    def send(self, message):
        out = [ self._header ]

        for c in (chr(message.TYPE_ID) + message.get_bytes()):
            if c in self._to_be_escaped:
                out.append(self._escape)
                out.append('%c' % ((~ord(c) & 0xFF),))
            else:
                out.append(c)
        out.append(self._footer)
        logging.info("Sending %d bytes" % (len(out),))
        self._serial.write(''.join(out))
        time.sleep(0.0001)

    def close(self):
        pass

class NullCommunicator(object):
    def send(self, message):
        pass
