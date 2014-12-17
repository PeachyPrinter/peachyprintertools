import wave
import os
import math
import numpy as np
from domain.data_writer import DataWriter

audio_formats = { 
            '32 bit': 4,
            '24 bit': 3,
            '16 bit': 2,
}

class FileWriter(DataWriter):
    def __init__(self, sample_rate, bit_depth, base_directory):
        self._sample_rate = sample_rate
        # if bit_depth in audio_formats.keys():
        self._depth = audio_formats[bit_depth]
        self._base_directory = base_directory
        self._current_file = None
        self._current_layer_height = 0.0
        self._max_bit_value = math.pow(2, self._depth * 8 - 1) - 1.0

    def write_chunk(self, chunk):
        if not self._current_file:
            self._create_file()
        data = np.array(list(chunk))
        frames = self._to_frame(data)
        self._current_file.writeframes(frames)

    def _to_frame(self, values):
        values = np.rint( values * self._max_bit_value)
        return  values.astype(np.dtype('<i2')).tostring()

    def next_layer(self, layer):
        raise NotImplementedError('next_layer unimplmented')

    def close(self):
        pass

    def _create_file(self):
        # if self._current_file:
        #     raise Exception("File already open")
        filename = os.path.join(self._base_directory, 'layer_%s_.wav' % self._current_layer_height)
        self._current_file = wave.open(filename, 'wb')
        self._current_file.setnchannels(2)
        self._current_file.setsampwidth(self._depth)
        self._current_file.setframerate(self._sample_rate)