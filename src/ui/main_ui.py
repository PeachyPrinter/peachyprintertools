from Tkinter import *
import tkMessageBox
from ui_tools import *

class MainUI(PeachyFrame):

    def initialize(self):
        self.grid()
        
        Button(self,text=u"Setup Printers", command=self._setup_printers).grid(column=1,row=0,sticky=NSEW)
        Button(self,text=u"Print", command=self._print).grid(column=1,row=1,sticky=NSEW)
        self.update()

    def _setup_printers(self):
        from ui.configuration_ui import SetupUI
        self.navigate(SetupUI)

    def _print(self):
        from ui.print_ui import PrintUI
        self.navigate(PrintUI)
        # self.navigate(PrintUI)