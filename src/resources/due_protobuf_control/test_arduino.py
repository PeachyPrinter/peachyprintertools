import serial
import time

packet = '@%sA'
con = serial.Serial('/dev/ttyACM1',9600,timeout = 1, writeTimeout = 1, interCharTimeout=1)
time.sleep(2)
for i in range(0, 30):
    data = packet % (chr(67 + i) * 10)
    con.write(data)
    # con.write(packet)
    print('sent: %s' % data)
