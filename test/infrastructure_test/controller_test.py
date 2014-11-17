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
from infrastructure.controller import *
from infrastructure.layer_generators import StubLayerGenerator, SinglePointGenerator

@patch('domain.laser_control.LaserControl')
@patch('domain.zaxis.ZAxis')
@patch('infrastructure.audiofiler.PathToAudio')
@patch('infrastructure.audio.AudioWriter')
@patch('domain.layer_generator.LayerGenerator')
class ControllerTests(unittest.TestCase):
    controller = None

    def wait_for_controller(self):
        while self.controller.starting or self.controller.running:
            time.sleep(0.01)

    def tearDown(self):
        if self.controller and self.controller.is_alive():
            self.controller.close()

    # def test_close_should_close_all_processes_cleanly(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     mock_zaxis = mock_ZAxis.return_value
    #     mock_layer_generator = mock_LayerGenerator.return_value
    #     mock_layer_generator.next.return_value =  Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
    #     mock_path_to_audio.process.return_value = "SomeAudio"
    #     mock_laser_control.modulate.return_value = "SomeModulatedAudio"
    #     self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,mock_layer_generator,mock_zaxis)
    #     self.controller.start()

    #     time.sleep(0.1)

    #     self.controller.close()

    #     time.sleep(0.1)

    #     mock_zaxis.close.assert_called_with()
    #     mock_audio_writer.close.assert_called_with()

    # def test_stop_should_close_all_processes_cleanly_while_waiting_for_z(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     mock_zaxis = mock_ZAxis.return_value
    #     mock_zaxis.current_z_location_mm.return_value = 0.0
    #     mock_layer_generator = mock_LayerGenerator.return_value
    #     mock_layer_generator.next.return_value =   Layer(1.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
    #     mock_path_to_audio.process.return_value = "SomeAudio"
    #     mock_laser_control.modulate.return_value = "SomeModulatedAudio"
    #     mock_commander = MagicMock()
    #     self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,mock_layer_generator,mock_zaxis, commander = mock_commander)
    #     self.controller.start()

    #     time.sleep(0.1)

    #     self.controller.close()

    #     self.wait_for_controller()

    #     mock_zaxis.close.assert_called_with()
    #     mock_audio_writer.close.assert_called_with()
    #     mock_commander.close.assert_called_with()

    # def test_stop_should_close_all_processes_cleanly_while_working_on_commands(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     mock_layer_generator = mock_LayerGenerator.return_value
    #     test_layer = Layer(1.0, [ LateralDraw([2.0,2.0],[0.0,0.0],2.0) for x in range(0,32768)])
    #     stub_layer_generator = StubLayerGenerator([test_layer])
    #     mock_path_to_audio.process.return_value = "SomeAudio"
    #     mock_laser_control.modulate.return_value = "SomeModulatedAudio"
    #     self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator)
    #     self.controller.start()
    #     time.sleep(0.1)

    #     self.controller.close()
    #     time.sleep(0.1)

    #     mock_audio_writer.close.assert_called_with()
        
    #     self.wait_for_controller()

    # def test_should_update_layer_height(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
    #     expected_model_height = 32.7
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     mock_zaxis = mock_ZAxis.return_value
    #     mock_zaxis.current_z_location_mm.return_value = 23.2
    #     mock_layer_generator = mock_LayerGenerator.return_value
    #     mock_layer_generator.next.return_value = Layer(expected_model_height,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
    #     mock_path_to_audio.process.return_value = "SomeAudio"
    #     mock_laser_control.modulate.return_value = "SomeModulatedAudio"
    #     self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,mock_layer_generator,mock_zaxis)
    #     self.controller.start()
    #     time.sleep(0.01)
    #     self.controller.close()

    #     self.wait_for_controller()
    #     actual = self.controller.get_status()['model_height']

    #     self.assertEquals(expected_model_height,actual)

    # def test_set_waiting_while_not_wating_for_z(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     mock_zaxis = mock_ZAxis.return_value
    #     mock_zaxis.current_z_location_mm.return_value = 1.0
    #     mock_layer_generator = mock_LayerGenerator.return_value
    #     mock_layer_generator.next.return_value =  Layer(1.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
    #     mock_path_to_audio.process.return_value = "SomeAudio"
    #     mock_laser_control.modulate.return_value = "SomeModulatedAudio"
    #     self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,mock_layer_generator,mock_zaxis)
    #     self.controller.start()

    #     time.sleep(0.1)
    #     actual = self.controller.get_status()['waiting_for_drips']
    #     self.controller.close()

    #     self.wait_for_controller()

    #     self.assertFalse(actual)
        
    # def test_should_update_machine_status(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     test_layer = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],100.0) ])
    #     stub_layer_generator = StubLayerGenerator([test_layer])
    #     mock_path_to_audio.process.return_value = "SomeAudio"
    #     mock_laser_control.modulate.return_value = "SomeModulatedAudio"

    #     self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator)
    #     self.controller.start()

    #     self.wait_for_controller()

    #     self.assertEquals(1, self.controller.get_status()['current_layer'])
    #     self.assertEquals('Complete',self.controller.get_status()['status'])

    # def test_should_record_errors_and_abort(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     mock_layer_generator = mock_LayerGenerator.return_value
    #     mock_layer_generator.next.return_value =  Layer(1.0,[ LateralDraw([0.0,0.0],[2.0,2.0],2.0) ])
    #     mock_path_to_audio.process.side_effect = Exception("Something Broke")
    #     mock_laser_control.modulate.return_value = "SomeModulatedAudio"

    #     self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,mock_layer_generator)
    #     self.controller.start()

    #     self.wait_for_controller()

    #     self.assertEquals(1, len(self.controller.get_status()['errors']))
    #     self.assertEquals("Something Broke", self.controller.get_status()['errors'][0]['message'])

    # def test_should_record_errors_and_continue_when_abort_on_error_is_false(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     test_layer1 = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],100.0) ])
    #     test_layer2 = Layer(0.0,[ LateralDraw([0.0,0.0],[2.0,2.0],100.0) ])
    #     stub_layer_generator = StubLayerGenerator([test_layer1, test_layer2])
    #     mock_path_to_audio.process.side_effect = Exception("Something Broke")
    #     mock_laser_control.modulate.return_value = "SomeModulatedAudio"

    #     self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator, abort_on_error = False)
    #     self.controller.start()

    #     self.wait_for_controller()

    #     self.assertEquals(2, len(self.controller.get_status()['errors']))

    # def test_should_change_layer_generator(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value

    #     generator1 = SinglePointGenerator([1.0,1.0])
    #     generator2 = SinglePointGenerator([0.0,0.0])

    #     self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,generator1)
    #     self.controller.start()
    #     time.sleep(0.1)
    #     pre_switch = mock_path_to_audio.process.call_args
    #     self.controller.change_generator(generator2)
    #     time.sleep(0.1)
    #     post_switch = mock_path_to_audio.process.call_args
    #     self.controller.close()
    #     self.wait_for_controller()

    #     self.assertEquals( ([1.0,1.0,0.0],[1.0,1.0,0.0],100.0), pre_switch[0] )
    #     self.assertEquals( ([0.0,0.0,0.0],[0.0,0.0,0.0],100.0), post_switch[0] )

    # def test_stop_should_stop_working_on_commands_when_generator_changed(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     mock_layer_generator = mock_LayerGenerator.return_value
    #     test_layer1 = Layer(1.0, [ LateralDraw([2.0,2.0],[0.0,0.0],2.0) for x in range(0,32768)])
    #     stub_layer_generator1 = StubLayerGenerator([test_layer1])
    #     test_layer2 = Layer(1.0, [ LateralDraw([0.0,0.0],[0.0,0.0],2.0)] )
    #     stub_layer_generator2 = StubLayerGenerator([test_layer2])
    #     mock_path_to_audio.process.return_value = "SomeAudio"
    #     mock_laser_control.modulate.return_value = "SomeModulatedAudio"
    #     self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator1)
    #     self.controller.start()
    #     time.sleep(0.1)

    #     self.controller.change_generator(stub_layer_generator2)
    #     time.sleep(0.1)

    #     mock_path_to_audio.process.assert_called_with([0.0,0.0,1.0],[0.0,0.0,1.0],2.0)
        
    #     self.wait_for_controller()

    # def test_init_should_set_call_back_on_zaxis(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     mock_layer_generator = mock_LayerGenerator.return_value
    #     mock_zaxis = mock_ZAxis.return_value
    #     Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,mock_layer_generator, mock_zaxis)

    #     self.assertTrue(mock_zaxis.set_call_back.called)

    # def test_should_write_moves_if_prelayer_delay(self, mock_LayerGenerator,mock_AudioWriter,mock_PathToAudio,mock_ZAxis,mock_LaserControl):
    #     mock_laser_control = mock_LaserControl.return_value
    #     mock_path_to_audio = mock_PathToAudio.return_value
    #     mock_audio_writer = mock_AudioWriter.return_value
    #     test_layer1 = Layer(0.0,[ LateralDraw([2.0,2.0],[2.0,2.0],100.0) ])
    #     test_layer2 = Layer(1.0,[ LateralDraw([2.0,2.0],[2.0,2.0],100.0) ])
    #     stub_layer_generator = StubLayerGenerator([test_layer1, test_layer2])
    #     mock_path_to_audio.process.return_value = "SomeAudio"
    #     mock_laser_control.modulate.return_value = "SomeModulatedAudio"

    #     self.controller = Controller(mock_laser_control,mock_path_to_audio,mock_audio_writer,stub_layer_generator, pre_layer_delay = 0.1)
    #     self.controller.start()

    #     self.wait_for_controller()

    #     mock_path_to_audio.process.call_count

    #     self.assertTrue( 10 < mock_path_to_audio.process.call_count,mock_path_to_audio.process.call_count) #Calls are appxorimate 
    #     self.assertTrue( 3000 > mock_path_to_audio.process.call_count,mock_path_to_audio.process.call_count) #Calls are appxorimate 

        

#     # TODO JT
#     # Skip layers if z at next layer

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='DEBUG')
    unittest.main()