import unittest
import sys
import os
import pyaudio
from mock import patch

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

import test_helpers
from infrastructure.audio_writer import AudioWriter


class AudioWriterTests(unittest.TestCase, test_helpers.TestHelpers):

    @patch('pyaudio.PyAudio')
    def test_should_terminate_when_close_is_called(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        
        audio_writer = AudioWriter(48000,16)
        audio_writer.close()
        mock_py_audio.is_format_supported.return_value = True
        mock_py_audio.terminate.assert_called_with()

    @patch('pyaudio.PyAudio')
    def test_should_open_a_stream_with_correct_data(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        sampling_frequency = 48000
        bit_rate = 16
        expected_format = pyaudio.paInt16
        expected_channels = 2
        expected_rate = 48000
        expected_frames_per_buffer = expected_rate / 8
        expected_output = True

        audio_writer = AudioWriter(sampling_frequency,bit_rate)
        mock_py_audio.is_format_supported.return_value = True
        mock_py_audio.open.assert_called_with(format=expected_format,
                                                channels=expected_channels,
                                                rate=expected_rate,
                                                output=expected_output,
                                                frames_per_buffer=expected_frames_per_buffer )


    @patch('pyaudio.PyAudio')
    def test_verifies_support_for_stream_settings(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        sampling_frequency = 48000
        bit_rate = 16
        sample_device_info = {
            'index': 0L, 'name': u'ALSA', 
            'defaultOutputDevice': 12L, 'type': 8L, 
            'deviceCount': 13L, 'defaultInputDevice': 12L, 
            'structVersion': 1L
        }

        mock_py_audio.get_default_host_api_info.return_value = sample_device_info
        mock_py_audio.is_format_supported.return_value = True

        audio_writer = AudioWriter(sampling_frequency,bit_rate)

        expected_format = pyaudio.paInt16
        expected_channels = 2
        expected_rate = 48000
        expected_frames_per_buffer = expected_rate / 8
        expected_output = True
        mock_py_audio.is_format_supported.assert_called_with(sampling_frequency,output_device=12,output_channels=2,output_format=pyaudio.paInt16)

if __name__ == '__main__':
    unittest.main()