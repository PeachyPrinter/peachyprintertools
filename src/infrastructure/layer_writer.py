import time
import logging
from domain.commands import *
from threading import Lock

class LayerWriter():
    def __init__(self, 
        override_speed,
        state,
        audio_writer,
        path_to_audio,
        laser_control
        ):
        self._override_speed = override_speed
        self._state = state
        self._audio_writer = audio_writer
        self._path_to_audio = path_to_audio
        self._laser_control = laser_control
        self.laser_off_override = False

        self._abort_current_command = False
        self._shutting_down = False
        self._shutdown = False
        self._lock = Lock()

    def _almost_equal(self,a,b,sig_fig=5):
        return ( a==b or int(a*10**sig_fig) == int(b*10**sig_fig))

    def _same_posisition(self,pos_1,pos_2):
        return self._almost_equal(pos_1[0],pos_2[0]) and self._almost_equal(pos_1[1],pos_2[1])

    def process_layer(self, layer):
        if self._shutting_down or self._shutdown:
            raise Exception("LayerWriter already shutdown")
        with self._lock:
            for command in layer.commands:
                # logging.info("Processing command: %s" % command)
                if self._shutting_down:
                    return
                if self._abort_current_command:
                    self._abort_current_command = False
                    return
                if type(command) == LateralDraw:
                    if not self._same_posisition(self._state.xy, command.start):
                        self._move_lateral(command.start,layer.z,command.speed)
                    self._draw_lateral(command.end, layer.z, command.speed )
                elif type(command) == LateralMove:
                    self._move_lateral(command.end, layer.z, command.speed)

    def _move_lateral(self,(to_x,to_y), to_z,speed):
        self._laser_control.set_laser_off()
        for i in range(0,1):
            self._write_lateral(to_x,to_y,to_z,speed)

    def _draw_lateral(self,(to_x,to_y), to_z,speed):
        if self.laser_off_override:
            self._laser_control.set_laser_off()
        else:
            self._laser_control.set_laser_on()
        for i in range(0,1):
            self._write_lateral(to_x,to_y,to_z,speed)
    
    def _write_lateral(self,to_x,to_y, to_z,speed):
        if self._override_speed and speed > self._override_speed:
            speed = self._override_speed
        to_xyz = [to_x,to_y,to_z]
        path = self._path_to_audio.process(self._state.xyz,to_xyz , speed)
        modulated_path = self._laser_control.modulate(path)
        if self._audio_writer:
            self._audio_writer.write_chunk(modulated_path)
        self._state.set_state(to_xyz,speed)

    def abort_current_command(self):
        self._abort_current_command = True

    def wait_till_time(self, wait_time):
        while time.time() <= wait_time:
            if self._shutting_down:
                return
            self._move_lateral(self._state.xy, self._state.z,self._state.speed)

    def terminate(self):
        self._shutting_down = True
        with self._lock:
            self._shutdown = True
            try:
                self._audio_writer.close()
                logging.info("Audio shutdown correctly")
            except Exception as ex:
                logging.error(ex)