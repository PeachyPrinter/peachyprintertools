import pyaudio
import numpy as np
import math
import time

class AudioWriter(object):
    def __init__(self, sample_rate, bit_rate):
        self._sample_rate = sample_rate
        self._bit_rate = bit_rate
        self._format = self._get_format_from_rate(bit_rate)
        self._max_bit_value = math.pow(2, bit_rate - 1) - 1.0
        self._pa = pyaudio.PyAudio()
        self._format = self._get_format_from_rate(bit_rate)
        self._buffer_size = self._sample_rate / 8

        if not self._configuration_supported(self._sample_rate,self._format):
            raise Exception("Audio configuration not supported; Sample Rate: %s; Sample Bits: %s " % (self._sample_rate, self._bit_rate) )
        self._outstream = self._pa.open(
            format=self._format,
            channels = 2,
            rate=self._sample_rate,
            output=True,
            frames_per_buffer=self._buffer_size 
            )
        self._outstream.start_stream()

    def _configuration_supported(self, sample_rate, format):
        device_info = self._pa.get_default_host_api_info()
        default_device_id = device_info['defaultInputDevice']
        supported = self._pa.is_format_supported(sample_rate,output_device=default_device_id,output_channels=2,output_format=format)
        return supported

    def _get_format_from_rate(self,rate):
        if rate == 8:
            return pyaudio.paInt8
        elif rate == 16:
            return pyaudio.paInt16
        elif rate == 24:
            return pyaudio.paInt24
        elif rate == 32:
            return pyaudio.paInt32
        else:
            raise Exception("Bit rate %s specified is not supported" % rate)

    def write_chunk(self, chunk):
        frames = self._to_frame(chunk)
        while frames and len(frames) > 0:
            buffer_size = self._outstream.get_write_available()
            if buffer_size > len(frames):
                self._outstream.write(frames)
                frames = None
            else:
                self._outstream.write(frames[:buffer_size-1])
                frames = frames[buffer_size-1:]

    def _to_frame(self, values):
        values = np.rint( values * self._max_bit_value)
        mod = values.astype(np.dtype('<i2'))
        return mod.tostring()

    #TODO JT 2014-04-01 - Ctrl-C hook
    def close(self):
        self._outstream.stop_stream()
        self._pa.terminate()
