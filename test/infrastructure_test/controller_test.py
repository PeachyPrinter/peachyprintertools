import unittest
import os
import sys
from mock import patch

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from infrastructure.controller import Controller 
from domain.commands import *
from infrastructure.layer_generators import StubLayerGenerator

@patch('domain.laser_control.LaserControl')
@patch('domain.zaxis.ZAxis')
@patch('infrastructure.audiofiler.PathToAudio')
@patch('infrastructure.audio_writer.AudioWriter')
@patch('domain.layer_generator.LayerGenerator')
class ControllerTests(unittest.TestCase):

    def test_should_turn_on_laser_for_draw_commands(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],100.0) ])
        stub_layer_generator = StubLayerGenerator([test_layer])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"

        controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator)
        controller.start()

        self.assertEqual(1,mock_laser_control.set_laser_on.call_count)

    def test_should_turn_off_laser_for_move_commands(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralMove([0.0,0.0],[2.0,2.0],100.0) ])
        stub_layer_generator = StubLayerGenerator([test_layer])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"
                
        controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator)
        controller.start()

        self.assertEqual(1,mock_laser_control.set_laser_off.call_count)
        self.assertEqual(0,mock_laser_control.set_laser_on.call_count)

    def test_should_output_modulated_audio_for_movement_commands(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
        stub_layer_generator = StubLayerGenerator([test_layer])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"

        controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator)
        controller.start()

        mock_path_to_audio.process.assert_called_with([0.0,0.0],[2.0,2.0],2.0)
        mock_laser_control.modulate.assert_called_with("SomeAudio")
        mock_audio_writer.write_chunk.assert_called_with("SomeModulatedAudio")

    def test_should_remember_current_posisition(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0), LateralDraw([2.0,2.0],[-1.0,-1.0],2.0) ])
        stub_layer_generator = StubLayerGenerator([test_layer])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"

        controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator)
        controller.start()

        mock_path_to_audio.process.assert_called_with([2.0,2.0],[-1.0,-1.0],2.0)

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

        controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator)
        controller.start()

        mock_laser_control.modulate.call_count = 3
        mock_path_to_audio.process.call_count = 3
        mock_laser_control.set_laser_off.assert_called_with()
        self.assertEqual(([0.0,0.0],[2.0,2.0],2.0), mock_path_to_audio.process.call_args_list[1][0])

    def test_if_move_command_start_and_current_pos_are_not_the_same_should_move_to_new_posisition(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer = Layer(0.0,[ LateralMove([0.0,0.0],[0.0,0.0],2.0), LateralMove([2.0,2.0],[-1.0,-1.0],2.0) ])
        stub_layer_generator = StubLayerGenerator([test_layer])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"

        controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator)
        controller.start()

        mock_laser_control.modulate.call_count = 2
        mock_path_to_audio.process.call_count = 2
        mock_laser_control.set_laser_off.assert_called_with()
        self.assertEqual(([0.0,0.0],[-1.0,-1.0],2.0), mock_path_to_audio.process.call_args_list[1][0])

    def test_should_ignore_z_in_layer_if_z_axis_none(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        mock_laser_control = mock_LaserControl.return_value
        mock_path_to_audio = mock_PathToAudio.return_value
        mock_audio_writer = mock_AudioWriter.return_value
        test_layer1 = Layer(0.0, [ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
        test_layer2 = Layer(1.0, [ LateralDraw([2.0,2.0],[0.0,0.0],2.0) ])
        stub_layer_generator = StubLayerGenerator([test_layer1,test_layer2])
        mock_path_to_audio.process.return_value = "SomeAudio"
        mock_laser_control.modulate.return_value = "SomeModulatedAudio"

        controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator,None)
        controller.start()

        self.assertEqual(2,mock_path_to_audio.process.call_count)
        mock_path_to_audio.process.assert_called_with([2.0,2.0],[0.0,0.0],2.0)

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

        controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator, mock_zaxis)
        controller.start()

        self.assertEqual(4, mock_path_to_audio.process.call_count)
        self.assertEqual(2, mock_laser_control.set_laser_off.call_count)
        self.assertEqual(([2.0,2.0],[2.0,2.0],2.0), mock_path_to_audio.process.call_args_list[1][0])
        self.assertEqual(([2.0,2.0],[2.0,2.0],2.0), mock_path_to_audio.process.call_args_list[2][0])

    def test_sublayers(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
        #Expand
        pass

    #TODO JT
    #Skip layers if z at next layer

if __name__ == '__main__':
    unittest.main()