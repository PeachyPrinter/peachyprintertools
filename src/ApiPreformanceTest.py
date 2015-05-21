import logging
import os
import sys
import time
from peachyprinter import config, PrinterAPI
import signal
import sys

print_api = None


def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        global print_api
        print_api.close()
        sys.exit(0)


def setup_logging():
    peachy_logger = logging.getLogger('peachy')
    logging_format = '%(levelname)s: %(asctime)s %(module)s - %(message)s'
    logging_level = "INFO"

    peachy_logger.propagate = False
    logFormatter = logging.Formatter(logging_format)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    peachy_logger.addHandler(consoleHandler)
    peachy_logger.setLevel(logging_level)


def callback(data):
    pass


def run():
    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C to exit')
    global print_api
    setup_logging()
    api = PrinterAPI()
    api.load_printer()
    print_api = api.get_print_api(status_call_back=callback)
    test_print_api = api.get_test_print_api()
    name = "Simple 5 Sided 180 Twist Vase (BETA)"
    height = 80.0
    width = 80.0
    layer_height = 0.01
    speed = 120.0
    generator = test_print_api.get_test_print(name, height, width, layer_height, speed)

    print_api.print_layers(generator)
    signal.pause()

if __name__ == "__main__":
    run()
