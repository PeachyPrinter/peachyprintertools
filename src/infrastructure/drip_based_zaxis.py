import threading
import pyaudio
import struct
import time
import logging
import numpy as np
from audio import audio_formats
from domain.zaxis import ZAxis


class Threshold(object):
    def __init__(self, sample_rate):
        self._samples = np.array([0])
        self._max_samples = sample_rate / 2

    def threshold(self):
        self._samples = self._samples[-1 * self._max_samples:]
        return np.mean(self._samples)

    def add_value(self, values):
        self._samples = np.append(self._samples, np.absolute(values))


class DripDetector(object):
    def __init__(self, sample_rate, call_back=None, calls_back_per_second=15):
        self.MONO_WAVE_STRUCT = struct.Struct("h")
        self.sample_rate = sample_rate

        self._drips = 0
        self._threshold = Threshold(self.sample_rate)
        self._indrip = 0
        self._debounce = 0
        self._min_sample_size = sample_rate * 0.004
        self._debounce_time = sample_rate * 0.004
        self._this_drip_recorded = False
        self._peak = 0
        self._min_value = 0
        self._call_back = call_back
        self._call_back_samples = self.sample_rate / calls_back_per_second
        self._samples_since_call_back = 0
        self._samples_since_drip = 0
        self._drips_per_second = 0.0
        self._drip_history = []
        self._samples = 0

    def _get_value_chunk(self, seq):
        return (seq[pos:pos + self.sample_rate] for pos in xrange(0, len(seq), self.sample_rate))

    def process_frames(self, frames):
        values = [self.MONO_WAVE_STRUCT.unpack_from(frames, offset)[0] for offset in range(0, len(frames), self.MONO_WAVE_STRUCT.size)]
        for chunk in self._get_value_chunk(values):
            self._process_value_chunk(chunk)

    def _process_value_chunk(self, values):
        self._threshold.add_value(values)
        current_threshold = -1 * self._threshold.threshold()
        logging.info("Processing Input Audio Chunk")

        for value in values:
            self._samples += 1
            self._samples_since_drip += 1
            if value < current_threshold:
                if self._peak > value:
                    self._peak = value
                self._indrip += 1
            else:
                self._indrip = 0
                if self._this_drip_recorded:
                    self._debounce += 1
                    if self._debounce > self._debounce_time:
                        self._debounce = 0
                        self._this_drip_recorded = False

            if self._indrip >= self._min_sample_size:
                if value <= self._peak * 0.5 and self._this_drip_recorded is False:
                    self._drips += 1
                    self._drip_history.append(self._samples)
                    self.update_average()
                    self._peak = self._peak * 0.5
                    self._this_drip_recorded = True

            if self._call_back:
                self._samples_since_call_back += 1
                if self._samples_since_call_back >= self._call_back_samples:
                    self._samples_since_call_back = 0
                    self._drip_history = self._drip_history[-100:]
                    self._call_back(self._drips, self._drips_per_second, self._drip_history)

    def update_average(self):
        dripsec = self.sample_rate * 1.0 / self._samples_since_drip * 1.00
        if self._drips_per_second > 0.0:
            self._drips_per_second = (self._drips_per_second * 0.5) + (dripsec * 0.5)
        else:
            self._drips_per_second = dripsec
        self._samples_since_drip = 0

    def drips(self):
        return self._drips


class AudioDripZAxis(ZAxis, threading.Thread):
    def __init__(self,
                 drips_per_mm,
                 starting_height,
                 sample_rate,
                 bit_depth,
                 commander,
                 dripper_on_command,
                 dripper_off_command,
                 drip_call_back=None,):
        threading.Thread.__init__(self)
        super(AudioDripZAxis, self).__init__(starting_height)
        self._last_command = ('', 0)
        self._drips_per_mm = drips_per_mm
        self._sample_rate = sample_rate
        self._format = audio_formats[bit_depth]

        self._drip_call_back = drip_call_back

        self._commander = commander
        self._dripper_on_command = dripper_on_command
        self._dripper_off_command = dripper_off_command

        self._buffer_size = self._sample_rate / 2
        self._chunk_size = self._buffer_size / 4
        self._drips = 0
        self._destination_height = 0.0
        self._command_delay = 0.5

        self.running = True
        self.shutdown = False

        self.pa = pyaudio.PyAudio()
        self.drip_detector = DripDetector(self._sample_rate, self._call_back)

    def set_call_back(self, call_back):
        self._drip_call_back = call_back

    def _call_back(self, drips, average_drips, drip_history):
        self._drips = drips
        if self._drip_call_back:
            self._drip_call_back(drips, self.current_z_location_mm(), average_drips, drip_history)

    def reset(self):
        self.drip_detector = DripDetector(self._sample_rate, self._call_back)
        self._drips = 0

    def current_z_location_mm(self):
        return self._starting_height + (self._drips * 1.0 / self._drips_per_mm)

    def set_drips_per_mm(self, drips_per_mm):
        self._drips_per_mm = drips_per_mm

    def move_to(self, height_mm):
        self._destination_height = height_mm

    def _update_state(self):
        last, last_time = self._last_command
        now_time = time.time()
        if self._destination_height >= self.current_z_location_mm():
            if last != self._dripper_on_command or now_time - last_time > self._command_delay:
                self._last_command = (self._dripper_on_command, now_time)
                self._commander.send_command(self._dripper_on_command)
        else:
            if last != self._dripper_off_command or now_time - last_time > self._command_delay:
                self._last_command = (self._dripper_off_command, now_time)
                self._commander.send_command(self._dripper_off_command)

    def run(self):
        stream = self._get_stream()
        while self.running:
            self.drip_detector.process_frames(self._get_frames(stream))
            self._update_state()
        self._commander.send_command(self._dripper_off_command)
        stream.stop_stream()
        stream.close()
        self.shutdown = True

    def _get_frames(self, stream):
        if stream.get_read_available() > self._chunk_size:
            return stream.read(stream.get_read_available())
        else:
            return stream.read(self._chunk_size)

    def _get_stream(self):
        stream = self.pa.open(
            format=self._format,
            channels=1,
            rate=self._sample_rate,
            input=True,
            frames_per_buffer=self._buffer_size
            )
        stream.start_stream()
        return stream

    def close(self):
        self._commander.send_command(self._dripper_off_command)
        self.running = False
        attempts = 10
        while not self.shutdown and attempts > 0:
            attempts -= 1
            time.sleep(0.2)
        if attempts > 0:
            logging.info("AudioDripZAxis shutdown successfully")
        else:
            logging.info("AudioDripZAxis did not shutdown successfully")
        self.pa.terminate()
