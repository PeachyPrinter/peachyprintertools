import unittest
import test_helpers
import sys
import os
import numpy

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

import test_helpers
from infrastructure.audiofiler import PathToAudio

class PathToAudioTests(unittest.TestCase, test_helpers.TestHelpers):
    
    def setup(self):
        pass

    def test_given_an_x_movement_an_x_path_should_be_created(self):
        samples_per_second = 6
        x_range_mm = 8
        y_range_mm = 8
        laser_size = 0.5
        path2audio = PathToAudio(samples_per_second, x_range_mm, y_range_mm, laser_size)
        expected = numpy.array([[0.5,0.5],[0.6,0.5],[0.7,0.5],[0.8,0.5],[0.9,0.5],[1.0,0.5]])

        actual = path2audio.process([0.0,0.0],[4.0,0.0],4.0)
        self.assertNumpyArrayEquals(expected, actual)

    def test_given_an_y_movement_a_y_path_should_be_created(self):
        samples_per_second = 6
        x_range_mm = 8
        y_range_mm = 8
        laser_size = 0.5
        path2audio = PathToAudio(samples_per_second, x_range_mm, y_range_mm, laser_size)
        expected = numpy.array([[0.5,0.5],[0.5,0.6],[0.5,0.7],[0.5,0.8],[0.5,0.9],[0.5,1.0]])

        actual = path2audio.process([0.0,0.0],[0.0,4.0],4.0)
        self.assertNumpyArrayEquals(expected, actual)

    def test_given_an_xy_movement_na_xy_path_should_be_created(self):
        samples_per_second = 6
        x_range_mm = 6
        y_range_mm = 8
        laser_size = 0.5
        path2audio = PathToAudio(samples_per_second, x_range_mm, y_range_mm, laser_size)
        expected = numpy.array([[0.5,0.5],[0.6,0.6],[0.7,0.7],[0.8,0.8],[0.9,0.9],[1.0,1.0]])

        actual = path2audio.process([0.0,0.0],[3.0,4.0],5.0)
        self.assertNumpyArrayEquals(expected, actual)

    def test_given_an_xy_movement_in_negitive_plane_a_xy_path_should_be_created(self):
        samples_per_second = 6
        x_range_mm = 6
        y_range_mm = 8
        laser_size = 0.5
        path2audio = PathToAudio(samples_per_second, x_range_mm, y_range_mm, laser_size)
        expected = numpy.array([[0.5,0.5],[0.4,0.4],[0.3,0.3],[0.2,0.2],[0.1,0.1],[0.0,0.0]])

        actual = path2audio.process([0.0,0.0],[-3.0,-4.0],5.0)
        self.assertNumpyArrayClose(expected, actual)

    def test_given_an_non_zero_origin(self):
        samples_per_second = 6
        x_range_mm = 6
        y_range_mm = 8
        laser_size = 0.5
        path2audio = PathToAudio(samples_per_second, x_range_mm, y_range_mm, laser_size)
        expected = numpy.array([[0.0,0.0],[0.1,0.1],[0.2,0.2],[0.3,0.3],[0.4,0.4],[0.5,0.5]])

        actual = path2audio.process([-3.0,-4.0],[0.0,0.0],5.0)
        self.assertNumpyArrayClose(expected, actual)

    def test_given_a_command_with_no_change_assume_movment_and_time_equal_to_laser_width(self):
        samples_per_second = 4
        x_range_mm = 6
        y_range_mm = 6
        laser_size = 0.5
        path2audio = PathToAudio(samples_per_second, x_range_mm, y_range_mm, laser_size)
        expected = numpy.array([[0.5,0.5],[0.5,0.5]])

        actual = path2audio.process([0.0,0.0],[0.0,0.0], 1.0)
        self.assertNumpyArrayClose(expected, actual)

if __name__ == '__main__':
    unittest.main()