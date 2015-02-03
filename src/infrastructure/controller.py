import threading
import logging
import time
import traceback
from domain.commands import *
from infrastructure.machine import MachineError


class Controller(threading.Thread,):
    def __init__(self,
                 layer_writer,
                 layer_processer,
                 layer_generator,
                 status,
                 abort_on_error=True,
                 ):
        threading.Thread.__init__(self)
        self.deamon = True

        self._shutting_down = False
        self.running = False
        self.starting = True
        self._shutdown = False
        self._lock = threading.Lock()
        self._pausing = False

        self._abort_on_error = abort_on_error
        self._layer_generator = layer_generator
        self._layer_processing = layer_processer
        self._writer = layer_writer
        self._status = status

    def run(self):
        logging.info('Running Controller')
        self.running = True
        self.starting = False
        self._process_layers()
        self.running = False
        self._terminate()
        self._status.set_complete()

    def change_generator(self, layer_generator):
        self._writer.abort_current_command()
        logging.debug("Lock aquiring change")
        with self._lock:
            self._layer_generator = layer_generator
        logging.debug("Lock releaseing change")

    def get_status(self):
        return self._status.status()

    def close(self):
        logging.warning("Shutdown requested")
        if not self._shutting_down:
            self._shutting_down = True
            self._writer.terminate()
            self._layer_processing.terminate()
        attempts = 20
        while not self._shutdown and attempts > 0:
            attempts -= 1
            time.sleep(1)
            logging.info("Waiting for Controller Shutdown Correctly")
        if attempts > 0:
            logging.info("Controller Shutdown Correctly")
        else:
            logging.info("Controller Failed Shutting Down.")

    def _process_layers(self):
        logging.info('Start Processing Layers')
        while not self._shutting_down:
            logging.debug("Lock aquiring process")
            with self._lock:
                try:
                    layer = self._layer_generator.next()
                    self._layer_processing.process(layer)
                except StopIteration:
                    logging.info('Layers Complete')
                    self._shutting_down = True
                except Exception as ex:
                    self._status.add_error(MachineError(str(ex), self._status.status()['current_layer']))
                    logging.error('Unexpected Error: %s' % str(ex))
                    traceback.print_exc()
                    if self._abort_on_error:
                        self._shutting_down = True
            logging.debug("Lock released process")
        logging.info("Processing Layers Complete")

    def _terminate(self):
        logging.info('Controller shutdown requested')
        self._shutting_down = True
        self._writer.abort_current_command()
        self._writer.terminate()
        self._layer_processing.terminate()
        self._shutdown = True
