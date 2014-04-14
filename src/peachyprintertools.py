#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import logging
import argparse
from Tkinter import *
from infrastructure.configuration import FileBasedConfigurationManager
from api.configuration_api import ConfigurationAPI
from ui.main_ui import MainUI

class PeachyPrinterTools(Tk):
    def __init__(self,parent):
        Tk.__init__(self,parent)
        self.geometry("500x250")
        self.parent = parent
        configuration_manager = FileBasedConfigurationManager()
        self._configuration_api = ConfigurationAPI(configuration_manager)

        self.start_main_window()

        self.protocol("WM_DELETE_WINDOW", self.close)


    def start_main_window(self):
        MainUI(self, self._configuration_api)


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
    logging.basicConfig(format='%(asctime)s %(message)s', level=numeric_level)
    app = PeachyPrinterTools(None)
    app.title('Peachy Printer Tools')
    app.mainloop()