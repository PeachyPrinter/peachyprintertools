import serial
import logging
import time
import threading

class Commander(object):
    def send_command(self, command):
        raise NotImplementedError("This is not implemented")

class SerialCommander(object):
    def __init__(self, port, baud= 9600, connection_timeout = 10):
        self._lock = threading.Lock()
        self.port = port
        self.baud = baud
        self._connection_timeout = connection_timeout
        logging.info("Opening serial on port: %s at rate: %s" % (self.port,self.baud))
        self._connection = serial.Serial(self.port,self.baud,timeout = 1, writeTimeout = 1, interCharTimeout=1)
        self._wait_for_init()

    def _wait_for_init(self):
        start = time.time()
        while time.time() - start < self._connection_timeout:
            logging.info('Serial Writing Hello')
            self._connection.write("D")
            logging.info('Reading Hello')
            time.sleep(1)
            read = self._connection.readline().rstrip()
            if read == "OK":
                logging.info('Read Hello Successfully')
                return
            logging.info('Failed Reading Hello retrying')
        logging.error("FAILED Opening serial on port: %s at rate: %s" % (self.port,self.baud))
        raise Exception("Could not start serial")

    def send_command(self, command):
        # logging.info("Attempting to send command: %s" % command) 
        self._lock.acquire()
        try:
            if self._connection.isOpen():
                self._connection.flushInput()
                self._connection.flushOutput()
                serial_command = '%s\r\n' % command.encode('utf-8')
                self._connection.write(serial_command)
                # logging.info("sent command: %s" % command) 
        finally:
            self._lock.release()


    def close(self):
        self._connection.close()

class NullCommander(Commander):
    def __init__(self):
        pass
    def send_command(self, command):
        pass
