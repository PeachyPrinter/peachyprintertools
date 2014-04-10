from Tkinter import *
import tkMessageBox
from ui_tools import *

class MainUI(PeachyFrame):

    def initialize(self):
        self.grid()
        
        add_printer_button = Button(self,text=u"Setup Printers", command=self._setup_printers)
        add_printer_button.grid(column=1,row=0)

        audio_setup_button = Button(self,text=u"Print", command=self._print)
        audio_setup_button.grid(column=1,row=1)

        self.grid_columnconfigure(1,weight=1)
        self.update()

    def _setup_printers(self):
        from ui.configuration_ui import SetupUI
        self.navigate(SetupUI)

    def _print(self):
        tkMessageBox.showwarning(
            "Coming Soon",
            "Peachy Printer Printing Coming Soon"
        )
        # self.navigate(PrintUI)