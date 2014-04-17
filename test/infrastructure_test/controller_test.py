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
from infrastructure.controller import Controller, MachineStatus
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
        actual = self.controller.status.waiting_for_drips
        self.controller.stop()

        self.wait_for_controller()

        self.assertTrue(actual)

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
        actual = self.controller.status.waiting_for_drips
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

        self.assertEquals(1, self.controller.status.current_layer)
        self.assertTrue(self.controller.status.complete)

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


    #TODO JT
    #Skip layers if z at next layer


class MachineStatusTests(unittest.TestCase):
    real_datetime = datetime.datetime
    real_timedelta = datetime.timedelta

    @patch.object(datetime, 'datetime')
    def test_elapsed_time_gives_elapsed_time_in_seconds(self, mock_datetime):
        expected = self.real_timedelta(seconds = 10)
        values = [self.real_datetime(2012,1,1,8,0,0), self.real_datetime(2012,1,1,8,0,10)]
        def next_values():
            return values.pop(0)
        mock_datetime.now.side_effect = next_values

        status = MachineStatus()
        actual = status.elapsed_time

        self.assertEqual(expected,actual)

    def test_add_layer_adds_a_layer(self):
        status = MachineStatus()
        status.add_layer()

        self.assertEqual(1,status.current_layer)

    @patch.object(infrastructure.drip_based_zaxis.DripBasedZAxis, 'current_z_location_mm')
    @patch.object(infrastructure.drip_based_zaxis.DripBasedZAxis, 'get_drips')
    def test_add_layer_adds_a_layer(self, mock_drips, mock_z_location_mm):
        mock_drips.return_value = 67
        mock_z_location_mm.return_value = 12
        
        status = MachineStatus(DripBasedZAxis())
        self.assertEqual(12, status.z_posisition)
        self.assertEqual(67, status.drips)



if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()