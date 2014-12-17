import unittest
import sys
import os
import logging
from mock import patch
import numpy

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

import test_helpers
from infrastructure.file import FileWriter

@patch('infrastructure.file.wave')
class FileWriterTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_write_chunk_writes_data_to_correct_file(self, mock_Wave):
        output_folder = 'somefolder'
        test_file_writer = FileWriter(48000,'16 bit',output_folder)
        mock_wave_writer = mock_Wave.open.return_value
        chunk = numpy.array([[1.0,1.0],[0.0,0.0],[-1.0,-1.0],[0.5,0.5]])

        expected_channels = 2
        expected_sampWidth = 2 # 16bits -> 2 bytes
        expected_framerate = 48000 
        expected_frames = numpy.array([[32767,32767],[0,0],[-32767,-32767],[16384,16384]]).astype(numpy.dtype('<i2')).tostring()
        
        test_file_writer.write_chunk(chunk)

        mock_Wave.open.assert_called_with(os.path.join(output_folder, 'layer_0.0_.wav'), 'wb')

        mock_wave_writer.setnchannels.assert_called_with(expected_channels)
        mock_wave_writer.setsampwidth.assert_called_with(expected_sampWidth)
        mock_wave_writer.setframerate.assert_called_with(expected_framerate)
        mock_wave_writer.writeframes.assert_called_with(expected_frames)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()