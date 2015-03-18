import unittest
import sys
import os
import numpy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from test_helpers import TestHelpers
from peachyprinter.infrastructure.path_to_points import PathToPoints
from peachyprinter.infrastructure.transformer import OneToOneTransformer, TuningTransformer


class PathToPointsTests(unittest.TestCase, TestHelpers):
    transformer = OneToOneTransformer()

    def test_given_an_x_movement_an_x_path_should_be_created(self):
        samples_per_second = 11
        laser_size = 0.5
        path2audio = PathToPoints(samples_per_second, self.transformer, laser_size)
        expected = numpy.array([[0.0, 0.0], [0.25, 0.0], [0.5, 0.0], [0.75, 0.0], [1.0, 0.0]])

        actual = path2audio.process([0.0, 0.0, 1.0], [1.0, 0.0, 1.0], 2.0)
        self.assertNumpyArrayEquals(expected, actual)

    def test_given_an_y_movement_a_y_path_should_be_created(self):
        samples_per_second = 11
        laser_size = 0.5
        path2audio = PathToPoints(samples_per_second, self.transformer, laser_size)
        expected = numpy.array([[0.0, 0.0], [0.0, 0.25], [0.0, 0.5], [0.0, 0.75], [0.0, 1.0]])

        actual = path2audio.process([0.0, 0.0, 1.0], [0.0, 1.0, 1.0], 2.0)
        self.assertNumpyArrayEquals(expected, actual)

    def test_given_an_xy_movement_na_xy_path_should_be_created(self):
        samples_per_second = 11
        laser_size = 0.5
        path2audio = PathToPoints(samples_per_second, self.transformer, laser_size)
        expected = numpy.array([[0.0, 0.0], [0.25, 0.25], [0.5, 0.5], [0.75, 0.75], [1.0, 1.0]])

        actual = path2audio.process([0.0, 0.0, 1.0], [1.0, 1.0, 1.0], 3.0)
        self.assertNumpyArrayEquals(expected, actual)

    def test_given_an_non_zero_origin(self):
        samples_per_second = 11
        laser_size = 0.5
        path2audio = PathToPoints(samples_per_second, self.transformer, laser_size)
        expected = numpy.array([[1.0, 1.0], [0.75, 0.75], [0.5, 0.5], [0.25, 0.25], [0.0, 0.0]])

        actual = path2audio.process([1.0, 1.0, 1.0], [0.0, 0.0, 1.0], 3.0)
        self.assertNumpyArrayClose(expected, actual)

    def test_given_a_command_with_no_change_assume_movment_and_time_equal_to_laser_width(self):
        samples_per_second = 4
        laser_size = 0.5
        path2audio = PathToPoints(samples_per_second, self.transformer, laser_size)
        expected = numpy.array([[0.0, 0.0], [0.0, 0.0]])

        actual = path2audio.process([0.0, 0.0, 1.0], [0.0, 0.0, 1.0], 1.0)
        self.assertNumpyArrayClose(expected, actual)

    def test_can_change_transformer(self):
        samples_per_second = 4
        laser_size = 0.5
        path2audio = PathToPoints(samples_per_second, self.transformer, laser_size)
        path2audio.set_transformer(TuningTransformer())
        expected = numpy.array([[1.0, 1.0], [1.0, 1.0]])

        actual = path2audio.process([1.0, 1.0, 1.0], [1.0, 1.0, 1.0], 1.0)
        self.assertNumpyArrayClose(expected, actual)

    def test_in_the_event_of_a_distance_smaller_then_a_sample_the_vertex_time_should_not_be_skiped(self):
        samples_per_second = 10
        laser_size = 0.5
        path2audio = PathToPoints(samples_per_second, self.transformer, laser_size)
        expected1 = numpy.empty((0, 2))
        expected2 = numpy.array([[0.0, 0.0], [1.0, 1.0]])

        actual1 = path2audio.process([ 0.0, 0.0, 1.0], [0.0, 1.0, 1.0], 10.0)
        actual2 = path2audio.process([ 0.0, 1.0, 1.0], [1.0, 1.0, 1.0], 10.0)

        self.assertNumpyArrayEquals(expected1, actual1)
        self.assertNumpyArrayEquals(expected2, actual2)

    def test_when_handling_subone_sample_data_vertical_changes_cause_reset(self):
        samples_per_second = 10
        laser_size = 0.5
        path2audio = PathToPoints(samples_per_second, self.transformer, laser_size)
        expected1 = numpy.empty((0, 2))
        expected2 = numpy.array([[0.0, 1.0], [1.0, 1.0]])

        actual1 = path2audio.process([ 0.0, 0.0, 1.0], [0.0, 1.0, 1.0], 10.0)
        actual2 = path2audio.process([ 0.0, 1.0, 1.1], [1.0, 1.0, 1.1], 5.0)

        self.assertNumpyArrayEquals(expected1, actual1)
        self.assertNumpyArrayEquals(expected2, actual2)


if __name__ == '__main__':
    unittest.main()
