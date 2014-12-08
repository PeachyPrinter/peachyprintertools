#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import logging
import config
import argparse
import os
import sys
import time
from Tkinter import *
from infrastructure.configuration import FileBasedConfigurationManager
from api.configuration_api import ConfigurationAPI
from ui.main_ui import MainUI

class PeachyPrinterTools(Tk):
    def __init__(self,parent, path):
        Tk.__init__(self,parent)
        self.path = path
        self.geometry("800x700")
        self.title('Peachy Printer Tools')

        if sys.platform != 'darwin':
            self.setup_icon()
            
        self.parent = parent
        configuration_manager = FileBasedConfigurationManager()
        self._configuration_manager = configuration_manager

        self.start_main_window()

        self.protocol("WM_DELETE_WINDOW", self.close)

    def start_main_window(self):
        MainUI(self, self._configuration_manager)

    def setup_icon(self):
        img_file = os.path.join(self.path,'resources','peachy.gif')
        img = PhotoImage(file=img_file)
        self.tk.call('wm', 'iconphoto', self._w, img)

    def close(self):
        self.destroy()
        sys.exit(0)

def setup_logging(args):
    if args.devmode:
        timestr = time.strftime("%Y-%m-%d-%H:%M:%S")
        logfile = os.path.join(config.PEACHY_PATH,'peachyprinter-%s.log' % timestr )
    else:  
        logfile = os.path.join(config.PEACHY_PATH,'peachyprinter.log' )
    if os.path.isfile(logfile):
        os.remove(logfile)
    logging_format = '%(levelname)s: %(asctime)s %(module)s - %(message)s'
    logging_level = getattr(logging, args.loglevel.upper(), "WARNING")
    if not isinstance(logging_level, int):
        raise ValueError('Invalid log level: %s' % args.loglevel)
    if args.console:
        rootLogger = logging.getLogger()
        logFormatter = logging.Formatter(logging_format)
        fileHandler = logging.FileHandler(logfile)
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        rootLogger.addHandler(consoleHandler)
    else:
        logging.basicConfig(filename = logfile ,format=logging_format, level=logging_level)


if __name__ == "__main__":
    if not os.path.exists(config.PEACHY_PATH):
        os.makedirs(config.PEACHY_PATH)

    parser = argparse.ArgumentParser("Configure and print with Peachy Printer")
    parser.add_argument('-l', '--log',     dest='loglevel', action='store',      required=False, default="WARNING", help="Enter the loglevel [DEBUG|INFO|WARNING|ERROR] default: WARNING" )
    parser.add_argument('-c', '--console', dest='console',  action='store_true', required=False, help="Logs to console not file" )
    parser.add_argument('-d', '--development', dest='devmode',  action='store_true', required=False, help="Enable Developer Testing Mode" )
    args, unknown = parser.parse_known_args()

    setup_logging(args)
    if args.devmode:
        config.devmode = True

    if getattr(sys, 'frozen', False):
        path = os.path.dirname(sys.executable)
    else:
        path = os.path.dirname(os.path.realpath(__file__))
    app = PeachyPrinterTools(None, path)
    app.title('Peachy Printer Tools')
    app.mainloop()