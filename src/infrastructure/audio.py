import pyaudio
import numpy as np
import math
import time

# class PyAudioAudioSetup(object):
#     def __init__(self):
#         pass

#     def get_valid_input_devices(self):
#         pass

#     def get_valid_sample_rates(self, device):
#         pass

#     def get_valid



class AudioWriter(object):
    def __init__(self, sample_rate, bit_depth):
        self._sample_rate = sample_rate
        self._bit_depth = bit_depth
        self._set_format_from_depth(bit_depth)
        self._max_bit_value = math.pow(2, bit_depth - 1) - 1.0
        self._pa = pyaudio.PyAudio()
        self._buffer_size = self._sample_rate / 8

        if not self._configuration_supported(self._sample_rate,self._format):
            raise Exception("Audio configuration not supported; Sample Rate: %s; Sample Bits: %s " % (self._sample_rate, self._bit_depth) )
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

    def _set_format_from_depth(self,depth):
        if depth == 8:
            self._format =  pyaudio.paInt8
            self._max_bit_value = math.pow(2, depth - 1) - 1.0
        elif depth == 16:
            self._format =  pyaudio.paInt16
            self._max_bit_value = math.pow(2, depth - 1) - 1.0
        elif depth == 24:
            self._format =  pyaudio.paInt24
            self._max_bit_value = math.pow(2, depth - 1) - 1.0
        elif depth == 32:
            self._format =  pyaudio.paFloat32
            self._max_bit_value = 1.0
        else:
            raise Exception("Bit depth %s specified is not supported" % depth)

    def _wait_for_buffer(self,current_buffer_size):
        if current_buffer_size < self._buffer_size / 8.0:
            time.sleep(self._buffer_size * 1.0 / self._sample_rate * 1.0 / 8.0)

    def write_chunk(self, chunk):
        for audio in chunk:
            frames = self._to_frame(audio)
            buffer_size = self._outstream.get_write_available()
            self._wait_for_buffer(buffer_size)
            self._outstream.write(frames)


    def _to_frame(self, values):
        if (self._format == pyaudio.paFloat32):
            return values.astype(np.dtype('f4')).tostring()
        else:
            values = np.rint( values * self._max_bit_value)
            return  values.astype(np.dtype('<i2')).tostring()

    #TODO JT 2014-04-01 - Ctrl-C hook
    def close(self):
        self._outstream.stop_stream()
        self._pa.terminate()
