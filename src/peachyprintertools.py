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

        drip_calibration_button = Tkinter.Button(self,text=u"Start Drip Calibration", command=self.drip_calibration_button_click)
        drip_calibration_button.grid(column=1,row=0)

        button = Tkinter.Button(self,text=u"Start Calibration", command=self.start_calibration_button_click)
        button.grid(column=1,row=1)

        self.grid_columnconfigure(1,weight=1)
        self.update()

    def drip_calibration_button_click(self):
        self.parent.start_drip_calibration()

    def start_calibration_button_click(self):
        tkMessageBox.showwarning(
            "Coming Soon",
            "Peachy Printer Calibration Coming Soon"
        )


class PeachyPrinterTools(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.main_frame = None
        self.start_main_window()

    def close_current(self):
        if self.main_frame:
            self.main_frame.grid_forget()
            self.main_frame.destroy()
 
    def start_drip_calibration(self):
        self.close_current()
        self.main_frame = DripCalibrationUI(self)
        self.main_frame.pack()

    def start_main_window(self):
        self.close_current()
        self.main_frame = MainFrame(self)
        self.main_frame.pack()


if __name__ == "__main__":
    app = PeachyPrinterTools(None)
    app.title('Peachy Printer Tools')
    app.mainloop()