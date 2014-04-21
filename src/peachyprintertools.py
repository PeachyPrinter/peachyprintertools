#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import logging
import argparse
import os
from Tkinter import *
from infrastructure.configuration import FileBasedConfigurationManager
from api.configuration_api import ConfigurationAPI
from ui.main_ui import MainUI

class PeachyPrinterTools(Tk):
    def __init__(self,parent):
        Tk.__init__(self,parent)
        self.geometry("640x480")
        self.title('Peachy Printer Tools')
        img = PhotoImage(file=os.path.join(os.path.dirname(__file__),'resources','peachy.gif'))
        self.tk.call('wm', 'iconphoto', self._w, img)
        self.parent = parent
        configuration_manager = FileBasedConfigurationManager()
        self._configuration_manager = configuration_manager

        self.start_main_window()

        self.protocol("WM_DELETE_WINDOW", self.close)


    def start_main_window(self):
        MainUI(self, self._configuration_manager)


    def close(self):
        self.destroy()
        exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Configure and print with Peachy Printer")
    parser.add_argument("--log", dest='loglevel', action='store', required=False, default="WARNING", help="Enter the loglevel [DEBUG|INFO|WARNING|ERROR] default: WARNING" )
    args = parser.parse_args()
    numeric_level = getattr(logging, args.loglevel.upper(), "INFO")
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.loglevel)
    logging.basicConfig(format='%(levelname)s: %(asctime)s %(module)s - %(message)s', level=numeric_level)
    app = PeachyPrinterTools(None)
    app.title('Peachy Printer Tools')
    app.mainloop()