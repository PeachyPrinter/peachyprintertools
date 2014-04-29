from Tkinter import *
import tkMessageBox
from ui_tools import *
import sys

class MainUI(PeachyFrame):

    def initialize(self):
        self.grid()
        
        Button(self,text=u"Setup Printers", command=self._setup_printers).grid(column=1,row=10,sticky=NSEW)
        Button(self,text=u"Print", command=self._print).grid(column=1,row=20,sticky=NSEW)
        Label(self).grid(column=1,row=30)
        Button(self,text=u"Quit", command=self._quit).grid(column=0,row=40)
        self.update()

    def _setup_printers(self):
        from ui.configuration_ui import SetupUI
        self.navigate(SetupUI)

    def _print(self):
        from ui.print_ui import PrintUI
        self.navigate(PrintUI)

    def _quit(self):
        sys.exit(0)