import wave
import serial
import struct
import time
import signal
import sys

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sr.close()
        data.close()
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


with serial.Serial('COM9', 
                    baudrate = 2, 
                    timeout =1,
                    parity = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_ONE,
                    bytesize = serial.EIGHTBITS) as sr:
    sr.writeTimeout = 10
    sr.flushOutput()
    data = wave.open('test.wav','r')
    time.sleep(1)

    frames = data.getnframes()
    written_chunks = 0
    while frames > 0:
        to_read = min(frames, 1024)
        tx = data.readframes(to_read)
        frames = frames - to_read
        fmt = "%ih" % to_read * 2
        unpacked = struct.unpack(fmt,tx)
        tr = ''
        for d in unpacked:
            try:
                tr += struct.pack('h', d)
            except Exception as ex:
                print("ERROR: could not pack value: %s"  % hex(d))
                exit(666)
        tx = ''
        for i in range(0,len(tr),4):
            tx = tx + tr[i] + tr[i+1]
        sr.write(tx)
        written_chunks += 1
        if written_chunks % 100 == 0:
            print("Chunks: %s" % written_chunks)
    data.close()
 

print("closing")
