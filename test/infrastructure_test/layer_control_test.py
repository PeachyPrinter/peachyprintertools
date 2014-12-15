import unittest
import os
import sys
import time
import datetime
import logging
from mock import patch, PropertyMock, call, MagicMock

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

import infrastructure
from infrastructure.layer_control import *
from domain.commands import *
from infrastructure.machine import *

@patch('domain.laser_control.LaserControl')
@patch('infrastructure.audiofiler.PathToAudio')
@patch('infrastructure.audio.AudioWriter')
class LayerWriterTests(unittest.TestCase):
    # def test_process_layer_should_turn_off_laser_for_draw_commands_when_forced_off(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],100.0) ])
    #     self.writer = LayerWriter(mock_audio_writer, mock_path_to_audio, mock_laser_control, MachineState(), override_speed =100)
    #     self.writer.laser_off_override = True

    #     self.writer.process_layer(test_layer)

    #     self.assertEqual(1,mock_laser_control.set_laser_off.call_count)
    #     self.assertEqual(0,mock_laser_control.set_laser_on.call_count)

    # def test_process_layer_should_turn_on_laser_for_draw_commands(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],100.0) ])
    #     self.writer = LayerWriter(mock_audio_writer, mock_path_to_audio, mock_laser_control, MachineState(), override_speed =100)

    #     self.writer.process_layer(test_layer)

    #     self.assertEqual(1,mock_laser_control.set_laser_on.call_count)

    # def test_process_layer_should_wait_after_move_before_draw_commands(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     test_layer = Layer(0.0,[ LateralDraw([2.0,2.0],[1.0,1.0],100.0) ])
    #     self.writer = LayerWriter(mock_audio_writer, mock_path_to_audio, mock_laser_control, MachineState(), override_speed =100, wait_speed = 5)

    #     self.writer.process_layer(test_layer)

    #     self.assertEqual(1,mock_laser_control.set_laser_off.call_count)
    #     self.assertEqual(1,mock_laser_control.set_laser_on.call_count)
    #     self.assertEqual(([0.0,0.0,0.0],[2.0,2.0,0.0],100.0), mock_path_to_audio.process.call_args_list[0][0])
    #     self.assertEqual(([2.0,2.0,0.0],[2.0,2.0,0.0],5.0), mock_path_to_audio.process.call_args_list[1][0])


    # def test_process_layer_should_turn_off_laser_for_move_commands(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     test_layer = Layer(0.0,[ LateralMove([0.0,0.0],[2.0,2.0],100.0), LateralDraw([2.0,2.0],[2.9,2.9],100.0) ])
    #     self.writer = LayerWriter(mock_audio_writer, mock_path_to_audio, mock_laser_control, MachineState(), override_speed =100)

    #     self.writer.process_layer(test_layer)

    #     self.assertEqual(1,mock_laser_control.set_laser_off.call_count)
    #     self.assertEqual(1, mock_laser_control.set_laser_on.call_count)

    # def test_process_layer_should_output_modulate_audio_for_movement_commands(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
    #     mock_path_to_audio.process.return_value = "SomeAudio"
    #     mock_laser_control.modulate.return_value = "SomeModulatedAudio"
    #     self.writer = LayerWriter(mock_audio_writer, mock_path_to_audio, mock_laser_control, MachineState(), override_speed =100)

    #     self.writer.process_layer(test_layer)

    #     mock_laser_control.modulate.assert_called_with("SomeAudio")
    #     mock_audio_writer.write_chunk.assert_called_with("SomeModulatedAudio")

    # def test_process_layer_should_work_with_no_audio_writer(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     audio_writer = None
    #     test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],100.0) ])
    #     self.writer = LayerWriter(audio_writer, mock_path_to_audio, mock_laser_control, MachineState(), override_speed =100)

    #     self.writer.process_layer(test_layer)

    # def test_process_layer_should_call_path_to_audio_with_xyz(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
    #     self.writer = LayerWriter(mock_audio_writer, mock_path_to_audio, mock_laser_control, MachineState(), override_speed =100)

    #     self.writer.process_layer(test_layer)

    #     mock_path_to_audio.process.assert_called_with([0.0,0.0,0.0],[2.0,2.0,0.0],2.0)

    # def test_process_layer_should_remember_current_posisition(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0), LateralDraw([2.0,2.0],[-1.0,-1.0],2.0) ])

    #     self.writer = LayerWriter(mock_audio_writer, mock_path_to_audio, mock_laser_control, MachineState(), override_speed =100)

    #     self.writer.process_layer(test_layer)

    #     mock_path_to_audio.process.assert_called_with([2.0,2.0,0.0],[-1.0,-1.0,0.0],2.0)

    # def test_process_layer_if_draw_command_start_and_current_pos_are_not_the_same_should_move_to_new_posisition(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     test_layer = Layer(0.0,[LateralDraw([0.0,0.0],[0.0,0.0],2.0), LateralDraw([2.0,2.0],[-1.0,-1.0],2.0) ])
    #     self.writer = LayerWriter(mock_audio_writer, mock_path_to_audio, mock_laser_control, MachineState(), override_speed = 100)

    #     self.writer.process_layer(test_layer)

    #     self.assertEqual(3, mock_laser_control.modulate.call_count)
    #     self.assertEqual(3, mock_path_to_audio.process.call_count)
    #     mock_laser_control.set_laser_off.assert_called_with()
    #     self.assertEqual(([0.0,0.0,0.0],[2.0,2.0,0.0],2.0), mock_path_to_audio.process.call_args_list[1][0])

    # def test_process_layer_if_move_command_start_and_current_pos_are_close_to_the_same_should_not_move_to_new_posisition_for_draw(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     test_layer = Layer(0.0,[ LateralMove([0.0,0.0],[0.0,0.0],2.0), LateralDraw([0.0000001,0.0],[-1.0,-1.0],2.0) ])
    #     self.writer = LayerWriter(mock_audio_writer, mock_path_to_audio, mock_laser_control, MachineState(), override_speed =100)

    #     self.writer.process_layer(test_layer)

    #     self.assertEqual(1, mock_laser_control.modulate.call_count)
    #     self.assertEqual(1, mock_path_to_audio.process.call_count)
    #     self.assertEqual(([0.0,0.0,0.0],[-1.0,-1.0,0.0],2.0), mock_path_to_audio.process.call_args_list[0][0])

    # def test_process_layer_if_move_command_start_and_current_pos_are_close_to_the_same_should_not_move_to_new_posisition_for_move(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     test_layer = Layer(0.0,[ LateralMove([0.0,0.0],[1.0,1.0],2.0), LateralMove([1.0,1.0],[1.000001,1.0],2.0) ])
    #     self.writer = LayerWriter(mock_audio_writer, mock_path_to_audio, mock_laser_control, MachineState(), override_speed =100)

    #     self.writer.process_layer(test_layer)

    #     self.assertEqual(0, mock_laser_control.modulate.call_count)
    #     self.assertEqual(0, mock_path_to_audio.process.call_count)
    #     self.assertEqual(0, mock_laser_control.set_laser_off.call_count)

    # def test_process_layer_should_use_max_speed_if_provided(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
    #     expected_speed = 2.0
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     mock_laser_control = mock_LaserControl.return_value
    #     test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0], expected_speed + 100.0) ])
    #     self.writer = LayerWriter(mock_audio_writer, mock_path_to_audio, mock_laser_control,MachineState(),override_speed = expected_speed, )

    #     self.writer.process_layer(test_layer)

    #     mock_path_to_audio.process.assert_called_with([0.0,0.0,0.0],[2.0,2.0,0.0],2.0)

    # def test_wait_till_time_will_move_to_existing_space(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     mock_laser_control = mock_LaserControl.return_value
    #     state = MachineState()
    #     self.writer = LayerWriter(mock_audio_writer, mock_path_to_audio, mock_laser_control, state, override_speed =100 )

    #     before = time.time()
    #     self.writer.wait_till_time(before + 1 )
    #     after = time.time()

    #     self.assertTrue(before + 1 <= after )
    #     mock_path_to_audio.process.assert_called_with(state.xyz,state.xyz,state.speed)
        

    def test_post_fire_delay_will_wait_after_laser_on(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        mock_laser_control = mock_LaserControl.return_value
        state = MachineState()
        self.writer = LayerWriter(mock_audio_writer, mock_path_to_audio, mock_laser_control, state, override_speed =100, post_fire_delay_speed=100.0 )

        mock_laser_control.laser_is_on.return_value = False
        before = time.time()
        self.writer.process_layer(Layer(0.0, commands = [
            LateralMove([0.0,0.0],[1.0,1.0],100.0),
            LateralDraw([1.0,1.0],[2.0,2.0],100.0),
            ]))

        (state.xyz,state.xyz,state.speed)
        self.assertEqual( mock_path_to_audio.process.call_args_list[0][0], ([0.0,0.0,0.0],[1.0,1.0,0.0],100.0) )
        self.assertEqual( mock_path_to_audio.process.call_args_list[1][0], ([1.0,1.0,0.0],[1.0,1.0,0.0],100.0) )
        self.assertEqual( mock_path_to_audio.process.call_args_list[2][0], ([1.0,1.0,0.0],[2.0,2.0,0.0],100.0) )
        self.assertEquals( 1, mock_laser_control.set_laser_off.call_count)


#     def test_wait_till_time_returns_instantly_if_shutting_down(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
#         mock_path_to_audio = mock_PathToAudio.return_value
#         mock_audio_writer = mock_AudioWriter.return_value
#         mock_laser_control = mock_LaserControl.return_value
#         state = MachineState()
#         self.writer = LayerWriter(100, state, mock_audio_writer, mock_path_to_audio, mock_laser_control)

#         before = time.time()
#         self.writer.terminate()
#         self.writer.wait_till_time(before + 100 )
#         after = time.time()

#         self.assertTrue(before + 10 > after )

#     def test_terminate_shutsdown_audio_writer(self,mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
#         mock_path_to_audio = mock_PathToAudio.return_value
#         mock_audio_writer = mock_AudioWriter.return_value
#         mock_laser_control = mock_LaserControl.return_value
#         state = MachineState()
#         self.writer = LayerWriter(mock_audio_writer, mock_path_to_audio, mock_laser_control, state, override_speed =100 )

#         self.writer.terminate()

#         mock_audio_writer.close.assert_called_with()

#     def test_process_layer_throws_exception_if_shutting_down(self,mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
#         mock_path_to_audio = mock_PathToAudio.return_value
#         mock_audio_writer = mock_AudioWriter.return_value
#         mock_laser_control = mock_LaserControl.return_value
#         state = MachineState()
#         self.writer = LayerWriter(mock_audio_writer, mock_path_to_audio, mock_laser_control,state,override_speed =100,)
#         test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],  100.0) ])
#         self.writer.terminate()

#         with self.assertRaises(Exception):
#             self.writer.process_layer(test_layer)


# @patch('infrastructure.layer_control.LayerWriter')
# @patch('domain.zaxis.ZAxis')
# class LayerProcessingTest(unittest.TestCase):

#     def test_process_should_skip_layers_if_higher_then_max_lead_distance(self, mock_ZAxis, mock_Writer):
#         max_lead_distance = 0.1
#         mock_writer = mock_Writer.return_value
#         mock_zaxis = mock_ZAxis.return_value
#         state = MachineState()
#         status = MachineStatus()
#         mock_zaxis.current_z_location_mm.return_value = 2.0
#         test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0), LateralDraw([2.0,2.0],[-1.0,-1.0],2.0) ])
#         layer_processing = LayerProcessing(mock_writer, state, status, mock_zaxis, max_lead_distance,NullCommander(),0,'a','b','z')

#         layer_processing.process(test_layer)

#         self.assertEquals(1, status.status()['skipped_layers'],"Was: %s" % status.status()['skipped_layers'])
#         self.assertEquals(0, mock_writer.process_layer.call_count)

#     def test_process_should_print_while_dripping_until_half_max_lead(self, mock_ZAxis, mock_Writer):
#         max_lead_distance = 1.0
#         mock_writer = mock_Writer.return_value
#         mock_zaxis = mock_ZAxis.return_value
#         state = MachineState()
#         status = MachineStatus()
#         mock_zaxis.current_z_location_mm.return_value = 2.0
#         test_layer = Layer(1.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0), LateralDraw([2.0,2.0],[-1.0,-1.0],2.0) ])
#         layer_processing = LayerProcessing(mock_writer, state, status, mock_zaxis, max_lead_distance,NullCommander(),0,'a','b','z')

#         layer_processing.process(test_layer)

#         self.assertEquals(0, status.status()['skipped_layers'])
#         self.assertEquals(1, mock_writer.process_layer.call_count)
#         mock_zaxis.move_to.assert_has_calls([call(1.5)])

#     def test_process_should_ignore_z_in_layer_if_z_axis_none(self, mock_ZAxis, mock_Writer):
#         mock_writer = mock_Writer.return_value
#         mock_zaxis = mock_ZAxis.return_value
#         state = MachineState()
#         status = MachineStatus()
#         test_layer = Layer(1.0, [ LateralDraw([2.0,2.0],[0.0,0.0],2.0) ])
#         layer_processing = LayerProcessing(mock_writer, state, status, None, 0.0,NullCommander(),0,'a','b','z')

#         layer_processing.process(test_layer)

#         mock_writer.process_layer.assert_called_with(test_layer)

#     def test_process_should_wait_for_zaxis(self, mock_ZAxis, mock_Writer):
#         mock_writer = mock_Writer.return_value
#         mock_zaxis = mock_ZAxis.return_value
#         state = MachineState()
#         status = MachineStatus()
#         zaxis_return_values = [ 0.0, 0.0, 1.0, 1.0 ]
#         def z_axis_side_effect():
#             return zaxis_return_values.pop(0)
#         mock_zaxis.current_z_location_mm = z_axis_side_effect
#         test_layer = Layer(1.0, [ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
#         layer_processing = LayerProcessing(mock_writer, state, status, mock_zaxis, 0.0, NullCommander(), 0, 'a','b','z')

#         layer_processing.process(test_layer)

#         self.assertEqual(1, mock_writer.process_layer.call_count)
#         self.assertEqual(2, mock_writer.wait_till_time.call_count)

#     @patch('infrastructure.machine.MachineStatus')
#     def test_process_should_set_waiting_while_wating_for_z(self, mock_MachineStatus, mock_ZAxis, mock_Writer):
#         mock_writer = mock_Writer.return_value
#         mock_zaxis = mock_ZAxis.return_value
#         mock_machinestatus = mock_MachineStatus.return_value
#         state = MachineState()
#         zaxis_return_values = [0.0,1.0,1.0]
#         def z_axis_side_effect():
#             logging.info(zaxis_return_values[0])
#             return zaxis_return_values.pop(0)
#         mock_zaxis.current_z_location_mm = z_axis_side_effect

#         test_layer = Layer(1.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])

#         layer_processing = LayerProcessing(mock_writer, state, mock_machinestatus, mock_zaxis, 0.0, NullCommander(), 0, 'a','b','z')

#         layer_processing.process(test_layer)

#         self.assertEqual(1, mock_writer.process_layer.call_count)
#         self.assertEqual(1, mock_writer.wait_till_time.call_count)
#         self.assertEqual(1, mock_machinestatus.set_waiting_for_drips.call_count)
#         self.assertEqual(1, mock_machinestatus.set_not_waiting_for_drips.call_count)

#     @patch('infrastructure.commander.Commander')
#     def test_process_should_write_layer_start_and_end_commands(self, mock_Commander, mock_ZAxis, mock_Writer):
#         mock_commander = mock_Commander.return_value
#         mock_zaxis = mock_ZAxis.return_value
#         mock_writer = mock_Writer.return_value
#         state = MachineState()
#         status = MachineStatus()
#         mock_zaxis.current_z_location_mm.return_value = 2.0
#         test_layer = Layer(1.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0), LateralDraw([2.0,2.0],[-1.0,-1.0],2.0) ])
#         layer_processing = LayerProcessing(mock_writer, state, status, mock_zaxis, 1.0,mock_commander,0,'a','b','z')

#         layer_processing.process(test_layer)

#         self.assertEquals([call('a'),call('b')], mock_commander.send_command.call_args_list)

#     @patch('infrastructure.commander.Commander')
#     def test_termiate_should_write_print_end_command_when_terminated(self, mock_Commander, mock_ZAxis,mock_Writer):
#         max_lead_distance = 1.0
#         mock_commander = mock_Commander.return_value
#         mock_writer = mock_Writer.return_value
#         mock_zaxis = mock_ZAxis.return_value
#         state = MachineState()
#         status = MachineStatus()
#         layer_processing = LayerProcessing(mock_writer, state, status, mock_zaxis, max_lead_distance,mock_commander,0,'a','b','z')

#         layer_processing.terminate()

#         self.assertEquals([call('z')], mock_commander.send_command.call_args_list)

#     def test_terminate_should_stop_z_axis(self, mock_ZAxis,mock_Writer):
#         mock_zaxis = mock_ZAxis.return_value
#         layer_processing = LayerProcessing(
#             mock_Writer.return_value, 
#             MachineState(),
#             MachineStatus(), 
#             mock_zaxis, 
#             1.0,
#             NullCommander(),
#             0,'a','b','z')

#         layer_processing.terminate()

#         mock_zaxis.close.assert_called_with()

#     @patch('infrastructure.commander.Commander')
#     def test_terminate_should_shutdown_commander(self, mock_Commander, mock_ZAxis,mock_Writer):
#         mock_zaxis = mock_ZAxis.return_value
#         mock_commander = mock_Commander.return_value
#         layer_processing = LayerProcessing(
#             mock_Writer.return_value, 
#             MachineState(),
#             MachineStatus(), 
#             mock_zaxis, 
#             1.0,
#             mock_commander,
#             0,'a','b','z')

#         layer_processing.terminate()

#         mock_commander.close.assert_called_with()

#     def test_process_while_shutting_down_should_exit(self, mock_ZAxis,mock_Writer):
#         mock_zaxis = mock_ZAxis.return_value
#         layer_processing = LayerProcessing(
#             mock_Writer.return_value, 
#             MachineState(),
#             MachineStatus(), 
#             mock_zaxis, 
#             1.0,
#             NullCommander(),
#             0,'a','b','z')
#         layer_processing.terminate()
#         with self.assertRaises(Exception):
#             layer_processing.process(Layer(1.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ]))

#     def test_process_should_update_layer_height(self, mock_ZAxis,mock_Writer):
#         mock_zaxis = mock_ZAxis.return_value
#         status = MachineStatus()
#         layer_processing = LayerProcessing(
#             mock_Writer.return_value, 
#             MachineState(),
#             status, 
#             mock_zaxis, )
#         expected_model_height = 32.7
#         mock_zaxis.current_z_location_mm.return_value = expected_model_height
        
#         test_layer = Layer(expected_model_height,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
        
#         layer_processing.process(test_layer)

#         actual = status.status()['model_height']
#         self.assertEquals(expected_model_height,actual)


#     def test_process_should_set_waiting_for_drips(self, mock_ZAxis,mock_Writer):
#         mock_zaxis = mock_ZAxis.return_value
#         status = MachineStatus()
#         layer_processing = LayerProcessing(
#             mock_Writer.return_value, 
#             MachineState(),
#             status, 
#             mock_zaxis, )
#         expected_model_height = 32.7
#         z_axis_results = [expected_model_height - 1, expected_model_height, expected_model_height]
#         actual = []
#         def side_effect():
#             actual.append(status.status()['waiting_for_drips'])
#             return z_axis_results.pop(0)

#         mock_zaxis.current_z_location_mm.side_effect = side_effect

        
#         test_layer = Layer(expected_model_height,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
        
#         layer_processing.process(test_layer)
        
#         actual.append(status.status()['waiting_for_drips'])
#         self.assertTrue( actual[0])
#         self.assertTrue(  actual[1])
#         self.assertFalse( actual[2])

#     def test_process_should_tell_writer_to_wait_when_prelayer_delay(self, mock_ZAxis,mock_Writer):
#         mock_zaxis = mock_ZAxis.return_value
#         mock_writer = mock_Writer.return_value
#         pre_layer_delay = 0.1
#         status = MachineStatus()
#         layer_processing = LayerProcessing(
#             mock_writer,
#             MachineState(),
#             status, 
#             mock_zaxis, 
#             pre_layer_delay = pre_layer_delay,
#             )
#         mock_zaxis.current_z_location_mm.return_value = 1.0
        
#         test_layer = Layer(1.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
        
#         start_time = time.time()
#         layer_processing.process(test_layer)
#         end_time = time.time()
        
#         self.assertTrue(mock_writer.wait_till_time.call_args_list[0][0][0]  >= start_time + pre_layer_delay ,"Was %s, expected: %s" % (mock_writer.wait_till_time.call_args_list[0][0]  ,start_time + pre_layer_delay) )
#         self.assertTrue(mock_writer.wait_till_time.call_args_list[0][0][0]  <= end_time + pre_layer_delay   ,"Was %s, expected: %s" % (mock_writer.wait_till_time.call_args_list[0][0]  ,start_time + pre_layer_delay) )

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()