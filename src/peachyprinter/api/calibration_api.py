import logging

from peachyprinter.infrastructure.path_to_points import PathToPoints
from peachyprinter.infrastructure.controller import Controller
from peachyprinter.infrastructure.communicator import UsbPacketCommunicator
from peachyprinter.domain.laser_control import LaserControl
from peachyprinter.infrastructure.micro_disseminator import MicroDisseminator
from peachyprinter.infrastructure.transformer import TuningTransformer, HomogenousTransformer
from peachyprinter.infrastructure.layer_generators import *
from peachyprinter.infrastructure.machine import *
from peachyprinter.infrastructure.layer_control import LayerWriter, LayerProcessing

logger = logging.getLogger('peachy')

'''The calibration API proivides the tools required to setup a Peacy Printer'''

class CalibrationAPI(object):
    def __init__(self, configuration_manager):
        logger.info("Calibartion API Startup")
        self._configuration_manager = configuration_manager
        self._configuration = self._configuration_manager.load()

        self._point_generator = SinglePointGenerator()
        self._blink_generator = BlinkGenerator()
        self._orientaiton_generator = OrientationGenerator()
        self._alignment_generator = CalibrationLineGenerator()
        self._scale_generator = SquareGenerator(speed=1, radius=1)

        self._test_patterns = {
            'Hilbert Space Filling Curve': HilbertGenerator(),
            'Square': SquareGenerator(),
            'Circle': CircleGenerator(),
            'Spiral': SpiralGenerator(),
            'Memory Hourglass': MemoryHourglassGenerator(),
            'Damping Test': DampingTestGenerator(),
            'NESW': NESWGenerator(),
            'Twitch': TwitchGenerator(),
            }

        self._current_generator = self._point_generator

        self._laser_control = LaserControl(self._configuration.cure_rate.override_laser_power_amount)
        transformer = TuningTransformer(scale=self._configuration.calibration.max_deflection)
        self._controller = None
        logger.debug("Setting up audiowriter")

        self._current_generator = self._point_generator

        self._state = MachineState()
        self._status = MachineStatus()

        self._communicator = UsbPacketCommunicator()
        self._communicator.start()
        self._disseminator = MicroDisseminator(
            self._laser_control,
            self._communicator,
            self._configuration.circut.data_rate
            )

        self._path_to_points = PathToPoints(
            self._disseminator.samples_per_second,
            transformer,
            self._configuration.options.laser_thickness_mm
            )

        post_fire_delay_speed = None
        slew_delay_speed = None
        if self._configuration.options.post_fire_delay:
            post_fire_delay_speed = self._configuration.options.laser_thickness_mm / (float(self._configuration.options.post_fire_delay) / 1000.0)
        if self._configuration.options.slew_delay:
            slew_delay_speed = self._configuration.options.laser_thickness_mm / (float(self._configuration.options.slew_delay) / 1000.0)

        self._writer = LayerWriter(
            self._disseminator,
            self._path_to_points,
            self._laser_control,
            self._state,
            post_fire_delay_speed=post_fire_delay_speed,
            slew_delay_speed=slew_delay_speed
            )

        self._layer_processing = LayerProcessing(
            self._writer,
            self._state,
            self._status,
            )

        self._controller = Controller(
            self._writer,
            self._layer_processing,
            self._current_generator,
            self._status,
            abort_on_error=False,
            )

        self.make_pattern_fit()
        self._controller.start()


    def set_print_area(self, width, height, depth):
        self._configuration.calibration.print_area_x = width
        self._configuration.calibration.print_area_y = height
        self._configuration.calibration.print_area_z = depth
        self._save()

    def get_print_area(self):
        return (self._configuration.calibration.print_area_x, self._configuration.calibration.print_area_y, self._configuration.calibration.print_area_z)

    def set_orientation(self, x_flip, yflip, swap_axis):
        self._configuration.calibration.flip_x_axis = x_flip
        self._configuration.calibration.flip_y_axis = yflip
        self._configuration.calibration.swap_axis = swap_axis
        self._save()

    def get_orientation(self):
        return (self._configuration.calibration.flip_x_axis, self._configuration.calibration.flip_y_axis, self._configuration.calibration.swap_axis)

    '''Used to show a single point with no calibration applied'''
    def show_point(self, xyz=[0.5, 0.5, 0.5]):
        # logger.info('Showing point')
        x, y, z = xyz
        self._point_generator.xy = [x, y]
        if (self._current_generator != self._point_generator):
            self._unapply_calibration()
            self._update_generator(self._point_generator)

    '''Used to show a blinking point with no calibration applied used for aligning on and off laser posisition'''
    def show_blink(self, xyz=[0.5, 0.5, 0.0]):
        logger.info('Showing blink')
        x, y, z = xyz
        self._blink_generator.xy = [x, y]
        if (self._current_generator != self._blink_generator):
            self._unapply_calibration()
            self._update_generator(self._blink_generator)

    '''Used to show pattern with no calibration applied used for determining orientation'''
    def show_orientation(self):
        logger.info('Showing Orientation')
        if (self._current_generator != self._orientaiton_generator):
            self._unapply_calibration()
            self._update_generator(self._orientaiton_generator)

    '''Used to show a single line on one axis used to line up calibration grid'''
    def show_line(self):
        logger.info('Showing line')
        self._unapply_calibration()
        self._update_generator(self._alignment_generator)

    '''Used to show a test pattern with calibration applied'''
    def show_test_pattern(self, pattern):
        logger.info('Showing test pattern %s' % pattern)
        if pattern in self._test_patterns.keys():
            self._apply_calibration()
            self._update_generator(self._test_patterns[pattern])
        else:
            logger.error('Pattern: %s does not exist' % pattern)
            raise Exception('Pattern: %s does not exist' % pattern)

    '''Shows the scale square'''
    def show_scale(self):
        logger.info('Showing scale')
        self._unapply_calibration()
        self._update_generator(self._scale_generator)

    def get_max_deflection(self):
        return self._configuration.calibration.max_deflection

    def set_max_deflection(self, deflection):
        self._configuration.calibration.max_deflection = deflection
        self._unapply_calibration()
        self._save()

    '''Allows user so force the laser on'''
    def set_laser_off_override(self, state):
        self._controller.laser_off_override = state

    '''Changes the speed at which the test pattern is drawn in mm/sec'''
    def set_test_pattern_speed(self, speed):
        [pattern.set_speed(speed) for pattern in self._test_patterns.values()]

    '''Changes the height at which the test pattern is drawn in mm'''
    def set_test_pattern_current_height(self, current_height):
        [pattern.set_current_height(current_height) for pattern in self._test_patterns.values()]

    '''returns a list of test patterns'''
    def get_test_patterns(self):
        return self._test_patterns.keys()

    '''Returns the current calibration for the printer'''
    def current_calibration(self):
        return self._configuration.calibration

    '''deprecated use set_lower_points and set_upper_points, set_height'''
    def save_points(self, height, lower_points, upper_points):
        self.set_lower_points(lower_points)
        self.set_upper_points(upper_points)
        self.set_height(height)

    '''Gets the lower calibration points'''
    def get_lower_points(self):
        return self._configuration.calibration.lower_points

    '''Set and saves the suppliled lower calibration'''
    def set_lower_points(self, lower_points):
        self._configuration.calibration.lower_points = lower_points
        self._save()

    '''Gets the upper calibration points'''
    def get_upper_points(self):
        return self._configuration.calibration.upper_points

    '''Set and saves the suppliled upper calibration'''
    def set_upper_points(self, upper_points):
        self._configuration.calibration.upper_points = upper_points
        self._save()

    '''Gets the calibration height'''
    def get_height(self):
        return self._configuration.calibration.height

    '''Set and saves the upper calibration height'''
    def set_height(self, height):
        self._configuration.calibration.height = height
        self._save()

    def _save(self):
        self._configuration_manager.save(self._configuration)
        self.make_pattern_fit()

    # deprecated
    def make_pattern_fit(self):
        for pattern in self._test_patterns.values():
            pattern.set_radius(self.get_largest_object_radius())

    '''Must be called before shutting down applications'''
    def close(self):
        self._controller.close()

    def _update_generator(self, generator):
        self._current_generator = generator
        self._controller.change_generator(self._current_generator)

    def _apply_calibration(self):
        self._path_to_points.set_transformer(
            HomogenousTransformer(
                self._configuration.calibration.max_deflection,
                self._configuration.calibration.height,
                self._configuration.calibration.lower_points,
                self._configuration.calibration.upper_points
                )
            )

    def _unapply_calibration(self):
        self._path_to_points.set_transformer(
            TuningTransformer(scale=self._configuration.calibration.max_deflection))

    def _validate_points(self, points):
        if (len(points) != 4):
            return False
        return True

    '''Based on current calibrations_gets_maximum_size_of_object at the base layer'''
    def get_largest_object_radius(self):
        lowest = None
        for (x, y) in self._configuration.calibration.lower_points.values():
            if not lowest or abs(x) < lowest:
                lowest = abs(x)
            if abs(y) < lowest:
                lowest = abs(y)
        logger.info("Calulated max radius of object as: %s mm" % lowest)
        return lowest

    def stop(self):
            self._controller.stop()
