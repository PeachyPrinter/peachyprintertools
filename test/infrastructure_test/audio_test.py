
import unittest
import sys
import os
import pyaudio
from mock import patch
import numpy

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

import test_helpers
from infrastructure.audio import AudioSetup, AudioWriter

class PyAudioSetupTests(unittest.TestCase, test_helpers.TestHelpers):
    maxDiff = None
    input_info  = {'defaultSampleRate': 44100.0, 'defaultLowOutputLatency': 0.011609977324263039, 'defaultLowInputLatency': 0.011609977324263039, 'maxInputChannels': 32L, 'structVersion': 2L, 'hostApi': 0L, 'index': 13L, 'defaultHighOutputLatency': 0.046439909297052155, 'maxOutputChannels': 32L, 'name': 'default', 'defaultHighInputLatency': 0.046439909297052155}
    output_info = {'defaultSampleRate': 44100.0, 'defaultLowOutputLatency': 0.011609977324263039, 'defaultLowInputLatency': 0.011609977324263039, 'maxInputChannels': 32L, 'structVersion': 2L, 'hostApi': 0L, 'index': 13L, 'defaultHighOutputLatency': 0.046439909297052155, 'maxOutputChannels': 32L, 'name': 'default', 'defaultHighInputLatency': 0.046439909297052155}

    @patch('pyaudio.PyAudio')
    def test_get_valid_sampling_options_should_list_options(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        mock_py_audio.get_default_input_device_info.return_value = self.input_info
        mock_py_audio.get_default_output_device_info.return_value = self.output_info
        mock_py_audio.is_format_supported.return_value = True
        all_options = [
                { 'sample_rate' : 44100, 'depth': '8 bit' },
                { 'sample_rate' : 44100, 'depth': '16 bit' },
                { 'sample_rate' : 44100, 'depth': '24 bit' },
                { 'sample_rate' : 44100, 'depth': '32 bit' },
                { 'sample_rate' : 44100, 'depth': '32 bit Floating Point' },
                { 'sample_rate' : 48000, 'depth': '8 bit'},
                { 'sample_rate' : 48000, 'depth': '16 bit' },
                { 'sample_rate' : 48000, 'depth': '24 bit' },
                { 'sample_rate' : 48000, 'depth': '32 bit' },
                { 'sample_rate' : 48000, 'depth': '32 bit Floating Point' },
                { 'sample_rate' : 96000, 'depth': '8 bit' },
                { 'sample_rate' : 96000, 'depth': '16 bit' },
                { 'sample_rate' : 96000, 'depth': '24 bit' },
                { 'sample_rate' : 96000, 'depth': '32 bit' },
                { 'sample_rate' : 96000, 'depth': '32 bit Floating Point' },
                { 'sample_rate' : 192000, 'depth': '8 bit' },
                { 'sample_rate' : 192000, 'depth': '16 bit' },
                { 'sample_rate' : 192000, 'depth': '24 bit' },
                { 'sample_rate' : 192000, 'depth': '32 bit' },
                { 'sample_rate' : 192000, 'depth': '32 bit Floating Point' },
            ]
        expected = {
            'input' : all_options,
            'output' : all_options
            }

        audio_setup = AudioSetup()

        actual = audio_setup.get_valid_sampling_options()
        self.assertListDict(expected['input'],actual['input'])
        self.assertListDict(expected['output'],actual['output'])

    @patch('pyaudio.PyAudio')
    def test_get_valid_sampling_options_should_return_none_if_input_channels_not_1(self, mock_PyAudio):
        no_channels = self.input_info.copy()
        no_channels['maxInputChannels'] = 0
        mock_py_audio = mock_PyAudio.return_value
        mock_py_audio.get_default_input_device_info.return_value = no_channels
        mock_py_audio.get_default_output_device_info.return_value = self.output_info
        mock_py_audio.is_format_supported.return_value = True

        audio_setup = AudioSetup()

        actual = audio_setup.get_valid_sampling_options()
        self.assertEquals([], actual['input'])

    @patch('pyaudio.PyAudio')
    def test_get_valid_sampling_options_should_return_none_if_output_channels_not_2(self, mock_PyAudio):
        no_channels = self.output_info.copy()
        no_channels['maxOutputChannels'] = 1
        mock_py_audio = mock_PyAudio.return_value
        mock_py_audio.get_default_input_device_info.return_value = no_channels
        mock_py_audio.get_default_output_device_info.return_value = self.output_info
        mock_py_audio.is_format_supported.return_value = True

        audio_setup = AudioSetup()

        actual = audio_setup.get_valid_sampling_options()
        self.assertEquals([], actual['output'])

    @patch('pyaudio.PyAudio')
    def test_get_valid_sampling_options_should_return_none_if_format_exception(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        mock_py_audio.get_default_input_device_info.return_value = self.input_info
        mock_py_audio.get_default_output_device_info.return_value = self.output_info
        mock_py_audio.is_format_supported.side_effect = ValueError(-9997)

        audio_setup = AudioSetup()

        actual = audio_setup.get_valid_sampling_options()
        self.assertEquals([], actual['output'])
        self.assertEquals([], actual['input'])


class AudioWriterTests(unittest.TestCase, test_helpers.TestHelpers):

    @patch('pyaudio.PyAudio')
    def test_should_terminate_when_close_is_called(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        
        audio_writer = AudioWriter(48000,'16 bit')
        audio_writer.close()
        mock_py_audio.is_format_supported.return_value = True
        mock_py_audio.terminate.assert_called_with()

    @patch('pyaudio.PyAudio')
    def test_should_open_a_stream_with_correct_data(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        sampling_frequency = 48000
        bit_depth = '16 bit'
        expected_format = pyaudio.paInt16
        expected_channels = 2
        expected_rate = 48000
        expected_frames_per_buffer = expected_rate / 8
        expected_output = True

        audio_writer = AudioWriter(sampling_frequency,bit_depth)
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
        bit_depth = '16 bit'
        sample_device_info = {
            'index': 0L, 'name': 'ALSA', 
            'defaultOutputDevice': 12L, 'type': 8L, 
            'deviceCount': 13L, 'defaultInputDevice': 12L, 
            'structVersion': 1L
        }

        mock_py_audio.get_default_host_api_info.return_value = sample_device_info
        mock_py_audio.is_format_supported.return_value = True

        audio_writer = AudioWriter(sampling_frequency,bit_depth)

        expected_format = pyaudio.paInt16
        expected_channels = 2
        expected_rate = 48000
        expected_frames_per_buffer = expected_rate / 8
        expected_output = True
        mock_py_audio.is_format_supported.assert_called_with(sampling_frequency,output_device=12,output_channels=2,output_format=pyaudio.paInt16)

    @patch('pyaudio.PyAudio')
    def test_should_throw_exception_for_unpossible_bit_depth(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        sampling_frequency = 48000
        bit_depth = '6 bit'

        with self.assertRaises(Exception):
            audio_writer = AudioWriter(sampling_frequency,bit_depth)

    @patch('pyaudio.PyAudio')
    def test_should_throw_exception_when_settings_unsupported(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        sampling_frequency = 48000
        bit_depth = '16 bit'
        sample_device_info = {
            'index': 0L, 'name': 'ALSA', 
            'defaultOutputDevice': 12L, 'type': 8L, 
            'deviceCount': 13L, 'defaultInputDevice': 12L, 
            'structVersion': 1L
        }

        mock_py_audio.get_default_host_api_info.return_value = sample_device_info
        mock_py_audio.is_format_supported.return_value = False

        with self.assertRaises(Exception):
            audio_writer = AudioWriter(sampling_frequency,bit_depth)


    @patch('pyaudio.PyAudio')
    def test_stream_should_be_started(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        sampling_frequency = 48000
        bit_depth = '16 bit'
        sample_device_info = { 'defaultInputDevice': 12L, }

        mock_py_audio.get_default_host_api_info.return_value = sample_device_info
        mock_py_audio.is_format_supported.return_value = True
        mock_outstream = mock_py_audio.open.return_value

        audio_writer = AudioWriter(sampling_frequency,bit_depth)

        mock_outstream.start_stream.assert_called_with()

    @patch('pyaudio.PyAudio')
    def test_stream_should_be_stopped_when_writer_stopped(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        sampling_frequency = 48000
        bit_depth = '16 bit'
        sample_device_info = { 'defaultInputDevice': 12L, }

        mock_py_audio.get_default_host_api_info.return_value = sample_device_info
        mock_py_audio.is_format_supported.return_value = True
        mock_outstream = mock_py_audio.open.return_value
        
        audio_writer = AudioWriter(sampling_frequency,bit_depth)
        audio_writer.close()

        mock_outstream.stop_stream.assert_called_with()

    @patch('pyaudio.PyAudio')
    def test_write_chunk_should_write_correct_frame_values(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        sampling_frequency = 48000
        bit_depth = '16 bit'
        sample_device_info = { 'defaultInputDevice': 12L, }

        mock_py_audio.get_default_host_api_info.return_value = sample_device_info
        mock_py_audio.is_format_supported.return_value = True
        mock_outstream = mock_py_audio.open.return_value
        mock_outstream.get_write_available.return_value = 2048
        
        audio_writer = AudioWriter(sampling_frequency,bit_depth)
        audio_writer.write_chunk(numpy.array([[1.0,1.0],[0.0,0.0],[-1.0,-1.0],[0.5,0.5]]))

        expected_frames = numpy.array([[32767,32767],[0,0],[-32767,-32767],[16384,16384]]).astype(numpy.dtype('<i2'))

        actual = ""

        self.assertEquals(4, mock_outstream.write.call_count)
        for h in range(0, len(mock_outstream.write.call_args_list)):
            for i in range(0, len(mock_outstream.write.call_args_list[h])):
                for j in range(0, len(mock_outstream.write.call_args_list[h][i])):
                    actual = actual + mock_outstream.write.call_args_list[h][i][j]

        self.assertEquals(expected_frames.tostring(),actual )

    @patch('pyaudio.PyAudio')
    def test_write_chunk_should_write_correct_frame_values_for_32_floating_point(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        sampling_frequency = 48000
        bit_depth = '32 bit Floating Point'
        sample_device_info = { 'defaultInputDevice': 12L, }

        mock_py_audio.get_default_host_api_info.return_value = sample_device_info
        mock_py_audio.is_format_supported.return_value = True
        mock_outstream = mock_py_audio.open.return_value
        mock_outstream.get_write_available.return_value = 2048
        
        audio_writer = AudioWriter(sampling_frequency,bit_depth)
        audio_writer.write_chunk(numpy.array([[1.0,1.0],[0.0,0.0],[-1.0,-1.0],[0.5,0.5]]))

        expected_frames = numpy.array([[1.0,1.0],[0.0,0.0],[-1.0,-1.0],[0.5,0.5]]).astype(numpy.dtype('<f4'))

        actual = ""

        self.assertEquals(4, mock_outstream.write.call_count)
        for h in range(0, len(mock_outstream.write.call_args_list)):
            for i in range(0, len(mock_outstream.write.call_args_list[h])):
                for j in range(0, len(mock_outstream.write.call_args_list[h][i])):
                    actual = actual + mock_outstream.write.call_args_list[h][i][j]

        self.assertEquals(expected_frames.tostring(),actual )

if __name__ == '__main__':
    unittest.main()