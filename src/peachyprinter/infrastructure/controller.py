import threading
import logging
import time
import traceback
from peachyprinter.domain.commands import *
from peachyprinter.infrastructure.machine import MachineError


class Controller(threading.Thread,):
    def __init__(self,
                 layer_writer,
                 layer_processer,
                 layer_generator,
                 status,
                 abort_on_error=True,
                 ):
        threading.Thread.__init__(self)

        self._shutting_down = False
        self._shutdown = False
        self._pausing = False

        self._abort_on_error = abort_on_error
        self._layer_generator = layer_generator
        self._layer_processing = layer_processer
        self._writer = layer_writer
        self._status = status
        self._next_layer_generator = None
        self._run_lock = threading.Lock()
        self._generator_lock = threading.Lock()

    def run(self):
        with self._run_lock:
            logging.info('Running Controller')
            self._process_layers()
            self._status.set_complete()
            self._writer.terminate()
            self._layer_processing.terminate()
            logging.info('Controller Shutdown')

    def change_generator(self, layer_generator):
        logging.info("Generator change requested")
        with self._generator_lock:
            self._layer_processing.abort_current_command()
            self._layer_generator = layer_generator

    def get_status(self):
        return self._status.status()

    def close(self):
        logging.info('Controller shutdown requested')
        self._shutting_down = True
        self._layer_processing.abort_current_command()
        self._run_lock.acquire()
        self._run_lock.release()

    def _process_layers(self):
        while not self._shutting_down:
            try:
                with self._generator_lock:
                    layer = self._layer_generator.next()
                self._layer_processing.process(layer)
            except StopIteration:
                logging.info('Layers Complete')
                return
            except Exception as ex:
                self._status.add_error(MachineError(str(ex), self._status.status()['current_layer']))
                logging.error('Unexpected Error: %s' % str(ex))
                traceback.print_exc()
                if self._abort_on_error:
                    return
