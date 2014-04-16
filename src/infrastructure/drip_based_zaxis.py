import threading
import pyaudio
import math
import struct
import time
import datetime
import logging

from audio import audio_formats
from domain.zaxis import ZAxis

class DripBasedZAxis(ZAxis, threading.Thread):
    MONO_WAVE_STRUCT_FMT = "h"
    MONO_WAVE_STRUCT = struct.Struct(MONO_WAVE_STRUCT_FMT)
    MAX_S16 = math.pow(2, 15)-1

    def __init__(self, 
                drips_per_mm = 1, 
                initial_height = 0.0, 
                sample_rate = 44100, 
                bit_depth = '16 bit', 
                threshold_percent = 0.50,
                release_ms = 6, 
                echo_drips = False ):

        threading.Thread.__init__(self)
        self.deamon = True
        self._drips_per_mm = drips_per_mm * 1.0
        self._sample_rate = sample_rate
        self._set_format_from_depth(bit_depth, threshold_percent)
        self._release = self._sample_rate / 1000 * release_ms
        self._echo_drips = echo_drips
        self._running = False
        self._num_drips = 0
        self._drips_per_mm = 1.0
        self._hold_samples = 0
        self._indrip = False
        self.instream = None
        self._buffer_size =  int(self._sample_rate/8)
        self._buffer_wait_time = self._buffer_size * 1.0 / self._sample_rate * 1.0 / 8.0

        self.set_drips_per_mm(drips_per_mm)
        logging.info("Drip Listening initialized using: samplerate: %s, bit depth %s, drips per mm: %s" %(self._sample_rate,bit_depth,self._drips_per_mm))

    def get_drips(self):
        return self._num_drips

    def _set_format_from_depth(self,depth, threshold):
        self._format = audio_formats[depth]
        if self._format ==  pyaudio.paInt8:
            self._threshold = threshold * math.pow(2, 8 - 1) - 1.0 
        elif self._format ==  pyaudio.paInt16:
            self._threshold = threshold * math.pow(2, 16 - 1) - 1.0 
        elif self._format ==  pyaudio.paInt24:
            self._threshold = threshold * math.pow(2, 24 - 1) - 1.0 
        elif self._format ==  pyaudio.paInt32:
            self._threshold = threshold * math.pow(2, 32 - 1) - 1.0 
        elif self._format ==  pyaudio.paFloat32:
            self._threshold = 1.0
        else:
            logger.error("Bit depth %s specified is not supported" % depth)
            raise Exception("Bit depth %s specified is not supported" % depth)

    def reset(self, z_height_mm = 0.0):
        self._num_drips = z_height_mm * self._drips_per_mm

    def set_drips_per_mm(self,number_drips_per_mm):
        self._drips_per_mm = number_drips_per_mm

    def current_z_location_mm(self):
        if (self._num_drips == 0):
            return 0.0
        return (self._num_drips * 1.0) / self._drips_per_mm

    def run(self):
        logging.info("Starting to listen to drips")
        pa = pyaudio.PyAudio()
        input_device = pa.get_default_input_device_info()
        input_device_id = input_device['index']
        if not pa.is_format_supported(
            self._sample_rate, 
            input_device = input_device_id, 
            input_channels = 1, 
            input_format=self._format
            ):
            raise Exception("Unsupported Format for your audio card")

        self.instream = pa.open(
                 format=self._format,
                 channels=1,
                 rate=self._sample_rate,
                 input=True,
                 frames_per_buffer=self._buffer_size
                 )
        self.instream.start_stream()
        self._running = True
        while(self._running):
            self._wait_for_buffer(self.instream.get_read_available())
            frames = self.instream.read(self.instream.get_read_available())
            self._add_frames(frames)

    def _wait_for_buffer(self,current_buffer_size):
        if current_buffer_size < self._buffer_size / 8.0:
            time.sleep(self._buffer_wait_time)

    def stop(self):
        while self.is_alive():
            if self._running:
                self._running = False
            time.sleep(0.1)
            if self.instream:
                try:
                    self.instream.stop_stream()
                except Exception as ex:
                    print(ex)
                time.sleep(0.1) # Waiting for current op to compelete
                try:
                    self.instream.close()
                except Exception as ex:
                    print(ex)


    def _add_frames(self, frames):
        hold_samples_c = 250

        for offset in range(0, len(frames), self.MONO_WAVE_STRUCT.size):
            value = self.MONO_WAVE_STRUCT.unpack_from(frames, offset)[0]
            if (value >=  self._threshold):
                self._indrip = True
                self._hold_samples = self._release
            else:
                if (self._hold_samples > 0):
                    self._hold_samples -= 1
                else:
                    if (self._indrip == True ):
                        self._num_drips += 1
                        if (self._echo_drips):
                            print("Drips: %d" % self._num_drips)
                        self._indrip = False
                        self._hold_samples = self._release