import unittest
import sys
import os
from mock import patch, Mock
from test_helpers import TestHelpers
import wave
import pyaudio 
import time

from infrastructure.drip_based_zaxis import DripBasedZAxis

class MockPyAudioInputStream(object):
    _read_frames = 0
    def __init__(self, wavefile, chunk_size = 1024):
        self._wave_data = wave.open(wavefile, 'rb')
        self._chunk_size = chunk_size
    
    def read(self,frames):
        self._read_frames += frames
        return self._wave_data.readframes(frames)

    def get_read_available(self):
        possible_frames = self._wave_data.getnframes() - self._read_frames
        if (possible_frames >= self._chunk_size):
            return self._chunk_size
        else:
            return possible_frames

    def start_stream(self):
        pass

    def stop_stream(self):
        pass

    def close(self):
        self._wave_data.close()


class DripBasedZAxisTests(unittest.TestCase):
    test_file_path = os.path.join(os.path.dirname(__file__), 'test_data')
    stream = None

    def wait_for_stream(self):
        if self.stream:
            while self.stream.get_read_available() > 0:
                time.sleep(0.01)

    def tearDown(self):
        try:
            self.stream.close()
        except:
            pass

    def test_drip_zaxis_should_report_height_of_0_when_stopped(self):
        drips_per = 1
        drip_zaxis = DripBasedZAxis(drips_per)
        self.assertEqual(0, drip_zaxis.current_z_location_mm())

    @patch('pyaudio.PyAudio')
    def test_drip_zaxis_should_report_1_drips_after_1_slow_drips(self, mock_pyaudio):
        drips_per = 1
        wave_file = os.path.join(self.test_file_path, '1_drip.wav')
        self.stream = MockPyAudioInputStream(wave_file)

        my_mock_pyaudio = mock_pyaudio.return_value
        my_mock_pyaudio.open.return_value = self.stream

        drip_zaxis = DripBasedZAxis(drips_per)
        drip_zaxis.start()
        self.wait_for_stream()
        drip_zaxis.stop()
        self.assertEqual(1, drip_zaxis.current_z_location_mm())

    @patch('pyaudio.PyAudio')
    def test_drip_zaxis_should_not_round_up_drips(self, mock_pyaudio):
        drips_per = 10
        wave_file = os.path.join(self.test_file_path, '1_drip.wav')
        self.stream = MockPyAudioInputStream(wave_file)

        my_mock_pyaudio = mock_pyaudio.return_value
        my_mock_pyaudio.open.return_value = self.stream

        drip_zaxis = DripBasedZAxis(drips_per)
        drip_zaxis.start()
        self.wait_for_stream()
        drip_zaxis.stop()
        self.assertEqual(0.1, drip_zaxis.current_z_location_mm())

    @patch('pyaudio.PyAudio')
    def test_drip_zaxis_should_report_1_drips_after_1_fast_drips(self, mock_pyaudio):
        drips_per = 1
        wave_file = os.path.join(self.test_file_path, '1_drip_fast.wav')
        self.stream = MockPyAudioInputStream(wave_file)

        my_mock_pyaudio = mock_pyaudio.return_value
        my_mock_pyaudio.open.return_value = self.stream

        drip_zaxis = DripBasedZAxis(drips_per)
        drip_zaxis.start()
        self.wait_for_stream()
        drip_zaxis.stop()
        self.assertEqual(1, drip_zaxis.current_z_location_mm())

    @patch('pyaudio.PyAudio')
    def test_drip_zaxis_should_report_14_drips_after_14_drips(self, mock_pyaudio):
        drips_per = 1
        wave_file = os.path.join(self.test_file_path, '14_drips.wav')
        self.stream = MockPyAudioInputStream(wave_file)

        my_mock_pyaudio = mock_pyaudio.return_value
        my_mock_pyaudio.open.return_value = self.stream

        drip_zaxis = DripBasedZAxis(drips_per)
        drip_zaxis.start()
        self.wait_for_stream()
        drip_zaxis.stop()
        self.assertEqual(14, drip_zaxis.current_z_location_mm())

    @patch('pyaudio.PyAudio')
    def test_drip_zaxis_should_report_22_drips_after_22_drips_speed_up(self, mock_pyaudio):
        drips_per = 1
        wave_file = os.path.join(self.test_file_path, '22_drips_speeding_up.wav')
        self.stream = MockPyAudioInputStream(wave_file)

        my_mock_pyaudio = mock_pyaudio.return_value
        my_mock_pyaudio.open.return_value = self.stream

        drip_zaxis = DripBasedZAxis(drips_per)
        drip_zaxis.start()
        self.wait_for_stream()
        drip_zaxis.stop()
        self.assertEqual(22, drip_zaxis.current_z_location_mm())

    @patch('pyaudio.PyAudio')
    def test_drip_zaxis_should_report_2_drips_if_started_half_way_though_drip(self, mock_pyaudio):
        drips_per = 1
        wave_file = os.path.join(self.test_file_path, 'half_and_1_drips.wav')
        self.stream = MockPyAudioInputStream(wave_file)

        my_mock_pyaudio = mock_pyaudio.return_value
        my_mock_pyaudio.open.return_value = self.stream

        drip_zaxis = DripBasedZAxis(drips_per)
        drip_zaxis.start()
        self.wait_for_stream()
        drip_zaxis.stop()
        self.assertEqual(2, drip_zaxis.current_z_location_mm())


    @patch('pyaudio.PyAudio')
    def test_reset_should_set_height_back_specified_height(self, mock_pyaudio):
        drips_per = 1
        wave_file = os.path.join(self.test_file_path, '1_drip_fast.wav')
        self.stream = MockPyAudioInputStream(wave_file)
        my_mock_pyaudio = mock_pyaudio.return_value
        my_mock_pyaudio.open.return_value = self.stream
        drip_zaxis = DripBasedZAxis(drips_per)
        drip_zaxis.start()
        self.wait_for_stream()
        inital_result = drip_zaxis.current_z_location_mm()

        drip_zaxis.reset()
        reset_result = drip_zaxis.current_z_location_mm()
        drip_zaxis.stop()

        self.assertEqual(1, inital_result)
        self.assertEqual(0, reset_result)

    @patch.object(pyaudio.PyAudio, 'get_default_input_device_info')
    @patch.object(pyaudio.PyAudio, 'open')
    @patch.object(pyaudio.PyAudio, 'is_format_supported')
    def test_should_respected_specified_sample_rate_and_bit_depth(self, mock_is_format_supported, mock_open, mock_get_default_input_device_info):
        input_device = 1
        sample_rate = 48000
        expected_buffer_size = 6000
        expected_format = pyaudio.paInt16
        wave_file = os.path.join(self.test_file_path, '1_drip_fast.wav')
        self.stream = MockPyAudioInputStream(wave_file)
        mock_open.return_value = self.stream
        mock_get_default_input_device_info.return_value = { 'index' : input_device}
        
        drip_zaxis = DripBasedZAxis(1,sample_rate=sample_rate, bit_depth = u'16 bit')
        drip_zaxis.start()
        self.wait_for_stream()
        drip_zaxis.stop()
        
        mock_is_format_supported.assert_called_with(sample_rate, input_device = input_device, input_channels = 1,input_format = expected_format)
        mock_open.assert_called_with(format = expected_format, input= True, frames_per_buffer = expected_buffer_size,channels =1, rate = sample_rate)

