#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import Tkinter
import tkMessageBox
from ui.drip_calibration_ui import DripCalibrationUI

class MainFrame(Tkinter.Frame):
    def __init__(self,parent):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        
        self.grid()

        audio_setup_button = Tkinter.Button(self,text=u"Setup Audio", command=self.drip_calibration_button_click)
        audio_setup_button.grid(column=1,row=0)

        drip_calibration_button = Tkinter.Button(self,text=u"Start Drip Calibration", command=self.drip_calibration_button_click)
        drip_calibration_button.grid(column=1,row=1)

        button = Tkinter.Button(self,text=u"Start Calibration", command=self.start_calibration_button_click)
        button.grid(column=1,row=2)

        self.grid_columnconfigure(1,weight=1)
        self.update()

    def drip_calibration_button_click(self):
        self.parent.start_drip_calibration()

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

    def start_main_window(self):
        self.close_current()
        self.current_frame = MainFrame(self)
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