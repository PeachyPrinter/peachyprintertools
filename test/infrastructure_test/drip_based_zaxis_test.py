import unittest
import sys
import os
from mock import patch, Mock
import wave
import pyaudio 
import time
import random
import struct

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from test_helpers import TestHelpers
 
from infrastructure.drip_based_zaxis import DripDetector, Threshold, AudioDripZAxis
from infrastructure.audio import audio_formats

class DripDetectorTests(unittest.TestCase):

    def setUp(self):
        self.test_file_path = os.path.join(os.path.dirname(__file__), 'test_data')
        self.calls = 0
        self.drips = 0
        self.average_drips = 0

    def teardown(self):
        pass

    def call_back(self, drips, average_drips):
        self.calls += 1
        self.drips = drips
        self.average_drips = average_drips

    def test_audio_samples(self):
        files = [ [file_name, int(file_name.split('_')[0])] for file_name in os.listdir(self.test_file_path) if file_name.endswith('.wav') ]

        for a_file in files:
            full_path = os.path.join(self.test_file_path, a_file[0])
            expected_drips = a_file[1]
            data_file = wave.open(full_path, 'rb')
            sample_rate = data_file.getframerate()
            bit_depth = data_file.getsampwidth()
            no_frames = data_file.getnframes()
            frames = data_file.readframes(no_frames)
            # print('Processing %s at %s, %s' % (a_file[0], sample_rate, bit_depth ))
            dd = DripDetector(sample_rate)
            dd.process_frames(frames)
            # print('Processed %s' % a_file[0])
            self.assertEqual(expected_drips, dd.drips())

    def test_should_process_quickly(self):
        a_file = '22_drips_speeding_up.wav'
        full_path = os.path.join(self.test_file_path, a_file)

        data_file = wave.open(full_path, 'rb')
        sample_rate = data_file.getframerate()
        no_frames = data_file.getnframes()
        frames = data_file.readframes(no_frames)
        dd = DripDetector(sample_rate,call_back = self.call_back)
        starttime = time.time()
        dd.process_frames(frames)
        endtime = time.time()
        delta = endtime - starttime
        self.assertTrue(delta < 2.0, delta)

    def test_should_call_back_every_x_samples_if_call_back_provided(self):
        a_file = '22_drips_speeding_up.wav'
        full_path = os.path.join(self.test_file_path, a_file)

        data_file = wave.open(full_path, 'rb')
        sample_rate = data_file.getframerate()
        no_frames = data_file.getnframes()
        frames = data_file.readframes(no_frames)
        call_backs_per_second = 15
        samples = len([ struct.Struct("h").unpack_from(frames, offset)[0] for offset in range(0, len(frames), struct.Struct("h").size) ])
        expected_call_backs = int((samples * 1.0 / sample_rate * 1.0) * call_backs_per_second)
        expected_average = 7.6
        dd = DripDetector(sample_rate, call_back = self.call_back, calls_back_per_second = call_backs_per_second)
        
        dd.process_frames(frames)
        
        self.assertEquals(expected_call_backs, self.calls)
        self.assertEquals(22, self.drips)
        self.assertAlmostEquals(expected_average,self.average_drips, places = 1)

class ThresholdTests(unittest.TestCase):
    def test_threshold_is_fast(self):
        data_set = [ random.randrange(-32768, 32766) for i in range(0,48000 * 10) ]
        t = Threshold(48000)
        starttime = time.time()
        t.add_value(data_set)
        a = t.threshold()
        endtime = time.time()
        delta = endtime - starttime
        self.assertTrue(delta < 0.5, delta)

    def test_returns_the_average_floor(self):
        expected_floor = 1200
        data_set = [ expected_floor for i in range(0,48000) ]
        t = Threshold(48000)
        t.add_value(data_set)
        actual = t.threshold()
        self.assertEquals(expected_floor,actual)

    def test_returns_the_average_floor_when_negitive(self):
        floor = -1200
        expected_floor = 1200.0
        data_set = [ floor for i in range(0,48000) ]
        t = Threshold(48000)
        t.add_value(data_set)
        actual = t.threshold()
        self.assertEquals(expected_floor,actual)

    def test_returns_the_average_for_one_second(self):
        expected_floor = 1200.0
        data_set = [ 0 for i in range(0,48000) ]
        [ data_set.append(expected_floor)  for i in range(0,48000) ]
        t = Threshold(48000)
        t.add_value(data_set)
        actual = t.threshold()
        self.assertEquals(expected_floor,actual)

class MockPyAudioInStream(object):
    _read_frames = 0
    def __init__(self, file_name = '1_drip_fast.wav'):
        test_file = os.path.join(os.path.dirname(__file__), 'test_data', file_name)
        self._wave_data = wave.open(test_file, 'rb')
        self.frames = self._wave_data.getnframes()
        self.chunk_size = 1024
        self.closed = False
    
    def read(self,frames):
        self._read_frames += frames
        return self._wave_data.readframes(frames)

    def get_read_available(self):
        possible_frames = self.frames - self._read_frames
        if (possible_frames >= self.chunk_size):
            return self.chunk_size
        else:
            return possible_frames

    def start_stream(self):
        pass

    def stop_stream(self):
        pass

    def close(self):
        self._wave_data.close()
        self.closed = True

@patch('pyaudio.PyAudio')
class AudioDripZAxisTests(unittest.TestCase, ):
    def setUp(self):
        self.adza = None
        self.stream = None
        # Call Back 
        self.calls = 0
        self.drips = 0
        self.height = 0
        self.drips_per_second = 0
    
    def tearDown(self):
        if self.adza:
            self.adza.stop()
        if self.stream and not self.stream.closed:
            self.stream.close()
            print("*" * 30)
            print("WARNING AUDIO STREAM NOT CLOSED AudioDripZAxisTests")
            print("*" * 30)

    def setup_mock(self, mock_PyAudio, file_name = '1_drip_fast.wav'):
        self.stream = MockPyAudioInStream(file_name)
        mock_pyaudio = mock_PyAudio.return_value
        mock_pyaudio.get_default_input_device_info.return_value = { 'index' : 0 }
        mock_pyaudio.open.return_value = self.stream
        return mock_pyaudio
    
    def wait_for_stream(self):
        while self.stream.get_read_available() > 0:
            time.sleep(0.1)

    def call_back(self, drips, height, drips_per_second):
        self.calls += 1
        self.drips = drips
        self.height = height
        self.drips_per_second = drips_per_second

    def test_shuts_down_correctly(self,mock_PyAudio):
        mock_pyaudio = self.setup_mock(mock_PyAudio)

        drips_per_mm = 1
        sample_rate = 48000
        bit_depth = '16 bit'
        self.adza = AudioDripZAxis(drips_per_mm,sample_rate,bit_depth)

        self.adza.start()
        self.adza.stop()
        self.assertFalse(self.adza.is_alive())
        mock_pyaudio.terminate.assert_called_with()

    def test_should_open_stream_correctly(self,mock_PyAudio):
        mock_pyaudio = self.setup_mock(mock_PyAudio)

        drips_per_mm = 1
        sample_rate = 48000
        bit_depth = '16 bit'
        self.adza = AudioDripZAxis(drips_per_mm,sample_rate,bit_depth)

        self.adza.start()
        self.adza.stop()

        mock_pyaudio.open.assert_called_with(
            rate = sample_rate, 
            channels = 1,
            input = True, 
            format=audio_formats[bit_depth],
            frames_per_buffer=sample_rate / 2
            )

    @patch.object(DripDetector,'process_frames')
    def test_should_call_a_DripDetector_with_buffered_data_correctly(self, mock_process_frames,mock_PyAudio):
        mock_pyaudio = self.setup_mock(mock_PyAudio, file_name = '14_drips.wav')

        drips_per_mm = 1
        sample_rate = 48000
        bit_depth = '16 bit'
        self.adza = AudioDripZAxis(drips_per_mm,sample_rate,bit_depth)
        expected_call_count = int(self.stream.frames * 1.0 / self.stream.chunk_size)

        self.adza.start()
        self.wait_for_stream()
        self.adza.stop()

        self.assertTrue(expected_call_count < mock_process_frames.call_count)

    def test_should_call_back_when_DripDetector_calls_back(self,mock_PyAudio):
        mock_pyaudio = self.setup_mock(mock_PyAudio)

        drips_per_mm = 1
        sample_rate = 48000
        bit_depth = '16 bit'
        self.adza = AudioDripZAxis(drips_per_mm,sample_rate,bit_depth, self.call_back)
        
        self.adza.start()
        self.wait_for_stream()
        self.adza.stop()

        self.assertEquals(2, self.calls)
        self.assertEquals(1, self.drips)
        self.assertEquals(1, self.height)
        self.assertAlmostEquals(55.3, self.drips_per_second, places =1)
        self.assertEqual(1, self.adza.current_z_location_mm())

    def test_should_be_able_to_set_call_back(self,mock_PyAudio):
        mock_pyaudio = self.setup_mock(mock_PyAudio)

        drips_per_mm = 1
        sample_rate = 48000
        bit_depth = '16 bit'
        self.adza = AudioDripZAxis(drips_per_mm,sample_rate,bit_depth)
        self.adza.set_call_back(self.call_back)
        
        self.adza.start()
        self.wait_for_stream()
        self.adza.stop()

        self.assertEquals(2, self.calls)
        self.assertEquals(1, self.drips)
        self.assertEquals(1, self.height)
        self.assertAlmostEquals(55.3, self.drips_per_second, places =1)
        self.assertEqual(1, self.adza.current_z_location_mm())

if __name__ == '__main__':
    unittest.main()
