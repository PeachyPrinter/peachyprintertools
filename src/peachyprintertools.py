#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import Tkinter
import tkMessageBox
from infrastructure.configuration import FileBasedConfigurationManager
from api.configuration_api import ConfigurationAPI
from ui.drip_calibration_ui import DripCalibrationUI
from ui.add_printer_ui import AddPrinterUI
from ui.configuration_ui import SetupAudioUI


class MainFrame(Tkinter.Frame):
    def __init__(self,parent, configuration_api):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self._configuration_api = configuration_api
        self.initialize()

    def initialize(self):
        
        self.grid()
        printer_selection_current = Tkinter.StringVar()
        
        if not self._configuration_api.get_available_printers():
            self._configuration_api.add_printer("Peachy Printer")
        available_printers = self._configuration_api.get_available_printers() 

        printer_selection_current.set(available_printers[0])
        self._printer_selected(available_printers[0])
        printer_selection_menu = Tkinter.OptionMenu(
            self,
            printer_selection_current, 
            *available_printers,
            command = self._printer_selected)
        printer_selection_menu.grid(column=1,row=0)

        add_printer_button = Tkinter.Button(self,text=u"Add Printer", command=self._add_printer)
        add_printer_button.grid(column=2,row=0)

        audio_setup_button = Tkinter.Button(self,text=u"Setup Audio", command=self.setup_audio_button_click)
        audio_setup_button.grid(column=1,row=1)

        drip_calibration_button = Tkinter.Button(self,text=u"Start Drip Calibration", command=self.drip_calibration_button_click)
        drip_calibration_button.grid(column=1,row=2)

        button = Tkinter.Button(self,text=u"Start Calibration", command=self.start_calibration_button_click)
        button.grid(column=1,row=3)

        self.grid_columnconfigure(1,weight=1)
        self.update()

    def _printer_selected(self, selection):
        self._configuration_api.load_printer(selection)

    def _add_printer(self):
        self.parent.start_add_printer()


    def drip_calibration_button_click(self):
        self.parent.start_drip_calibration()

    def setup_audio_button_click(self):
        self.parent.start_audio_setup()

    def start_calibration_button_click(self):
        tkMessageBox.showwarning(
            "Coming Soon",
            "Peachy Printer Calibration Coming Soon"
        )

    def close(self):
        pass


class PeachyPrinterTools(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.current_frame = None
        configuration_manager = FileBasedConfigurationManager()
        self._configuration_api = ConfigurationAPI(configuration_manager)

        self.start_main_window()

        self.protocol("WM_DELETE_WINDOW", self.close)

    def close_current(self):
        if self.current_frame:
            self.current_frame.close()
            self.current_frame.grid_forget()
            self.current_frame.destroy()
 
    def start_drip_calibration(self):
        self.close_current()
        self.current_frame = DripCalibrationUI(self)
        self.current_frame.pack()

    def start_add_printer(self):
        self.close_current()
        self.current_frame = AddPrinterUI(self, self._configuration_api)
        self.current_frame.pack()

    def start_audio_setup(self):
        self.close_current()
        self.current_frame = SetupAudioUI(self, self._configuration_api)
        self.current_frame.pack()

    def start_main_window(self):
        self.close_current()
        self.current_frame = MainFrame(self, self._configuration_api)
        self.current_frame.pack()

    def close(self):
        if self.current_frame.__class__.__name__ == "MainFrame":
            self.destroy()
            exit(0)
        else:
            self.start_main_window()

if __name__ == "__main__":
    app = PeachyPrinterTools(None)
    app.title('Peachy Printer Tools')
    app.mainloop()