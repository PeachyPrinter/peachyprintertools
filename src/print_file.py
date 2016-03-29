#!/bin/python

import logging
import os
import sys
import time
import argparse

from peachyprinter import PrinterAPI

running = False

def setup_logging(args):
    peachy_logger = logging.getLogger('peachy')
    logfile = os.path.join(args.log_path, 'peachyprinter.log')
    print ("Using logfile: {}".format(logfile))
    try:
        if os.path.isfile(logfile):
            os.remove(logfile)
    except:
        print("Log file: {} appears to be in use by another process, attempting to continue logs may be bad.".format(logfile))

    logging_format = '%(levelname)s: %(asctime)s %(module)s - %(message)s'
    logging_level = getattr(logging, args.loglevel.upper(), "INFO")
    if not isinstance(logging_level, int):
        raise ValueError('Invalid log level: %s' % args.loglevel)
    if True:
        peachy_logger = logging.getLogger('peachy')
        peachy_logger.propagate = False
        logFormatter = logging.Formatter(logging_format)

        fileHandler = logging.FileHandler(logfile)
        consoleHandler = logging.StreamHandler()

        fileHandler.setFormatter(logFormatter)
        consoleHandler.setFormatter(logFormatter)

        peachy_logger.addHandler(fileHandler)
        if args.console:
            peachy_logger.addHandler(consoleHandler)

        peachy_logger.setLevel(logging_level)


def setup_env(path):
    python_64 = sys.maxsize > 2**32
    if getattr(sys, 'frozen', False):
        if os.name == 'nt':
            dll_base = os.path.join(path, 'win')
        elif sys.platform == 'darwin':
            dll_base = os.path.join(path, 'mac')
        elif sys.platform == 'linux2':
            dll_base = os.path.join(path, 'linux')
        if python_64:
            os.environ['PEACHY_API_DLL_PATH'] = os.path.join(dll_base, "AMD64")
        else:
            os.environ['PEACHY_API_DLL_PATH'] = os.path.join(dll_base, "x86")


status_calls = 0
logger = None

def print_status(status):
    global status_calls
    if not status_calls % 10:
        print "| Layer |  Status  |Waiting| Height | Drips |Drips/Sec|Skipped|"

    status_calls += 1


    status['waiting_for_drips'] = "True" if status['waiting_for_drips'] else "False"
    line = '|{current_layer: >7}|{status: <10}|{waiting_for_drips: <7}|{height: 8.4f}|{drips: >7}|{drips_per_second: 9.4f}|{skipped_layers: >7}|'
    try:
        print(line.format(**status))
    except Exception as ex:
        print(ex)

def print_file(a_file):
    api = PrinterAPI()
    api.load_printer()

    print_api = api.get_print_api()
    running = True
    print_api.print_gcode(a_file)

    while running:
        status = print_api.get_status()
        if status['status'] in ['Complete', 'Cancelled', 'Failed']:
            running = False
        time.sleep(0.05)
        print_status(status)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Configure and print with Peachy Printer")
    parser.add_argument('-l', '--log',      dest='loglevel', action='store',      required=False, default="WARNING",  help="Enter the loglevel [DEBUG|INFO|WARNING|ERROR] default: WARNING")
    parser.add_argument('-t', '--console',  dest='console',  action='store_true', required=False,                     help="Logs to console not file")
    parser.add_argument('-p', '--log_path', dest='log_path', action='store',      required=False,  default=None,       help="Set the path for the log files")
    parser.add_argument('-f', '--file',     dest='file',     action='store',      required=True,  default=None,       help='Specify a file to print')
    args, unknown = parser.parse_known_args()

    path = os.path.dirname(os.path.realpath(__file__))
    setup_env(path)

    if not args.log_path:
        args.log_path = os.path.join(os.path.expanduser('~'), '.peachyprintertools',)
    if not os.path.exists(args.log_path):
        os.makedirs(args.log_path)
    setup_logging(args)

    print_file(args.file)
