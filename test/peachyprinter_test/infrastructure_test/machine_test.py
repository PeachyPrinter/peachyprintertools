import unittest
import os
import sys
import logging
from mock import patch, PropertyMock, call, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

import peachyprinter.infrastructure
from peachyprinter.infrastructure.machine import *
from peachyprinter.domain.commands import *


class MachineStatusTests(unittest.TestCase):
    real_datetime = datetime.datetime
    real_timedelta = datetime.timedelta

    call_count = 0

    def call_back(self,status):
        self.call_count += 1

    def setup(self):
        self.call_count = 0

    @patch.object(datetime, 'datetime')
    def test_status_elapsed_time_gives_elapsed_time_in_seconds(self, mock_datetime):
        expected = self.real_timedelta(seconds = 10)
        values = [self.real_datetime(2012,1,1,8,0,0), self.real_datetime(2012,1,1,8,0,10)]
        def next_values():
            return values.pop(0)
        mock_datetime.now.side_effect = next_values

        status = MachineStatus()
        actual = status.status()['elapsed_time']

        self.assertEqual(expected,actual)

    @patch.object(datetime, 'datetime')
    def test_status_start_time_gives_start_time(self, mock_datetime):
        start_time = self.real_datetime(2012,1,1,8,0,0)
        mock_datetime.now.return_value = start_time

        status = MachineStatus()
        actual = status.status()['start_time']

        self.assertEqual(start_time,actual)

    def test_add_layer_adds_a_layer(self):
        status = MachineStatus()
        status.add_layer()

        self.assertEqual(1,status.status()['current_layer'])

    def test_skipped_layer_adds_a_skipped_layer(self):
        status = MachineStatus()
        status.skipped_layer()

        self.assertEqual(1,status.status()['skipped_layers'])

    def test_status_is_starting_before_first_drip(self):
        status = MachineStatus()
        self.assertEqual('Starting',status.status()['status'])

    def test_status_is_running_after_first_drip(self):
        status = MachineStatus()
        status.drip_call_back(1,1,1)
        self.assertEqual('Running',status.status()['status'])

    def test_status_is_running_after_first_layer(self):
        status = MachineStatus()
        status.add_layer()
        self.assertEqual('Running',status.status()['status'])

    def test_set_complete_makes_status_complete(self):
        status = MachineStatus()
        status.set_complete()
        self.assertEqual('Complete',status.status()['status'])

    def test_once_complete_drips_or_layers_dont_change_status(self):
        status = MachineStatus()
        status.set_complete()
        status.add_layer()
        status.drip_call_back(45,10,12)
        self.assertEqual('Complete',status.status()['status'])

    def test_once_aborted_drips_or_layers_dont_change_status(self):
        status = MachineStatus()
        status.set_aborted()
        status.add_layer()
        status.drip_call_back(45,10,12)
        self.assertEqual('Cancelled',status.status()['status'])

    def test_add_error_adds_an_error(self):
        status = MachineStatus()
        status.add_error(MachineError("Error", "Test Error"))

        self.assertEqual(1,status.status()['errors'])

    def test_set_model_height_update_height_of_layer(self):
        status = MachineStatus()
        status.set_model_height(7.12213)

        self.assertEqual(7.12213,status.status()['model_height'])

    def test_waiting_for_drips_sets_waiting(self):
        status = MachineStatus()
        status.set_waiting_for_drips()

        self.assertEqual(True,status.status()['waiting_for_drips'])

    def test_not_waiting_for_drips_sets_waiting(self):
        status = MachineStatus()
        status.set_not_waiting_for_drips()

        self.assertEqual(False,status.status()['waiting_for_drips'])

    @patch.object(datetime, 'datetime')
    def test_add_error_adds_an_error(self,mock_datetime):
        mock_time = self.real_datetime(2012,1,1,8,0,0)
        mock_datetime.now.return_value = mock_time
        message = "Message"
        expected = [{
        'layer' : None,
        'time': mock_time, 
        'message': message,
        }]

        status = MachineStatus()
        status.add_error(MachineError(message))

        self.assertEqual(expected,status.status()['errors'])

    @patch.object(datetime, 'datetime')
    def test_add_error_adds_an_error_with_layer(self,mock_datetime):
        expected_layer = 34
        mock_time = self.real_datetime(2012,1,1,8,0,0)
        mock_datetime.now.return_value = mock_time
        message = "Message"
        expected = [{
        'layer' : expected_layer,
        'time': mock_time, 
        'message': message,
        }]

        status = MachineStatus()
        status.add_error(MachineError(message, expected_layer))

        self.assertEqual(expected,status.status()['errors'])

    def test_drip_call_back_updates_height(self):
        status = MachineStatus()
        status.drip_call_back(67,12,12.2, [])
        self.assertEqual(12, status.status()['height'])
        self.assertEqual(67, status.status()['drips'])
        self.assertEqual(12.2, status.status()['drips_per_second'])

    def test_drip_call_back_updates_history(self):
        status = MachineStatus()
        status.drip_call_back(67,12,12.2, [12,13])
        self.assertEqual([12,13], status.status()['drip_history'])



    def test_any_change_should_call_call_back(self):
        status = MachineStatus(status_call_back = self.call_back)
        self.assertEquals(0,self.call_count)
        status.set_not_waiting_for_drips()
        self.assertEquals(1,self.call_count)
        status.set_waiting_for_drips()
        self.assertEquals(2,self.call_count)
        status.drip_call_back(1,1,1)
        self.assertEquals(3,self.call_count)
        status.add_layer()
        self.assertEquals(4,self.call_count)
        status.add_error(MachineError("whooops"))
        self.assertEquals(5,self.call_count)
        status.set_complete()
        self.assertEquals(6,self.call_count)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()