import unittest
import sys
import os
from mock import patch, Mock, call
import wave
import time
import random
import struct
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.drip_based_zaxis import DripDetector, Threshold, AudioDripZAxis
from infrastructure.audio import audio_formats
from infrastructure.commander import NullCommander


class DripDetectorTests(unittest.TestCase):

    def setUp(self):
        self.test_file_path = os.path.join(os.path.dirname(__file__), 'test_data')
        self.calls = 0
        self.drips = 0
        self.average_drips = 0
        self.drip_history = []

    def teardown(self):
        pass

    def call_back(self, drips, average_drips, drip_history):
        self.calls += 1
        self.drips = drips
        self.average_drips = average_drips
        self.drip_history = drip_history

    def test_audio_samples(self):
        files = [[file_name, int(file_name.split('_')[0])] for file_name in os.listdir(self.test_file_path) if file_name.endswith('.wav')]

        for a_file in files:
            full_path = os.path.join(self.test_file_path, a_file[0])
            expected_drips = a_file[1]
            data_file = wave.open(full_path, 'rb')
            sample_rate = data_file.getframerate()
            no_frames = data_file.getnframes()
            frames = data_file.readframes(no_frames)
            dd = DripDetector(sample_rate)
            dd.process_frames(frames)
            self.assertEqual(expected_drips, dd.drips())

    def test_should_process_quickly(self):
        a_file = '22_drips_speeding_up.wav'
        full_path = os.path.join(self.test_file_path, a_file)
        data_file = wave.open(full_path, 'rb')
        sample_rate = data_file.getframerate()
        no_frames = data_file.getnframes()
        frames = data_file.readframes(no_frames)
        dd = DripDetector(sample_rate, call_back=self.call_back)

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
        samples = len([struct.Struct("h").unpack_from(frames, offset)[0] for offset in range(0, len(frames), struct.Struct("h").size)])
        expected_call_backs = int((samples * 1.0 / sample_rate * 1.0) * call_backs_per_second)
        expected_average = 7.6
        expected_history = [4619, 22484, 35208, 45068, 54232, 63228, 71914, 80447, 88759, 96840, 104792, 112544, 120148, 127470, 134588, 141474, 148171, 154629, 160937, 167060, 172897, 178464]
        dd = DripDetector(sample_rate, call_back=self.call_back, calls_back_per_second=call_backs_per_second)

        dd.process_frames(frames)

        self.assertEquals(expected_call_backs, self.calls)
        self.assertEquals(22, self.drips)
        self.assertAlmostEquals(expected_average, self.average_drips, places=1)
        self.assertEquals(expected_history, self.drip_history,)


class ThresholdTests(unittest.TestCase):
    def test_threshold_is_fast(self):
        data_set = [random.randrange(-32768, 32766) for i in range(0, 48000 * 10)]
        t = Threshold(48000)
        starttime = time.time()
        t.add_value(data_set)
        endtime = time.time()
        delta = endtime - starttime
        self.assertTrue(delta < 0.5, delta)

    def test_returns_the_average_floor(self):
        expected_floor = 1200
        data_set = [expected_floor for i in range(0, 48000)]
        t = Threshold(48000)
        t.add_value(data_set)
        actual = t.threshold()
        self.assertEquals(expected_floor, actual)

    def test_returns_the_average_floor_when_negitive(self):
        floor = -1200
        expected_floor = 1200.0
        data_set = [floor for i in range(0, 48000)]
        t = Threshold(48000)
        t.add_value(data_set)
        actual = t.threshold()
        self.assertEquals(expected_floor, actual)

    def test_returns_the_average_for_one_second(self):
        expected_floor = 1200.0
        data_set = [0 for i in range(0, 48000)]
        [data_set.append(expected_floor) for i in range(0, 48000)]
        t = Threshold(48000)
        t.add_value(data_set)
        actual = t.threshold()
        self.assertEquals(expected_floor, actual)


class MockPyAudioInStream(object):
    _read_frames = 0

    def __init__(self, file_name='1_drip_fast.wav'):
        test_file = os.path.join(os.path.dirname(__file__), 'test_data', file_name)
        self._wave_data = wave.open(test_file, 'rb')
        self.frames = self._wave_data.getnframes()
        self.chunk_size = 1024
        self.closed = False
        self.calls = 0
        self.get_availables = 0

    def read(self, frames):
        self.get_availables = 0
        self.calls += 1
        self._read_frames += frames
        time.sleep(frames / 48000)
        return self._wave_data.readframes(frames)

    def get_read_available(self):
        possible_frames = self.frames - self._read_frames
        if (possible_frames >= self.chunk_size):
            self.get_availables += 1
            return self.chunk_size * self.get_availables
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
        self.calls = 0
        self.drips = 0
        self.height = 0
        self.drips_per_second = 0
        self.drip_history = []

    def tearDown(self):
        if self.adza:
            self.adza.close()
        if self.stream and not self.stream.closed:
            self.stream.close()
            print("*" * 30)
            print("WARNING AUDIO STREAM NOT CLOSED AudioDripZAxisTests")
            print("*" * 30)

    def setup_mock(self, mock_PyAudio, file_name='1_drip_fast.wav'):
        self.stream = MockPyAudioInStream(file_name)
        mock_pyaudio = mock_PyAudio.return_value
        mock_pyaudio.get_default_input_device_info.return_value = {'index': 0}
        mock_pyaudio.open.return_value = self.stream
        return mock_pyaudio

    def wait_for_stream(self):
        while self.stream.get_read_available() > 0:
            time.sleep(0.1)

    def call_back(self, drips, height, drips_per_second, drip_history=[]):
        self.calls += 1
        self.drips = drips
        self.height = height
        self.drips_per_second = drips_per_second
        self.drip_history = drip_history

    def test_shuts_down_correctly(self, mock_PyAudio):
        mock_pyaudio = self.setup_mock(mock_PyAudio)

        drips_per_mm = 1
        sample_rate = 48000
        bit_depth = '16 bit'
        self.adza = AudioDripZAxis(drips_per_mm, 0.0, sample_rate, bit_depth, NullCommander(), '', '')

        print("Starting tests 1")
        self.adza.start()
        print("Starting tests 2")
        time.sleep(0.1)
        self.adza.close()
        print("Starting tests 3")
        self.assertTrue(self.adza.shutdown)
        mock_pyaudio.terminate.assert_called_with()

    def test_should_open_stream_correctly(self, mock_PyAudio):
        mock_pyaudio = self.setup_mock(mock_PyAudio)

        drips_per_mm = 1
        sample_rate = 48000
        bit_depth = '16 bit'
        self.adza = AudioDripZAxis(drips_per_mm, 0.0, sample_rate, bit_depth, NullCommander(), '', '')

        self.adza.start()
        self.wait_for_stream()
        self.adza.close()

        mock_pyaudio.open.assert_called_with(
            rate=sample_rate,
            channels=1,
            input=True,
            format=audio_formats[bit_depth],
            frames_per_buffer=sample_rate / 2
            )

    @patch.object(DripDetector, 'process_frames')
    def test_should_call_a_DripDetector_with_buffered_data_correctly(self, mock_process_frames, mock_PyAudio):
        self.setup_mock(mock_PyAudio, file_name='14_drips.wav')

        drips_per_mm = 1
        sample_rate = 48000
        bit_depth = '16 bit'
        self.adza = AudioDripZAxis(drips_per_mm, 0.0, sample_rate, bit_depth, NullCommander(), '', '')

        self.adza.start()
        self.wait_for_stream()
        self.adza.close()

        self.assertTrue(self.stream.calls >= mock_process_frames.call_count, "Was: %s, should be less then %s" % (mock_process_frames.call_count, self.stream.calls))

    def test_should_call_back_when_DripDetector_calls_back(self, mock_PyAudio):
        self.setup_mock(mock_PyAudio)

        drips_per_mm = 1
        sample_rate = 48000
        bit_depth = '16 bit'
        self.adza = AudioDripZAxis(drips_per_mm, 0.0, sample_rate, bit_depth, NullCommander(), '', '', self.call_back)

        self.adza.start()
        self.wait_for_stream()
        self.adza.close()

        self.assertEquals(2, self.calls)
        self.assertEquals(1, self.drips)
        self.assertEquals(1, self.height)
        self.assertAlmostEquals(58.5, self.drips_per_second, places=0)
        self.assertEqual(1, self.adza.current_z_location_mm())

    def test_should_be_able_to_set_call_back(self, mock_PyAudio):
        self.setup_mock(mock_PyAudio)

        drips_per_mm = 1
        sample_rate = 48000
        bit_depth = '16 bit'
        self.adza = AudioDripZAxis(drips_per_mm, 0.0, sample_rate, bit_depth, NullCommander(), '', '')
        self.adza.set_call_back(self.call_back)

        self.adza.start()
        self.wait_for_stream()
        self.adza.close()

        self.assertEquals(2, self.calls)
        self.assertEquals(1, self.drips)
        self.assertEquals(1, self.height)
        self.assertEquals([820], self.drip_history)
        self.assertAlmostEquals(58.4, self.drips_per_second, places=0)
        self.assertEqual(1, self.adza.current_z_location_mm())

    def test_should_be_able_to_set_drips_per_mm(self, mock_PyAudio):
        self.setup_mock(mock_PyAudio)

        original_drips_per_mm = 1
        new_drips_per_mm = 0.1
        sample_rate = 48000
        bit_depth = '16 bit'
        self.adza = AudioDripZAxis(original_drips_per_mm, 0.0, sample_rate, bit_depth, NullCommander(), '', '')
        self.adza.set_drips_per_mm(new_drips_per_mm)
        
        self.adza.start()
        self.wait_for_stream()
        self.adza.close()

        self.assertEqual(10.0, self.adza.current_z_location_mm())

    def test_reset_should_set_drips_to_0(self, mock_PyAudio):
        self.setup_mock(mock_PyAudio)

        drips_per_mm = 1
        sample_rate = 48000
        bit_depth = '16 bit'
        self.adza = AudioDripZAxis(drips_per_mm, 0.0, sample_rate, bit_depth, NullCommander(), '', '')        
        self.adza.start()
        self.wait_for_stream()
        self.adza.close()
        self.adza.reset()

        self.assertEqual(0.0, self.adza.current_z_location_mm())

    def test_move_to_should_call_commander_with_dripper_on_command(self, mock_PyAudio):
        self.setup_mock(mock_PyAudio)

        drips_per_mm = 1
        sample_rate = 48000
        bit_depth = '16 bit'
        commander = Mock()
        expected_drip_on_command = 'on'
        expected_drip_off_command = 'off'
        self.adza = AudioDripZAxis(
            drips_per_mm,
            0.0,
            sample_rate,
            bit_depth,
            commander,
            expected_drip_on_command,
            expected_drip_off_command
            )
        self.adza.start()
        self.adza.move_to(300)
        self.wait_for_stream()
        self.adza.close()

        commander.send_command.assert_has_calls([call(expected_drip_on_command), call(expected_drip_off_command)])

    def test_move_to_should_call_commander_with_dripper_off_command(self, mock_PyAudio):
        self.setup_mock(mock_PyAudio)

        drips_per_mm = 1
        sample_rate = 48000
        bit_depth = '16 bit'
        commander = Mock()
        expected_drip_on_command = 'on'
        expected_drip_off_command = 'off'
        self.adza = AudioDripZAxis(
            drips_per_mm,
            0.0,
            sample_rate,
            bit_depth,
            commander,
            expected_drip_on_command,
            expected_drip_off_command
            )

        self.adza.start()
        self.adza.move_to(-300)
        self.wait_for_stream()
        self.adza.close()

        commander.send_command.assert_has_calls([call(expected_drip_off_command)])

    # def test_stop_should_call_commander_with_dripper_off_command(self, mock_PyAudio):
    #     self.setup_mock(mock_PyAudio)

    #     drips_per_mm = 1
    #     sample_rate = 48000
    #     bit_depth = '16 bit'
    #     commander = Mock()
    #     expected_drip_on_command = 'on'
    #     expected_drip_off_command = 'off'
    #     self.adza = AudioDripZAxis(
    #         drips_per_mm,
    #         0.0,
    #         sample_rate,
    #         bit_depth,
    #         commander,
    #         expected_drip_on_command,
    #         expected_drip_off_command
    #         )

    #     self.adza.start()
    #     self.adza.move_to(300)
    #     self.wait_for_stream()
    #     self.adza.close()

    #     commander.send_command.assert_called_with(expected_drip_off_command)

    def test_current_z_location_should_respond_with_dripped_height_and_starting_height(self, mock_PyAudio):
        self.setup_mock(mock_PyAudio)
        starting_height = 7.7
        expected_end_height = starting_height + 1.0
        drips_per_mm = 1
        sample_rate = 48000
        bit_depth = '16 bit'
        self.adza = AudioDripZAxis(
            drips_per_mm, starting_height, sample_rate, bit_depth, NullCommander(), '', ''
            )

        self.assertEquals(starting_height, self.adza.current_z_location_mm())

        self.adza.start()
        self.wait_for_stream()
        self.adza.close()

        self.assertEquals(expected_end_height, self.adza.current_z_location_mm())


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    logging.info("Starting tests for drip_based_zaxis_tests")
    unittest.main()
