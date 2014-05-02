import unittest
import os
import sys
import time
import datetime
import itertools
import logging
from mock import patch, PropertyMock

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

import infrastructure
from infrastructure.controller import Controller, MachineStatus, MachineError
from domain.commands import *
from infrastructure.layer_generators import StubLayerGenerator, SinglePointGenerator
from infrastructure.drip_based_zaxis import DripBasedZAxis

@patch('domain.laser_control.LaserControl')
@patch('domain.zaxis.ZAxis')
@patch('infrastructure.audiofiler.PathToAudio')
@patch('infrastructure.audio.AudioWriter')
@patch('domain.layer_generator.LayerGenerator')
class ControllerTests(unittest.TestCase):
    controller = None

    def wait_for_controller(self):
        while self.controller.starting or self.controller.running:
            time.sleep(0.1)

    def tearDown(self):
        if self.controller and self.controller.is_alive():
            self.controller.stop()


    def test_should_turn_on_laser_for_draw_commands(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],100.0) ])
        stub_layer_generator = StubLayerGenerator([test_layer])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"

        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator)
        self.controller.start()

        self.wait_for_controller()

        self.assertEqual(1,mock_laser_control.set_laser_on.call_count)

    def test_should_turn_off_laser_for_move_commands(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralMove([0.0,0.0],[2.0,2.0],100.0) ])
        stub_layer_generator = StubLayerGenerator([test_layer])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"
                
        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator)
        self.controller.start()

        self.wait_for_controller()

        self.assertEqual(1,mock_laser_control.set_laser_off.call_count)
        self.assertEqual(0,mock_laser_control.set_laser_on.call_count)

    def test_should_output_modulate_audio_for_movement_commands(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
        stub_layer_generator = StubLayerGenerator([test_layer])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"

        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator)
        self.controller.start()

        self.wait_for_controller()

        mock_laser_control.modulate.assert_called_with("SomeAudio")
        mock_audio_writer.write_chunk.assert_called_with("SomeModulatedAudio")

    def test_should_call_path_to_audio_with_xyz(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
        stub_layer_generator = StubLayerGenerator([test_layer])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"

        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator)
        self.controller.start()

        self.wait_for_controller()

        mock_path_to_audio.process.assert_called_with([0.0,0.0,0.0],[2.0,2.0,0.0],2.0)

    def test_should_remember_current_posisition(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0), LateralDraw([2.0,2.0],[-1.0,-1.0],2.0) ])
        stub_layer_generator = StubLayerGenerator([test_layer])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"

        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator)
        self.controller.start()

        self.wait_for_controller()

        mock_path_to_audio.process.assert_called_with([2.0,2.0,0.0],[-1.0,-1.0,0.0],2.0)

    def test_if_max_lead_specifed_should_skip_layers_if_higher(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        max_lead_distance = 0.1
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        mock_zaxis = mock_ZAxis.return_value
        zaxis_return_values = [ 0.0, 0.0, 2.0, 2.0,2.0,2.0 ]
        def z_axis_side_effect():
            return zaxis_return_values.pop(0)
        mock_zaxis.current_z_location_mm = z_axis_side_effect
        test_layer1 = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0), LateralDraw([2.0,2.0],[-1.0,-1.0],2.0) ])
        test_layer2 = Layer(1.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0), LateralDraw([2.0,2.0],[-1.0,-1.0],2.0) ])
        test_layer3 = Layer(2.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0), LateralDraw([2.0,2.0],[-1.0,-1.0],2.0) ])
        stub_layer_generator = StubLayerGenerator([test_layer1, test_layer2, test_layer3])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"

        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator,zaxis =mock_zaxis,max_lead_distance=max_lead_distance)
        self.controller.start()
        self.wait_for_controller()
        self.assertEquals(5, mock_audio_writer.write_chunk.call_count)

    def test_if_draw_command_start_and_current_pos_are_not_the_same_should_move_to_new_posisition(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ 
            LateralDraw([0.0,0.0],[0.0,0.0],2.0), 
            LateralDraw([2.0,2.0],[-1.0,-1.0],2.0)
             ])
        stub_layer_generator = StubLayerGenerator([test_layer])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"

        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator)
        self.controller.start()

        self.wait_for_controller()

        mock_laser_control.modulate.call_count = 3
        mock_path_to_audio.process.call_count = 3
        mock_laser_control.set_laser_off.assert_called_with()
        self.assertEqual(([0.0,0.0,0.0],[2.0,2.0,0.0],2.0), mock_path_to_audio.process.call_args_list[1][0])

    def test_if_move_command_start_and_current_pos_are_not_the_same_should_move_to_new_posisition(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralMove([0.0,0.0],[0.0,0.0],2.0), LateralMove([2.0,2.0],[-1.0,-1.0],2.0) ])
        stub_layer_generator = StubLayerGenerator([test_layer])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"

        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator)
        self.controller.start()

        self.wait_for_controller()

        mock_laser_control.modulate.call_count = 2
        mock_path_to_audio.process.call_count = 2
        mock_laser_control.set_laser_off.assert_called_with()
        self.assertEqual(([0.0,0.0,0.0],[-1.0,-1.0,0.0],2.0), mock_path_to_audio.process.call_args_list[1][0])

    def test_should_ignore_z_in_layer_if_z_axis_none(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer1 = Layer(0.0, [ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
        test_layer2 = Layer(1.0, [ LateralDraw([2.0,2.0],[0.0,0.0],2.0) ])
        stub_layer_generator = StubLayerGenerator([test_layer1,test_layer2])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"

        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator,None)
        self.controller.start()

        self.wait_for_controller()

        self.assertEqual(2,mock_path_to_audio.process.call_count)
        mock_path_to_audio.process.assert_called_with([2.0,2.0,0.0],[0.0,0.0,1.0],2.0)

    def test_zaxis_should_be_waited_for_buy_outputing_laser_off_signal(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_zaxis = mock_ZAxis.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        zaxis_return_values = [ 0.0, 0.25, 0.75, 1.0 ]
        def z_axis_side_effect():
            return zaxis_return_values.pop(0)
        mock_zaxis.current_z_location_mm = z_axis_side_effect

        test_layer1 = Layer(0.0, [ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
        test_layer2 = Layer(1.0, [ LateralDraw([2.0,2.0],[0.0,0.0],2.0) ])
        stub_layer_generator = StubLayerGenerator([test_layer1,test_layer2])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"

        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator, mock_zaxis)
        self.controller.start()

        self.wait_for_controller()

        mock_zaxis.start.assert_called_with()
        self.assertEqual(4, mock_path_to_audio.process.call_count)
        self.assertEqual(2, mock_laser_control.set_laser_off.call_count)
        self.assertEqual(([2.0,2.0,0.0],[2.0,2.0,0.0],2.0), mock_path_to_audio.process.call_args_list[1][0])
        self.assertEqual(([2.0,2.0,0.0],[2.0,2.0,0.0],2.0), mock_path_to_audio.process.call_args_list[2][0])

    def test_stop_should_close_all_processes_cleanly(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        mock_zaxis = mock_ZAxis.return_value
        mock_layer_generator = mock_LayerGenerator.return_value
        mock_layer_generator.next.return_value =  Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"
        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,mock_layer_generator,mock_zaxis)
        self.controller.start()

        time.sleep(0.1)

        self.controller.stop()

        time.sleep(0.1)

        mock_zaxis.stop.assert_called_with()
        mock_audio_writer.close.assert_called_with()

    def test_stop_should_close_all_processes_cleanly_while_waiting_for_z(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        mock_zaxis = mock_ZAxis.return_value
        mock_zaxis.current_z_location_mm.return_value = 0.0
        mock_layer_generator = mock_LayerGenerator.return_value
        mock_layer_generator.next.return_value =   Layer(1.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"
        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,mock_layer_generator,mock_zaxis)
        self.controller.start()

        time.sleep(0.1)

        self.controller.stop()

        self.wait_for_controller()

        mock_zaxis.stop.assert_called_with()
        mock_audio_writer.close.assert_called_with()

    def test_stop_should_close_all_processes_cleanly_while_working_on_commands(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        mock_layer_generator = mock_LayerGenerator.return_value
        test_layer = Layer(1.0, [ LateralDraw([2.0,2.0],[0.0,0.0],2.0) for x in range(0,32768)])
        stub_layer_generator = StubLayerGenerator([test_layer])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"
        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator)
        self.controller.start()
        time.sleep(0.1)

        self.controller.stop()
        time.sleep(0.1)

        mock_audio_writer.close.assert_called_with()
        
        self.wait_for_controller()


    def test_set_waiting_while_wating_for_z(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        mock_zaxis = mock_ZAxis.return_value
        mock_zaxis.current_z_location_mm.return_value = 0.0
        mock_layer_generator = mock_LayerGenerator.return_value
        mock_layer_generator.next.return_value = Layer(1.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"
        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,mock_layer_generator,mock_zaxis)
        self.controller.start()

        time.sleep(0.1)
        actual = self.controller.get_status()['waiting_for_drips']
        self.controller.stop()

        self.wait_for_controller()

        self.assertTrue(actual)

    def test_should_update_layer_height(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        expected_model_height = 32.7
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        mock_zaxis = mock_ZAxis.return_value
        mock_zaxis.current_z_location_mm.return_value = 23.2
        mock_layer_generator = mock_LayerGenerator.return_value
        mock_layer_generator.next.return_value = Layer(expected_model_height,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"
        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,mock_layer_generator,mock_zaxis)
        self.controller.start()

        self.controller.stop()

        self.wait_for_controller()
        actual = self.controller.get_status()['model_height']

        self.assertEquals(expected_model_height,actual)

    def test_set_waiting_while_not_wating_for_z(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        mock_zaxis = mock_ZAxis.return_value
        mock_zaxis.current_z_location_mm.return_value = 1.0
        mock_layer_generator = mock_LayerGenerator.return_value
        mock_layer_generator.next.return_value =  Layer(1.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"
        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,mock_layer_generator,mock_zaxis)
        self.controller.start()

        time.sleep(0.1)
        actual = self.controller.get_status()['waiting_for_drips']
        self.controller.stop()

        self.wait_for_controller()

        self.assertFalse(actual)
        
    def test_should_update_machine_status(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],100.0) ])
        stub_layer_generator = StubLayerGenerator([test_layer])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"

        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator)
        self.controller.start()

        self.wait_for_controller()

        self.assertEquals(1, self.controller.get_status()['current_layer'])
        self.assertEquals('Complete',self.controller.get_status()['status'])

    def test_should_change_layer_generator(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value

        generator1 = SinglePointGenerator([1.0,1.0])
        generator2 = SinglePointGenerator([0.0,0.0])

        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,generator1)
        self.controller.start()
        time.sleep(0.1)
        pre_switch = mock_path_to_audio.process.call_args
        self.controller.change_generator(generator2)
        time.sleep(0.1)
        post_switch = mock_path_to_audio.process.call_args
        self.controller.stop()
        self.wait_for_controller()

        self.assertEquals( ([1.0,1.0,0.0],[1.0,1.0,0.0],100.0), pre_switch[0] )
        self.assertEquals( ([0.0,0.0,0.0],[0.0,0.0,0.0],100.0), post_switch[0] )

    def test_stop_should_stop_working_on_commands_when_generator_changed(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        mock_layer_generator = mock_LayerGenerator.return_value
        test_layer1 = Layer(1.0, [ LateralDraw([2.0,2.0],[0.0,0.0],2.0) for x in range(0,32768)])
        stub_layer_generator1 = StubLayerGenerator([test_layer1])
        test_layer2 = Layer(1.0, [ LateralDraw([0.0,0.0],[0.0,0.0],2.0)] )
        stub_layer_generator2 = StubLayerGenerator([test_layer2])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"
        self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator1)
        self.controller.start()
        time.sleep(0.1)

        self.controller.change_generator(stub_layer_generator2)
        time.sleep(0.1)

        mock_path_to_audio.process.assert_called_with([0.0,0.0,1.0],[0.0,0.0,1.0],2.0)
        
        self.wait_for_controller()


    def test_init_should_set_call_back_on_zaxis(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        mock_layer_generator = mock_LayerGenerator.return_value
        mock_zaxis = mock_ZAxis.return_value
        Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,mock_layer_generator, mock_zaxis)

        self.assertTrue(mock_zaxis.set_drip_call_back.called)

    #TODO JT
    #Skip layers if z at next layer


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

    def test_status_is_starting_before_first_drip(self):
        status = MachineStatus()
        self.assertEqual('Starting',status.status()['status'])

    def test_status_is_running_after_first_drip(self):
        status = MachineStatus()
        status.drip_call_back(1,1)
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
        status.drip_call_back(45,10)
        self.assertEqual('Complete',status.status()['status'])

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
        'time': mock_time, 
        'message': message,
        }]

        status = MachineStatus()
        status.add_error(MachineError(message))

        self.assertEqual(expected,status.status()['errors'])


    def test_drip_call_back_updates_height(self):
        status = MachineStatus()
        status.drip_call_back(67,12)
        self.assertEqual(12, status.status()['height'])
        self.assertEqual(67, status.status()['drips'])


    def test_any_change_should_call_call_back(self):
        status = MachineStatus(status_call_back = self.call_back)
        self.assertEquals(0,self.call_count)
        status.set_not_waiting_for_drips()
        self.assertEquals(1,self.call_count)
        status.set_waiting_for_drips()
        self.assertEquals(2,self.call_count)
        status.drip_call_back(1,1)
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