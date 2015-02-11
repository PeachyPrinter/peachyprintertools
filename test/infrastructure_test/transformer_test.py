import unittest
import os
import sys
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import test_helpers
from infrastructure.transformer import OneToOneTransformer, TuningTransformer, HomogenousTransformer


class OneToOneTransformerTests(unittest.TestCase, test_helpers.TestHelpers):
    def test_works_on_xyz(self):
        self.assertEquals([1.0, 1.0, 1.0], OneToOneTransformer().transform([1.0, 1.0, 1.0]))

    def test_goes_boom_on_xy(self):
        with self.assertRaises(Exception):
            OneToOneTransformer().transform([1.0, 1.0])


class TuningTransformerTests(unittest.TestCase, test_helpers.TestHelpers):
    def test_works_on_xyz(self):
        tuning_transformer = TuningTransformer()
        self.assertEquals([1.0, 1.0], tuning_transformer.transform([1.0, 1.0, 1.0]))
        self.assertEquals([0.5, 0.5], tuning_transformer.transform([0.5, 0.5, 1.0]))
        self.assertEquals([0.0, 0.0], tuning_transformer.transform([0.0, 0.0, 1.0]))

    def test_works_on_xyz_with_scale(self):
        tuning_transformer = TuningTransformer(scale=0.5)
        self.assertEquals([0.75, 0.75], tuning_transformer.transform([1.0, 1.0, 1.0]))
        self.assertEquals([0.5, 0.5], tuning_transformer.transform([0.5, 0.5, 1.0]))
        self.assertEquals([0.25, 0.25], tuning_transformer.transform([0.0, 0.0, 1.0]))

    def test_should_kaboom_if_scale_greater_then_1(self):
        with self.assertRaises(Exception):
            TuningTransformer(scale=1.5)

    def test_should_kaboom_if_scale_not_greater_then_0(self):
        with self.assertRaises(Exception):
            TuningTransformer(scale=0.0)

    def test_should_adjust_if_request_points_out_of_bounds(self):
        tuning_transformer = TuningTransformer(scale=1.0)
        self.assertEquals([1.0, 1.0], tuning_transformer.transform([1.1, 1.0, 1.0]))
        self.assertEquals([0.0, 1.0], tuning_transformer.transform([-0.1, 1.0, 1.0]))
        self.assertEquals([1.0, 1.0], tuning_transformer.transform([1.0, 1.1, 1.0]))
        self.assertEquals([1.0, 0.0], tuning_transformer.transform([1.0, -0.1, 1.0]))

    def test_can_change_tuning_transformer_scale(self):
        tuning_transformer = TuningTransformer(scale=1.0)
        self.assertEquals([1.0, 1.0], tuning_transformer.transform([1.0, 1.0, 1.0]))
        self.assertEquals([0.5, 0.5], tuning_transformer.transform([0.5, 0.5, 1.0]))
        self.assertEquals([0.0, 0.0], tuning_transformer.transform([0.0, 0.0, 1.0]))
        tuning_transformer.set_scale(0.5)
        self.assertEquals([0.75, 0.75], tuning_transformer.transform([1.0, 1.0, 1.0]))
        self.assertEquals([0.5, 0.5], tuning_transformer.transform([0.5, 0.5, 1.0]))
        self.assertEquals([0.25, 0.25], tuning_transformer.transform([0.0, 0.0, 1.0]))


class HomogenousTransformerTests(unittest.TestCase, test_helpers.TestHelpers):
    def test_points_outside_range_clip(self):
        height = 1.0
        lower_points = {
                (1.0, 1.0): (1.0, 1.0),
                (0.0, 1.0): (-1.0, 1.0),
                (1.0, 0.0): (1.0, -1.0),
                (0.0, 0.0): (-1.0, -1.0)
                }
        upper_points = {
                (1.0, 1.0): (1.0, 1.0),
                (0.0, 1.0): (-1.0, 1.0),
                (1.0, 0.0): (1.0, -1.0),
                (0.0, 0.0): (-1.0, -1.0)
                }
        scale = 1.0
        transformer = HomogenousTransformer(scale, height, lower_points, upper_points)

        test_points = [[-2.0, -2.0, 0.0], [2.0, 2.0, 0.0]]
        results = []
        for test_point in test_points:
                results.append(transformer.transform(test_point))
        self.assertEquals([(0.0, 0.0), (1.0, 1.0)], results)

    def test_given_a_basic_mapping_yields_expected_results(self):
        height = 1.0
        lower_points = {
                (1.0, 1.0): (1.0, 1.0),
                (0.0, 1.0): (-1.0, 1.0),
                (1.0, 0.0): (1.0, -1.0),
                (0.0, 0.0): (-1.0, -1.0)
                }
        upper_points = {
                (1.0, 1.0): (1.0, 1.0),
                (0.0, 1.0): (-1.0, 1.0),
                (1.0, 0.0): (1.0, -1.0),
                (0.0, 0.0): (-1.0, -1.0)
                }
        scale = 1.0
        transformer = HomogenousTransformer(scale, height, lower_points, upper_points)

        test_points = [
            [1.0, 1.0, 0.0], [-1.0, -1.0, 0.0], [0.0, 0.0, 0.0], [0.5, 0.5, 0.0],
            [1.0, 1.0, 2.5], [-1.0, -1.0, 2.5], [0.0, 0.0, 2.5], [0.5, 0.5, 2.5],
            [1.0, 1.0, 5.0], [-1.0, -1.0, 5.0], [0.0, 0.0, 5.0], [0.5, 0.5, 5.0]]

        expected_points = [((x + 1.0) / 2.0, (y + 1.0) / 2.0) for (x, y, z) in test_points]
        actual_points = [transformer.transform(point) for point in test_points]

        self.assertEquals(expected_points, actual_points)

    def test_zero_should_not_change_regardless_of_height(self):
        height = 1.0
        lower_points = {
                (1.0, 1.0): (36.0, 27.0),
                (0.0, 1.0): (-38.0, 30.0),
                (1.0, 0.0): (35.0, -33.0),
                (0.0, 0.0): (-38.0, -29.0)
                }
        upper_points = {
                (1.0, 1.0): (30.0, 23.0),
                (0.0, 1.0): (-31.0, 26.0),
                (1.0, 0.0): (30.0, -27.0),
                (0.0, 0.0): (-32.0, -25.0)
                }
        scale = 1.0
        transformer = HomogenousTransformer(scale, height, lower_points, upper_points)
        test_points = [[0.0, 0.0, 0.1], [0.0, 0.0, 1.0]]

        actual_points = [transformer.transform(point) for point in test_points]
        self.assertAlmostEquals(actual_points[0][0], actual_points[1][0])
        self.assertAlmostEquals(actual_points[0][1], actual_points[1][1])

        #sanity
        bottom = transformer.transform([18.0, 13.5, 0.0])
        self.assertAlmostEquals(0.76, bottom[0], places=2)
        self.assertAlmostEquals(0.76, bottom[1], places=2)

        top = transformer.transform([18.0, 13.5, 1.0])
        self.assertAlmostEquals(0.82, top[0], places=2)
        self.assertAlmostEquals(0.80, top[1], places=2)

    def test_given_a_basic_mapping_yields_expected_results_with_scale(self):
        height = 1.0
        lower_points = {
                (1.0, 1.0): (1.0, 1.0),
                (0.0, 1.0): (-1.0, 1.0),
                (1.0, 0.0): (1.0, -1.0),
                (0.0, 0.0): (-1.0, -1.0)
                }
        upper_points = {
                (1.0, 1.0): (1.0, 1.0),
                (0.0, 1.0): (-1.0, 1.0),
                (1.0, 0.0): (1.0, -1.0),
                (0.0, 0.0): (-1.0, -1.0)
                }
        scale = 0.5
        transformer = HomogenousTransformer(scale, height, lower_points, upper_points)
        test_points = [[1.0, 1.0, 0.0], [-1.0, -1.0, 0.0], [0.0, 0.0, 0.0], [0.5, 0.5, 0.0]]
        expected_points = [(0.75, 0.75), (0.25, 0.25), (0.5, 0.5), (0.625, 0.625)]

        actual_points = [transformer.transform(point) for point in test_points]

        self.assertEquals(expected_points, actual_points)

    def test_given_a_basic_mapping_yields_expected_results_with_scale_change(self):
        height = 1.0
        lower_points = {
                (1.0, 1.0): (1.0, 1.0),
                (0.0, 1.0): (-1.0, 1.0),
                (1.0, 0.0): (1.0, -1.0),
                (0.0, 0.0): (-1.0, -1.0)
                }
        upper_points = {
                (1.0, 1.0): (1.0, 1.0),
                (0.0, 1.0): (-1.0, 1.0),
                (1.0, 0.0): (1.0, -1.0),
                (0.0, 0.0): (-1.0, -1.0)
                }
        scale = 0.5
        transformer = HomogenousTransformer(scale, height, lower_points, upper_points)
        test_points = [[1.0, 1.0, 0.0], [-1.0, -1.0, 0.0], [0.0, 0.0, 0.0], [0.5, 0.5, 0.0]]
        expected_points_pre = [(0.75, 0.75), (0.25, 0.25), (0.5, 0.5), (0.625, 0.625)]
        expected_points_post = [(1.0, 1.0), (0.0, 0.0), (0.5, 0.5), (0.75, 0.75)]

        actual_points_pre = [transformer.transform(point) for point in test_points]
        transformer.set_scale(1.0)
        actual_points_post = [transformer.transform(point) for point in test_points]

        self.assertEquals(expected_points_pre, actual_points_pre)
        self.assertEquals(expected_points_post, actual_points_post)

    def test_given_a_basic_mapping_yields_expected_results_2(self):
        height = 5.0
        lower_points = {
                (1.0, 1.0): (4.0, 4.0),
                (0.0, 1.0): (-4.0, 4.0),
                (1.0, 0.0): (4.0, -4.0),
                (0.0, 0.0): (-4.0, -4.0)
                }
        upper_points = {
                (1.0, 1.0): (1.0, 1.0),
                (0.0, 1.0): (-1.0, 1.0),
                (1.0, 0.0): (1.0, -1.0),
                (0.0, 0.0): (-1.0, -1.0)
                }
        scale = 1.0
        transformer = HomogenousTransformer(scale, height, lower_points, upper_points)

        test_points = [
            [1.0, 1.0, 0.0], [-1.0, -1.0, 0.0], [0.0, 0.0, 0.0], [0.5, 0.5, 0.0],
            # [1.0, 1.0, 2.5], [-1.0, -1.0,2.5], [0.0, 0.0,2.5], [0.5, 0.5,2.5],
            # [1.0, 1.0, 5.0], [-1.0, -1.0, 5.0], [0.0, 0.0, 5.0], [0.5, 0.5, 5.0]
            ]

        expected_points = [
            (0.6250, 0.6250), (0.3750, 0.3750), (0.5000, 0.5000), (0.5625, 0.5625),
            # (0.6667, 0.6667), (0.3333, 0.3333), (0.5000, 0.5000), (0.5833, 0.5833),
            # (1.0000, 1.0000), (0.0000, 0.0000), (0.5000, 0.5000), (0.7500, 0.7500)
            ]

        actual_points = [transformer.transform(point) for point in test_points]

        self.assertEquals(expected_points, actual_points)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()
