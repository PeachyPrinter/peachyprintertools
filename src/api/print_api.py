import logging
import time
from os import path, listdir

from infrastructure.audio import AudioWriter
from infrastructure.file import FileWriter
from infrastructure.audiofiler import PathToAudio
from infrastructure.controller import Controller
from infrastructure.drip_based_zaxis import AudioDripZAxis
from infrastructure.timed_drip_zaxis import TimedDripZAxis, PhotoZAxis
from infrastructure.laser_control import AudioModulationLaserControl
from infrastructure.gcode_layer_generator import GCodeReader
from infrastructure.transformer import HomogenousTransformer
from infrastructure.layer_generators import SubLayerGenerator, ShuffleGenerator, OverLapGenerator
from infrastructure.commander import SerialCommander, NullCommander
from infrastructure.notification import EmailNotificationService, EmailGateway
from infrastructure.layer_control import LayerWriter, LayerProcessing
from infrastructure.machine import *


class PrintQueueAPI(object):
    def __init__(self, configuration, status_call_back=None):
        self._configuration = configuration
        self._files = []
        self._api = None
        self._status_call_back = status_call_back
        self._configuration.options.print_queue_delay

    def call_back(self, status):
        if self._status_call_back:
            self._status_call_back(status)
        if status['status'] == "Complete":
            if self._api:
                self._api.close()
            logging.info('Print Complete proceeding to next file')
            if len(self._files) > 0:
                logging.info('Waiting %s seconds before proceeding to next file' % self._configuration.options.print_queue_delay)
                time.sleep(self._configuration.options.print_queue_delay)
                logging.info('Proceeding to next file')
                self.print_next()
            else:
                logging.info('Print Queue Complete')

    def print_next(self):
        afile = self._files.pop(0)
        logging.info("Printing Next File: %s" % afile)
        self._api = PrintAPI(self._configuration, self.call_back)
        self._api.print_gcode(afile)

    def print_folder(self, folder):
        self._files = self._get_files(folder)
        self.print_next()

    def _get_files(self, folder):
        if not path.isdir(folder):
            logging.info('Folder Specified Does Not Exist')
            raise Exception('Folder Specified Does Not Exist')
        all_files = [path.join(folder, item) for item in listdir(folder) if item.endswith('.gcode')]
        if len(all_files) == 0:
            logging.info('Folder Contains No Valid Files')
            raise Exception('Folder Contains No Valid Files')
        return all_files

    def close(self):
        self._files = []
        if self._api:
            self._api.close()


'''API designed to use configuration to print a thing'''


class PrintAPI(object):
    def __init__(self, configuration, start_height=0.0, status_call_back=None):
        logging.info('Print API Startup')
        self._configuration = configuration
        logging.info('Printer Name: %s' % self._configuration.name)
        self._controller = None
        self._status_call_back = status_call_back
        self._zaxis = None
        self._start_height = start_height
        self._current_file_name = None
        self._current_file = None
        if self._configuration.email.on:
            self._email_gateway = EmailGateway(self._configuration.email.host, self._configuration.email.port)
            self._notification_service = EmailNotificationService(self._email_gateway, self._configuration.email.sender, self._configuration.email.recipient)
        else:
            self._notification_service = None

    @property
    def configuration(self):
        return self._configuration

    def print_gcode(self, file_name, print_sub_layers=True, dry_run=False):
        self._current_file_name = file_name
        self._current_file = open(file_name, 'r')
        gcode_reader = GCodeReader(self._current_file, scale=self._configuration.options.scaling_factor)
        gcode_layer_generator = gcode_reader.get_layers()
        layer_generator = gcode_layer_generator
        logging.info("Shuffled: %s" % self._configuration.options.use_shufflelayers)
        logging.info("Sublayered: %s" % self._configuration.options.use_sublayers)
        logging.info("Overlapped: %s" % self._configuration.options.use_overlap)

        if self._configuration.options.use_sublayers and print_sub_layers:
            layer_generator = SubLayerGenerator(layer_generator, self._configuration.options.sublayer_height_mm)
        if self._configuration.options.use_shufflelayers:
            layer_generator = ShuffleGenerator(layer_generator, self._configuration.options.shuffle_layers_amount)
        if self._configuration.options.use_overlap:
            layer_generator = OverLapGenerator(layer_generator, self._configuration.options.overlap_amount)
        self.print_layers(layer_generator, dry_run)

    def _get_zaxis(self):
        if self._configuration.dripper.dripper_type == 'audio':
            logging.info("Audio Zaxis")
            return AudioDripZAxis(
                self._configuration.dripper.drips_per_mm,
                self._start_height,
                self._configuration.audio.input.sample_rate,
                self._configuration.audio.input.bit_depth,
                self._commander,
                self._configuration.serial.on_command,
                self._configuration.serial.off_command
                )
        elif self._configuration.dripper.dripper_type == 'emulated':
            logging.info("Emulated Zaxis")
            return TimedDripZAxis(
                self._configuration.dripper.drips_per_mm,
                self._start_height,
                drips_per_second=self._configuration.dripper.emulated_drips_per_second
                )
        elif self._configuration.dripper.dripper_type == 'photo':
            logging.info("Photo Zaxis")
            return PhotoZAxis(
                self._start_height,
                self._configuration.dripper.photo_zaxis_delay
                )

    def print_layers(self, layer_generator, dry_run=False):
        if self._configuration.serial.on:
            self._commander = SerialCommander(self._configuration.serial.port)
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

        state = MachineState()
        self._status = MachineStatus(self._status_call_back)

        if dry_run:
            data_writer = None
            self._zaxis = None
            abort_on_error = False
        elif self._configuration.options.write_wav_files:
            data_writer = FileWriter(
                self._configuration.audio.output.sample_rate,
                self._configuration.audio.output.bit_depth,
                self._configuration.options.write_wav_files_folder,
                )
            self._zaxis = PhotoZAxis(
                self._start_height,
                0
                )
            abort_on_error = True
        else:
            data_writer = AudioWriter(
                self._configuration.audio.output.sample_rate,
                self._configuration.audio.output.bit_depth,
                )
            self._zaxis = self._get_zaxis()
            if self._zaxis:
                self._zaxis.set_call_back(self._status.drip_call_back)
                self._zaxis.start()
            abort_on_error = True

        override_speed = self._configuration.cure_rate.draw_speed if self._configuration.cure_rate.use_draw_speed else None
        pre_layer_delay = self._configuration.options.pre_layer_delay if self._configuration.options.pre_layer_delay else 0.0
        post_fire_delay_speed = None
        if self._configuration.options.post_fire_delay:
            post_fire_delay_speed = self._configuration.options.laser_thickness_mm / (float(self._configuration.options.post_fire_delay) / 1000.0)

        self._writer = LayerWriter(
            data_writer,
            path_to_audio,
            laser_control,
            state,
            move_distance_to_ignore=self._configuration.options.laser_thickness_mm,
            override_speed=override_speed,
            wait_speed=self._configuration.options.laser_thickness_mm / (float(self._configuration.options.wait_after_move_milliseconds) / 1000.0),
            post_fire_delay_speed=post_fire_delay_speed,
            )

        self._layer_processing = LayerProcessing(
            self._writer,
            state,
            self._status,
            self._zaxis,
            self._configuration.dripper.max_lead_distance_mm,
            self._commander,
            pre_layer_delay,
            self._configuration.serial.layer_started,
            self._configuration.serial.layer_ended,
            self._configuration.serial.print_ended,
            )

        self._controller = Controller(
            self._writer,
            self._layer_processing,
            layer_generator,
            self._status,
            abort_on_error=abort_on_error,
            )

        self._controller.start()

    def get_status(self):
        return self._controller.get_status()

    def can_set_drips_per_second(self):
        if getattr(self._zaxis, 'set_drips_per_second', False):
            return True
        else:
            return False

    def set_drips_per_second(self, drips_per_second):
        if getattr(self._zaxis, 'set_drips_per_second', False):
            self._zaxis.set_drips_per_second(drips_per_second)
        else:
            logging.error('Cannot change drips per second on %s' % type(self._zaxis))
            raise Exception('Cannot change drips per second on %s' % type(self._zaxis))

    def get_drips_per_second(self):
        if getattr(self._zaxis, 'get_drips_per_second'):
            return self._zaxis.get_drips_per_second()
        else:
            logging.warning("Drips per second requested but does not exist")
            return 0.0

    def verify_gcode(self, file_name):
        self.print_gcode(file_name,  print_sub_layers=False,  dry_run=True)

    def close(self):
        if self._zaxis:
            self._zaxis.close()
        if self._controller:
            self._controller.close()
        else:
            logging.warning('Stopped before printing')
        if self._current_file:
            self._current_file.close()
            logging.info("File Closed")
        if self._notification_service:
            self._notification_service.send_message("Print Complete", "%s is complete" % self._current_file_name)
