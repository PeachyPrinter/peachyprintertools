import unittest
import sys
import os
from mock import patch, Mock
import time

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from infrastructure.timed_drip_zaxis import TimedDripZAxis

class TimedDripZaxisTests(unittest.TestCase):
    def setUp(self):
        self.tdza = None
        
        self.calls = 0
        self.drips = 0
        self.height = 0
        self.drips_per_second = 0
    
    def tearDown(self):
        if self.tdza:
            self.tdza.stop()

    def call_back(self, drips, height, drips_per_second):
        self.calls += 1
        self.drips = drips
        self.height = height
        self.drips_per_second = drips_per_second

    def test_shutsdown_cleanly(self):
        self.tdza = TimedDripZAxis(1)
        self.tdza.start()
        self.tdza.stop()
        self.assertFalse(self.tdza.is_alive())

    def test_current_z_location_mm_returns_the_correct_number(self):
        self.tdza = TimedDripZAxis(5, drips_per_second = 100)
        expected_mm = 2
        start = time.time()
        self.tdza.start()
        while time.time() - start < 0.1:
            time.sleep(0.01)
        result = self.tdza.current_z_location_mm()
        self.tdza.stop()
        self.assertAlmostEquals(expected_mm, result, places = 0)

    def test_cset_drips_per_mm_returns_the_new_correct_height(self):
        original_drips_per_mm = 1
        new_drips_per_mm = 0.1
        
        self.tdza = TimedDripZAxis(original_drips_per_mm, drips_per_second = 100)
        start = time.time()
        self.tdza.start()
        while time.time() - start < 0.1:
            time.sleep(0.01)
        self.tdza.stop()
        time.sleep(0.01)
        original_result = self.tdza.current_z_location_mm()
        self.tdza.set_drips_per_mm(new_drips_per_mm)
        new_result = self.tdza.current_z_location_mm()
        self.assertAlmostEquals(original_result * 10 , new_result, places = 1)
        
    # TODO: JT 2014-06-04 -> There is a windows specific bug with this I need to look at this on windows
    # def test_call_back_calls_back_at_correct_rate(self):
    #     expected_time = 0.1
    #     expected_drips = 10
    #     expected_height = 10
    #     expected_average = 100

    #     self.tdza = TimedDripZAxis(
    #         1, 
    #         drips_per_second = expected_average, 
    #         call_back = self.call_back, 
    #         calls_back_per_second = 100
    #         )

    #     start = time.time()
    #     self.tdza.start()
    #     while self.calls < 10:
    #         time.sleep(0.01)
    #     actual_time = time.time() - start
    #     self.tdza.stop()

    #     self.assertAlmostEquals(expected_time, actual_time, places = 1)
    #     self.assertEquals(expected_drips, self.drips)
    #     self.assertAlmostEquals(expected_height, self.height, places = 0)
    #     self.assertEquals(expected_average, self.drips_per_second)

    def test_can_set_call_back(self):
        self.tdza = TimedDripZAxis(
            1, 
            drips_per_second = 10, 
            calls_back_per_second = 100
            )

        self.tdza.set_call_back(self.call_back) 
        self.tdza.start()
        time.sleep(0.1)
        self.tdza.stop()

        self.assertTrue(self.calls > 0 )

    def test_can_change_drips_per_second_with_out_altering_existing_data(self):
        self.tdza = TimedDripZAxis(
            1, 
            drips_per_second = 100, 
            calls_back_per_second = 100
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
        self.tdza.stop()

        self.assertTrue(self.calls > 0 )

    def test_set_drips_per_second(self):
        expected_drips_per_second = 12
        self.tdza = TimedDripZAxis(
            1, 
            drips_per_second = expected_drips_per_second, 
            calls_back_per_second = 100
            )
        
        self.tdza.start()
        actual = self.tdza.get_drips_per_second()
        self.tdza.stop()

        self.assertEquals(expected_drips_per_second, actual )
    
    def test_move_to_does_nothing(self):
        expected_drips_per_second = 12
        self.tdza = TimedDripZAxis(
            1, 
            drips_per_second = expected_drips_per_second, 
            calls_back_per_second = 100
            )
        
        self.tdza.start()
        self.tdza.move_to(7.0)

if __name__ == '__main__':
    unittest.main()
