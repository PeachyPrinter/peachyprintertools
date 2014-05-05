import logging
import serial
import time

from domain.zaxis import ZAxisControl

class SerialZAxisControl(ZAxisControl): 

    def __init__(self, port, baud = 9600, on_command = '1', off_command = '0', repeat_delay_ms= 2000):
        self.on_command = on_command
        self.off_command = off_command
        self._timeout = repeat_delay_ms

        self._on_last_called = 0.0
        self._off_last_called = 0.0
        self._connection = serial.Serial(port,baud)
        self._connection.open()

    def close(self):
        self._connection.close()

    def move_up(self):
        now = time.time()
        if now - self._on_last_called > self._timeout:
            self._connection.write(self.on_command)
            self._on_last_called = now

    def stop(self):
        now = time.time()
        if now - self._off_last_called > self._timeout:
            self._connection.write(self.off_command)
            self._off_last_called = now