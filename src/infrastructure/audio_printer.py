
class AudioPrinter(object):
    def init(self,sampling_frequency):
        self.sampling_frequency = sampling_frequency

    def start(self, output_stream):
        raise NotImplementedException()

    def stop(self):
        raise NotImplementedException()


class MockAudioPrinter(AudioPrinter):
    recorded_data = []
    running = False

    def start(self, output_stream):
        running = True
        for chunk in output_stream:
            if running:
                self.recorded_data.append(chunk)
            else:
                break
    
    def stop(self):
        running = False

    def reset():
        self.recorded_data[:] = []