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
from infrastructure.layer_writer import *
from domain.commands import *
from infrastructure.machine import *

@patch('domain.laser_control.LaserControl')
@patch('infrastructure.audiofiler.PathToAudio')
@patch('infrastructure.audio.AudioWriter')
class LayerWriterTests(unittest.TestCase):
    def test_process_layer_should_turn_off_laser_for_draw_commands_when_forced_off(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],100.0) ])
        self.writer = LayerWriter(100, MachineState(), mock_audio_writer, mock_path_to_audio, mock_laser_control)
        self.writer.laser_off_override = True

        self.writer.process_layer(test_layer)

        self.assertEqual(1,mock_laser_control.set_laser_off.call_count)
        self.assertEqual(0,mock_laser_control.set_laser_on.call_count)

    def test_process_layer_should_turn_on_laser_for_draw_commands(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],100.0) ])
        self.writer = LayerWriter(100, MachineState(), mock_audio_writer, mock_path_to_audio, mock_laser_control)

        self.writer.process_layer(test_layer)

        self.assertEqual(1,mock_laser_control.set_laser_on.call_count)

    def test_process_layer_should_turn_off_laser_for_move_commands(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralMove([0.0,0.0],[2.0,2.0],100.0) ])
        self.writer = LayerWriter(100, MachineState(), mock_audio_writer, mock_path_to_audio, mock_laser_control)

        self.writer.process_layer(test_layer)

        self.assertEqual(1,mock_laser_control.set_laser_off.call_count)
        self.assertEqual(0,mock_laser_control.set_laser_on.call_count)

    def test_process_layer_should_output_modulate_audio_for_movement_commands(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"
        self.writer = LayerWriter(100, MachineState(), mock_audio_writer, mock_path_to_audio, mock_laser_control)

        self.writer.process_layer(test_layer)

        mock_laser_control.modulate.assert_called_with("SomeAudio")
        mock_audio_writer.write_chunk.assert_called_with("SomeModulatedAudio")

    def test_process_layer_should_work_with_no_audio_writer(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        audio_writer = None
        test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],100.0) ])
        self.writer = LayerWriter(100, MachineState(), audio_writer, mock_path_to_audio, mock_laser_control)

        self.writer.process_layer(test_layer)

    def test_process_layer_should_call_path_to_audio_with_xyz(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
        self.writer = LayerWriter(100, MachineState(), mock_audio_writer, mock_path_to_audio, mock_laser_control)

        self.writer.process_layer(test_layer)

        mock_path_to_audio.process.assert_called_with([0.0,0.0,0.0],[2.0,2.0,0.0],2.0)

    def test_process_layer_should_remember_current_posisition(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0), LateralDraw([2.0,2.0],[-1.0,-1.0],2.0) ])

        self.writer = LayerWriter(100, MachineState(), mock_audio_writer, mock_path_to_audio, mock_laser_control)

        self.writer.process_layer(test_layer)

        mock_path_to_audio.process.assert_called_with([2.0,2.0,0.0],[-1.0,-1.0,0.0],2.0)

    def test_process_layer_if_draw_command_start_and_current_pos_are_not_the_same_should_move_to_new_posisition(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[LateralDraw([0.0,0.0],[0.0,0.0],2.0), LateralDraw([2.0,2.0],[-1.0,-1.0],2.0) ])
        self.writer = LayerWriter(100, MachineState(), mock_audio_writer, mock_path_to_audio, mock_laser_control)

        self.writer.process_layer(test_layer)

        self.assertEqual(3, mock_laser_control.modulate.call_count)
        self.assertEqual(3, mock_path_to_audio.process.call_count)
        mock_laser_control.set_laser_off.assert_called_with()
        self.assertEqual(([0.0,0.0,0.0],[2.0,2.0,0.0],2.0), mock_path_to_audio.process.call_args_list[1][0])

    def test_process_layer_if_move_command_start_and_current_pos_are_not_the_same_should_move_to_new_posisition(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralMove([0.0,0.0],[0.0,0.0],2.0), LateralMove([2.0,2.0],[-1.0,-1.0],2.0) ])
        self.writer = LayerWriter(100, MachineState(), mock_audio_writer, mock_path_to_audio, mock_laser_control)

        self.writer.process_layer(test_layer)

        self.assertEqual(2, mock_laser_control.modulate.call_count)
        self.assertEqual(2, mock_path_to_audio.process.call_count)
        mock_laser_control.set_laser_off.assert_called_with()
        self.assertEqual(([0.0,0.0,0.0],[-1.0,-1.0,0.0],2.0), mock_path_to_audio.process.call_args_list[1][0])

    def test_process_layer_if_move_command_start_and_current_pos_are_close_to_the_same_should_not_move_to_new_posisition(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralMove([0.0,0.0],[0.0,0.0],2.0), LateralDraw([0.0000001,0.0],[-1.0,-1.0],2.0) ])
        self.writer = LayerWriter(100, MachineState(), mock_audio_writer, mock_path_to_audio, mock_laser_control)

        self.writer.process_layer(test_layer)

        self.assertEqual(2, mock_laser_control.modulate.call_count)
        self.assertEqual(2, mock_path_to_audio.process.call_count)
        mock_laser_control.set_laser_off.assert_called_with()
        self.assertEqual(([0.0,0.0,0.0],[-1.0,-1.0,0.0],2.0), mock_path_to_audio.process.call_args_list[1][0])

    def test_process_layer_should_use_max_speed_if_provided(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
        expected_speed = 2.0
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        mock_laser_control = mock_LaserControl.return_value
        test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0], expected_speed + 100.0) ])
        self.writer = LayerWriter(expected_speed, MachineState(), mock_audio_writer, mock_path_to_audio, mock_laser_control)

        self.writer.process_layer(test_layer)

        mock_path_to_audio.process.assert_called_with([0.0,0.0,0.0],[2.0,2.0,0.0],2.0)

    def test_wait_till_time_will_move_to_existing_space(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        mock_laser_control = mock_LaserControl.return_value
        state = MachineState()
        self.writer = LayerWriter(100, state, mock_audio_writer, mock_path_to_audio, mock_laser_control)

        before = time.time()
        self.writer.wait_till_time(before + 1 )
        after = time.time()

        self.assertTrue(before + 1 <= after )
        mock_path_to_audio.process.assert_called_with(state.xyz,state.xyz,state.speed)
        

    def test_wait_till_time_returns_instantly_if_shutting_down(self, mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        mock_laser_control = mock_LaserControl.return_value
        state = MachineState()
        self.writer = LayerWriter(100, state, mock_audio_writer, mock_path_to_audio, mock_laser_control)

        before = time.time()
        self.writer.terminate()
        self.writer.wait_till_time(before + 100 )
        after = time.time()

        self.assertTrue(before + 10 > after )

    def test_terminate_shutsdown_audio_writer(self,mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        mock_laser_control = mock_LaserControl.return_value
        state = MachineState()
        self.writer = LayerWriter(100, state, mock_audio_writer, mock_path_to_audio, mock_laser_control)

        self.writer.terminate()

        mock_audio_writer.close.assert_called_with()

    def test_process_layer_throws_exception_if_shutting_down(self,mock_AudioWriter,mock_PathToAudio,mock_LaserControl):
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        mock_laser_control = mock_LaserControl.return_value
        state = MachineState()
        self.writer = LayerWriter(100, state, mock_audio_writer, mock_path_to_audio, mock_laser_control)
        test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],  100.0) ])
        self.writer.terminate()

        with self.assertRaises(Exception):
            self.writer.process_layer(test_layer)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()