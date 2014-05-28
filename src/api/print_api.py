import logging
import threading

from infrastructure.audio import AudioWriter
from infrastructure.audiofiler import PathToAudio
from infrastructure.controller import Controller
from infrastructure.drip_based_zaxis import DripBasedZAxis
from infrastructure.laser_control import AudioModulationLaserControl
from infrastructure.gcode_layer_generator import GCodeReader
from infrastructure.transformer import HomogenousTransformer
from infrastructure.layer_generators import SubLayerGenerator
from infrastructure.zaxis_control import SerialZAxisControl


'''TODO'''
class PrintAPI(object):
    def __init__(self, configuration, status_call_back = None):
        logging.info("Print API Startup")
        self._configuration = configuration
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

    def print_layers(self, layer_generator, dry_run = False):
        laser_control = AudioModulationLaserControl(
            self._configuration.audio.output.sample_rate,
            self._configuration.audio.output.modulation_on_frequency,
            self._configuration.audio.output.modulation_off_frequency
            )
        transformer = HomogenousTransformer(self._configuration.calibration)
        path_to_audio = PathToAudio(
            laser_control.actual_samples_per_second,
            transformer, 
            self._configuration.options.laser_thickness_mm
            )
        if dry_run:
            audio_writer = None
            zaxis = None
            zaxis_control = None
            abort_on_error = False
        else:
            audio_writer = AudioWriter(
                self._configuration.audio.output.sample_rate, 
                self._configuration.audio.output.bit_depth,
                )
            zaxis = DripBasedZAxis(
                drips_per_mm = self._configuration.dripper.drips_per_mm, 
                initial_height = 0.0, 
                sample_rate = self._configuration.audio.input.sample_rate,
                bit_depth = self._configuration.audio.input.bit_depth,
                )
            if self._configuration.serial.on:
                zaxis_control = SerialZAxisControl(
                                    self._configuration.serial.port, 
                                    on_command = self._configuration.serial.on_command, 
                                    off_command = self._configuration.serial.off_command
                                    )
            else:
                zaxis_control = None
            abort_on_error = True

        self._controller = Controller(
            laser_control,
            path_to_audio,
            audio_writer,
            layer_generator,
            zaxis = zaxis,
            zaxis_control = zaxis_control,
            status_call_back = self._status_call_back,
            max_lead_distance = self._configuration.dripper.max_lead_distance_mm,
            abort_on_error = abort_on_error
            )
        self._controller.start()


    def get_status(self):
        return self._controller.get_status()

    def verify_gcode(self, g_code_file_like_object):
        self.print_gcode(g_code_file_like_object, dry_run = True)

    def stop(self):
        if self._controller:
            self._controller.stop()
        else:
            logging.warning('Stopped before printing')