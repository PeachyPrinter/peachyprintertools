import logging
import pyaudio
import numpy as np
import math
import time
import types

audio_formats = {
            '32 bit Floating Point': pyaudio.paFloat32, 
            '32 bit': pyaudio.paInt32,
            '24 bit': pyaudio.paInt24,
            '16 bit': pyaudio.paInt16,
}

class AudioSetup(object):
    def __init__(self ):
        self._supported_rates = [ 44100, 48000 ]
        self._supported_depths = audio_formats.keys()

    def _get_depths_for_rate(self, pa, device_id, sample_rate, io_type):
        depths = []
        for depth in  self._supported_depths:
            try:
                format = audio_formats[depth]
                if io_type == 'input':
                    if pa.is_format_supported(rate=sample_rate,input_device=device_id, input_channels=1, input_format = format):
                        depths.append(depth)
                else:
                    if pa.is_format_supported(rate=sample_rate,output_device = device_id, output_channels=2, output_format= format):
                        depths.append(depth)
            except ValueError:
                pass
        return depths

    def get_valid_sampling_options(self):
        pa = None
        inputs = []
        outputs =  []
        try:
            pa = pyaudio.PyAudio()
            try:
                input_device = pa.get_default_input_device_info()
                output_device = pa.get_default_output_device_info()
            except IOError:
                return { 'input' : inputs, 'output' : outputs}
            input_device_id = input_device['index']
            output_device_id = output_device['index']
            for sample_rate in self._supported_rates:
                if input_device['maxInputChannels'] >= 1:
                    for depth in self._get_depths_for_rate(pa,input_device_id,sample_rate,'input'):
                        inputs.append({'sample_rate': sample_rate, 'depth' : depth})
                if output_device['maxOutputChannels'] >= 2:
                    for depth in self._get_depths_for_rate(pa,output_device_id,sample_rate,'output'):
                        outputs.append({'sample_rate': sample_rate, 'depth' : depth})
        finally:
            if pa:
                pa.terminate()
        return { 'input' : inputs, 'output' : outputs}


class DataWriter(object):
    
    def write_chunk(self, chunk):
        raise NotImplementedError('write_chunk unimplmented')

    def next_layer(self, layer):
        raise NotImplementedError('next_layer unimplmented')

    def close(self):
        pass

class AudioWriter(DataWriter):
    def __init__(self, sample_rate, bit_depth, buffer_divisor = 2):
        self._sample_rate = sample_rate
        self._bit_depth = bit_depth
        self._set_format_from_depth(bit_depth)
        self._pa = pyaudio.PyAudio()
        self._buffer_size = self._sample_rate / buffer_divisor

        logging.info("Audio Writer started with sample rate: %s, bit depth %s" % (self._sample_rate, self._bit_depth))
        try: 
            self._configuration_supported(self._sample_rate,self._format)
        except:
            logging.error("Audio configuration not supported; Sample Rate: %s; Sample Bits: %s " % (self._sample_rate, self._bit_depth))
            raise Exception("Audio configuration not supported; Sample Rate: %s; Sample Bits: %s " % (self._sample_rate, self._bit_depth) )
        
        self._outstream = self._pa.open(
            format=self._format,
            channels = 2,
            rate=self._sample_rate,
            output=True,
            frames_per_buffer=self._buffer_size 
            )
        self._outstream.start_stream()
        logging.info("Audio Writer started stream")


    def _configuration_supported(self, sample_rate, format):
        device_info = self._pa.get_default_host_api_info()
        default_device_id = device_info['defaultOutputDevice']
        logging.debug('Checking audio... id: %s, output_channels: %s, output_format: %s, sample rate: %s ' %(default_device_id, 2, format,sample_rate))
        supported = self._pa.is_format_supported(sample_rate,output_device=default_device_id,output_channels=2,output_format=format)
        return supported

    def _set_format_from_depth(self,depth):
        self._format = audio_formats[depth]
        if self._format ==  pyaudio.paInt8:
            self._max_bit_value = math.pow(2, 8 - 1) - 1.0
        elif self._format ==  pyaudio.paInt16:
            self._max_bit_value = math.pow(2, 16 - 1) - 1.0
        elif self._format ==  pyaudio.paInt24:
            self._max_bit_value = math.pow(2, 24 - 1) - 1.0
        elif self._format ==  pyaudio.paInt32:
            self._max_bit_value = math.pow(2, 32 - 1) - 1.0
        elif self._format ==  pyaudio.paFloat32:
            self._max_bit_value = 1.0
        else:
            logging.error("Bit depth ![%s]! specified is not supported" % depth)
            raise Exception("Bit depth ![%s]! specified is not supported" % depth)

    def write_chunk(self, chunk):
        # start = time.time()
        data = np.array(list(chunk))
        frames = self._to_frame(data)
        self._outstream.write(frames)
        # logging.debug('Wrote chunk: %s' % (time.time() - start))

    def _to_frame(self, values):
        if (self._format == pyaudio.paFloat32):
            return values.astype(np.dtype('f4')).tostring()
        else:
            values = np.rint( values * self._max_bit_value)
            return  values.astype(np.dtype('<i2')).tostring()

    def close(self):
        logging.info("Shutting down audio stream")
        self._outstream.stop_stream()
        self._pa.terminate()
