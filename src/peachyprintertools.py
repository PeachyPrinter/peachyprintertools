#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import logging
import argparse
import os
import sys
from Tkinter import *
from infrastructure.configuration import FileBasedConfigurationManager
from api.configuration_api import ConfigurationAPI
from ui.main_ui import MainUI

class PeachyPrinterTools(Tk):
    def __init__(self,parent):
        Tk.__init__(self,parent)
        self.geometry("800x600")
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
        working_dir = os.path.dirname(os.path.realpath(sys.modules[self.__class__.__module__].__file__))
        img_file = os.path.join(working_dir,'resources','peachy.gif')
        img = PhotoImage(file=img_file)
        self.tk.call('wm', 'iconphoto', self._w, img)

    def close(self):
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    PEACHY_PATH = '.peachyprintertools'
    logfile = os.path.join(os.path.expanduser('~'), PEACHY_PATH,'peachyprinter.log' )
    parser = argparse.ArgumentParser("Configure and print with Peachy Printer")
    parser.add_argument('-l', '--log',     dest='loglevel', action='store',      required=False, default="WARNING", help="Enter the loglevel [DEBUG|INFO|WARNING|ERROR] default: WARNING" )
    parser.add_argument('-c', '--console', dest='console',  action='store_true', required=False, help="Logs to console not file" )
    args, unknown = parser.parse_known_args()

    logging_format = '%(levelname)s: %(asctime)s %(module)s - %(message)s'
    logging_level = getattr(logging, args.loglevel.upper(), "WARNING")
    if not isinstance(logging_level, int):
        raise ValueError('Invalid log level: %s' % args.loglevel)
    if args.console:
        logging.basicConfig(stream = sys.stdout,format=logging_format, level=logging_level)
    else:
        logging.basicConfig(filename = logfile ,format=logging_format, level=logging_level)

    app = PeachyPrinterTools(None)
    app.title('Peachy Printer Tools')
    app.mainloop()