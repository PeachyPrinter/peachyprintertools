import logging
import threading

from infrastructure.audio import AudioWriter
from infrastructure.audiofiler import PathToAudio
from infrastructure.controller import Controller
from infrastructure.drip_based_zaxis import AudioDripZAxis
from infrastructure.timed_drip_zaxis import TimedDripZAxis
from infrastructure.laser_control import AudioModulationLaserControl
from infrastructure.gcode_layer_generator import GCodeReader
from infrastructure.transformer import HomogenousTransformer
from infrastructure.layer_generators import SubLayerGenerator
from infrastructure.commander import SerialCommander, NullCommander


'''TODO'''
class PrintAPI(object):
    def __init__(self, configuration, status_call_back = None):
        logging.info('Print API Startup')
        self._configuration = configuration
        logging.info('Printer Name: %s' % self._configuration.name)
        self._controller = None
        self._status_call_back = status_call_back

    def print_gcode(self, file_like_object, print_sub_layers = True, dry_run = False):
        gcode_reader = GCodeReader(file_like_object)
        gcode_layer_generator = gcode_reader.get_layers()
        if print_sub_layers:
            layer_generator = SubLayerGenerator(gcode_layer_generator, self._configuration.options.sublayer_height_mm)
        else:
            layer_generator = gcode_layer_generator
        self.print_layers(layer_generator, dry_run)

    def _get_zaxis(self):
        if self._configuration.dripper.dripper_type == 'audio':
            return AudioDripZAxis(
                self._configuration.dripper.drips_per_mm, 
                self._configuration.audio.input.sample_rate,
                self._configuration.audio.input.bit_depth,
                self._commander,
                self._configuration.serial.on_command, 
                self._configuration.serial.off_command
                )
        elif self._configuration.dripper.dripper_type == 'emulated':
            return TimedDripZAxis(
                self._configuration.dripper.drips_per_mm, 
                drips_per_second = self._configuration.dripper.emulated_drips_per_second
                )

    def print_layers(self, layer_generator, dry_run = False):
        if self._configuration.serial.on:
            self._commander = SerialCommander( self._configuration.serial.port )
        else:
            self._commander = NullCommander()

        laser_control = AudioModulationLaserControl(
            self._configuration.audio.output.sample_rate,
            self._configuration.audio.output.modulation_on_frequency,
            self._configuration.audio.output.modulation_off_frequency,
            self._configuration.options.laser_offset
            )
        transformer = HomogenousTransformer(
            self._configuration.calibration.max_deflection,
            self._configuration.calibration.height,
            self._configuration.calibration.lower_points,
            self._configuration.calibration.upper_points,
            )
        path_to_audio = PathToAudio(
            laser_control.actual_samples_per_second,
            transformer, 
            self._configuration.options.laser_thickness_mm
            )
        if dry_run:
            audio_writer = None
            self.zaxis = None
            zaxis_control = None
            abort_on_error = False
        else:
            audio_writer = AudioWriter(
                self._configuration.audio.output.sample_rate, 
                self._configuration.audio.output.bit_depth,
                )
            self.zaxis = self._get_zaxis()
            abort_on_error = True

        self._controller = Controller(
            laser_control,
            path_to_audio,
            audio_writer,
            layer_generator,
            zaxis = self.zaxis,
            status_call_back = self._status_call_back,
            max_lead_distance = self._configuration.dripper.max_lead_distance_mm,
            abort_on_error = abort_on_error,
            max_speed = self._configuration.options.draw_speed
            )
        self._controller.start()

    def get_status(self):
        return self._controller.get_status()

    def can_set_drips_per_second(self):
        if getattr(self.zaxis, 'set_drips_per_second', False):
            return True
        else:
            return False

    def set_drips_per_second(self, drips_per_second):
        if getattr(self.zaxis, 'set_drips_per_second', False):
            self.zaxis.set_drips_per_second(drips_per_second)
        else:
            logging.error('Cannot change drips per second on %s' % type(self.zaxis))
            raise Exception('Cannot change drips per second on %s' % type(self.zaxis))

    def get_drips_per_second(self):
        if getattr(self.zaxis, 'get_drips_per_second'):
            return self.zaxis.get_drips_per_second()
        else:
            logging.warning("Drips per second requested but does not exist")
            return 0.0

    def verify_gcode(self, g_code_file_like_object):
        self.print_gcode(g_code_file_like_object, dry_run = True)

    def stop(self):
        if self.zaxis:
            self.zaxis.stop()   #Work around for windows not closing.
        if self._controller:
            self._controller.stop()
        else:
            logging.warning('Stopped before printing')