#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import Tkinter

class MainFrame(Tkinter.Frame):
    def __init__(self,parent):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.grid()

        button = Tkinter.Button(self,text=u"Start Drip Calibration", command=self.OnButtonClick)
        button.grid(column=1,row=0)

        self.labelVariable = Tkinter.StringVar()
        label = Tkinter.Label(self,textvariable=self.labelVariable, anchor="w",fg="white",bg="blue")
        label.grid(column=0,row=1,columnspan=2,sticky='EW')
        self.labelVariable.set(u"ONE")

        self.grid_columnconfigure(0,weight=1)
        self.update()

    def OnButtonClick(self):
        self.parent.start_drip_calibration()

class DripCalibration(Tkinter.Frame):
    def __init__(self,parent):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.grid()

        button = Tkinter.Button(self,text=u"Quit", command=self.OnButtonClick)
        button.grid(column=1,row=0)

        self.labelVariable = Tkinter.StringVar()
        label = Tkinter.Label(self,textvariable=self.labelVariable, anchor="w",fg="white",bg="blue")
        label.grid(column=0,row=1,columnspan=2,sticky='EW')
        self.labelVariable.set(u"TWO !")
        
        self.grid_columnconfigure(0,weight=1)
        self.update()

    def OnButtonClick(self):
        self.parent.start_main_window()


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
        self.main_frame = DripCalibration(self)
        self.main_frame.pack()

    def start_main_window(self):
        self.close_current()
        self.main_frame = MainFrame(self)
        self.main_frame.pack()


if __name__ == "__main__":
    app = PeachyPrinterTools(None)
    app.title('Peachy Printer Tools')
    app.mainloop()