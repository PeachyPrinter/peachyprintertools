import serial
import logging
import time

class Commander(object):
    def send_command(self, command):
        raise NotImplementedError("This is not implemented")

class SerialCommander(object):
    def __init__(self, port, baud= 9600, connection_timeout = 20):
        logging.info("Opening serial on port: %s at rate: %s" % (port, baud))
        self._connection_timeout = connection_timeout
        self._connection = serial.Serial(port,baud)
        # self._wait_for_init()

    def _wait_for_init(self):
        start = time.time()
        while time.time() - start < self._connection_timeout:
            self._connection.write('1\n')
            time.sleep(0.1)
            if self._connection.readline().rstrip() == "OK":
                return
        raise Exception("Could not start serial")

    def send_command(self, command):
        logging.info("Attempting to send command: %s" % command) 
        if self._connection.isOpen():
            self._connection.flushInput()
            self._connection.flushOutput()
            serial_command = '%s\r\n' % command.encode('utf-8')
            self._connection.write(serial_command)
            logging.info("sent command: %s" % command) 


    def close(self):
        self._connection.close()

class NullCommander(Commander):
    def __init__(self):
        pass
    def send_command(self, command):
        pass
