import unittest
import mock


from infrastructure.laser_control import AudioModulationLaserControl

class AudioModulationLaserControlTests(unittest.TestCase):
    sample_rate = 1000
    on_frequency = 250
    off_frequency = 125
    audio_modulator = None

    def setup(self):
        pass

    def tearDown(self):
        if self.audio_modulator and self.audio_modulator.is_running():
            self.audio_modulator.stop()
        
    def test_laser_control_starts_and_stops_output_stream(self):
        # Pending
        pass

