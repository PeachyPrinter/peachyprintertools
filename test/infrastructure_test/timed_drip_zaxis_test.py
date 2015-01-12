import unittest
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.timed_drip_zaxis import TimedDripZAxis, PhotoZAxis


class TimedDripZaxisTests(unittest.TestCase):
    def setUp(self):
        self.tdza = None

        self.calls = 0
        self.drips = 0
        self.height = 0
        self.drips_per_second = 0

    def tearDown(self):
        if self.tdza:
            self.tdza.close()

    def call_back(self, drips, height, drips_per_second):
        self.calls += 1
        self.drips = drips
        self.height = height
        self.drips_per_second = drips_per_second

    def test_shutsdown_cleanly(self):
        self.tdza = TimedDripZAxis(1, 0.0)
        self.tdza.start()
        self.tdza.close()
        self.assertFalse(self.tdza.is_alive())

    def test_current_z_location_mm_returns_the_correct_number(self):
        self.tdza = TimedDripZAxis(5, 0.0, drips_per_second=100)
        expected_mm = 2
        start = time.time()
        self.tdza.start()
        while time.time() - start < 0.1:
            time.sleep(0.01)
        result = self.tdza.current_z_location_mm()
        self.tdza.close()
        self.assertAlmostEquals(expected_mm, result, places=0)

    def test_current_z_location_mm_returns_the_correct_number_given_starting_height(self):
        starting_height = 7.7
        expected_height = starting_height + 2
        self.tdza = TimedDripZAxis(5, starting_height, drips_per_second=100)

        self.assertEquals(starting_height, self.tdza.current_z_location_mm())

        start = time.time()
        self.tdza.start()
        while time.time() - start < 0.1:
            time.sleep(0.01)
        result = self.tdza.current_z_location_mm()
        self.tdza.close()

        self.assertAlmostEquals(expected_height, result, places=0)

    def test_cset_drips_per_mm_returns_the_new_correct_height(self):
        original_drips_per_mm = 1
        new_drips_per_mm = 0.1

        self.tdza = TimedDripZAxis(original_drips_per_mm, 0.0, drips_per_second=100)
        start = time.time()
        self.tdza.start()
        while time.time() - start < 0.1:
            time.sleep(0.01)
        self.tdza.close()
        time.sleep(0.01)
        original_result = self.tdza.current_z_location_mm()
        self.tdza.set_drips_per_mm(new_drips_per_mm)
        new_result = self.tdza.current_z_location_mm()
        self.assertAlmostEquals(original_result * 10, new_result, places=0)

    # TODO: JT 2014-06-04 -> There is a windows specific bug with this I need to look at this on windows
    # def test_call_back_calls_back_at_correct_rate(self):
    #     expected_time = 0.1
    #     expected_drips = 10
    #     expected_height = 10
    #     expected_average = 100

    #     self.tdza = TimedDripZAxis(
    #         1, 0.0, 
    #         drips_per_second = expected_average, 
    #         call_back = self.call_back, 
    #         calls_back_per_second = 100
    #         )

    #     start = time.time()
    #     self.tdza.start()
    #     while self.calls < 10:
    #         time.sleep(0.01)
    #     actual_time = time.time() - start
    #     self.tdza.close()

    #     self.assertAlmostEquals(expected_time, actual_time, places = 1)
    #     self.assertEquals(expected_drips, self.drips)
    #     self.assertAlmostEquals(expected_height, self.height, places = 0)
    #     self.assertEquals(expected_average, self.drips_per_second)

    def test_can_set_call_back(self):
        self.tdza = TimedDripZAxis(
            1,
            0.0,
            drips_per_second=10,
            calls_back_per_second=100
            )

        self.tdza.set_call_back(self.call_back)
        self.tdza.start()
        time.sleep(0.1)
        self.tdza.close()

        self.assertTrue(self.calls > 0)

    def test_can_change_drips_per_second_with_out_altering_existing_data(self):
        self.tdza = TimedDripZAxis(
            1,
            0.0,
            drips_per_second=100,
            calls_back_per_second=100
            )

        self.tdza.set_call_back(self.call_back)
        self.tdza.start()
        time.sleep(0.1)
        before_drips = self.drips
        before_cb_height = self.height
        before_height = self.tdza.current_z_location_mm()
        self.tdza.set_drips_per_second(10)
        time.sleep(0.1)
        self.assertTrue(before_height <= self.tdza.current_z_location_mm(), "%s !<= %s" % (before_height, self.tdza.current_z_location_mm()))
        self.assertTrue(before_cb_height <= self.height)
        self.assertTrue(before_drips <= self.drips)
        self.tdza.close()

        self.assertTrue(self.calls > 0)

    def test_set_drips_per_second(self):
        expected_drips_per_second = 12
        self.tdza = TimedDripZAxis(
            1,
            0.0,
            drips_per_second=expected_drips_per_second,
            calls_back_per_second=100
            )

        self.tdza.start()
        actual = self.tdza.get_drips_per_second()
        self.tdza.close()

        self.assertEquals(expected_drips_per_second, actual)

    def test_move_to_does_nothing(self):
        expected_drips_per_second = 12
        self.tdza = TimedDripZAxis(
            1,
            0.0,
            drips_per_second=expected_drips_per_second,
            calls_back_per_second=100
            )

        self.tdza.start()
        self.tdza.move_to(7.0)


class PhotoZAxisTests(unittest.TestCase):

    def setUp(self):
        self.calls = 0
        self.drips = 0
        self.height = 0
        self.drips_per_second = 0

    def call_back(self, drips, height, drips_per_second):
        self.calls += 1
        self.drips = drips
        self.height = height
        self.drips_per_second = drips_per_second

    def test_current_z_location_reports_0(self):
        test_zaxis = PhotoZAxis(0.0, )
        self.assertEquals(0.0, test_zaxis.current_z_location_mm())

    def test_current_z_location_reports_starting_height(self):
        starting_height = 7.7
        test_zaxis = PhotoZAxis(starting_height)
        self.assertEquals(starting_height, test_zaxis.current_z_location_mm())

    def test_calling_move_to_changes_z_height_when_delay_0(self):
        expected_height = 10.0
        test_zaxis = PhotoZAxis(0.0, 0.0)
        test_zaxis.move_to(expected_height)
        self.assertEquals(expected_height, test_zaxis.current_z_location_mm())

    def test_calling_move_to_changes_z_height_only_after_delay(self):
        expected_height = 10.0
        expected_delay = 0.250
        test_zaxis = PhotoZAxis(0.0, expected_delay)
        test_zaxis.move_to(expected_height)
        self.assertEquals(0, test_zaxis.current_z_location_mm())
        time.sleep(expected_delay)
        self.assertEquals(expected_height, test_zaxis.current_z_location_mm())

    def test_should_call_callback_when_something_changes(self):
        expected_height = 10.0
        expected_delay = 0.0
        test_zaxis = PhotoZAxis(0.0, expected_delay, call_back=self.call_back)
        test_zaxis.move_to(expected_height)
        test_zaxis.current_z_location_mm()
        self.assertEquals(expected_height, self.height)
        self.assertEquals(0, self.drips)
        self.assertEquals(0, self.drips_per_second)

    def test_set_call_back_should_add_callback(self):
        expected_height1 = 10.0
        expected_height2 = 20.0
        expected_delay = 0.0
        test_zaxis = PhotoZAxis(0.0, expected_delay, call_back=None)
        test_zaxis.move_to(expected_height1)
        test_zaxis.current_z_location_mm()
        self.assertEquals(0, self.height)
        self.assertEquals(0, self.drips)
        self.assertEquals(0, self.drips_per_second)

        test_zaxis.set_call_back(self.call_back)

        test_zaxis.move_to(expected_height2)
        test_zaxis.current_z_location_mm()
        self.assertEquals(expected_height2, self.height)
        self.assertEquals(0, self.drips)
        self.assertEquals(0, self.drips_per_second)

    def test_start_should_advance(self):
        test_zaxis = PhotoZAxis(0.0, )
        test_zaxis.start()
        self.assertEquals(0.0, test_zaxis.current_z_location_mm())

    def test_close_can_be_called(self):
        test_zaxis = PhotoZAxis(0.0, )
        test_zaxis.start()
        self.assertEquals(0.0, test_zaxis.current_z_location_mm())
        test_zaxis.close()

if __name__ == '__main__':
    unittest.main()
