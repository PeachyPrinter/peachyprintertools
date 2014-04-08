from Tkinter import *

class AddPrinterUI(Frame):
    def __init__(self,parent, configuration_api):
        Frame.__init__(self, parent)
        self.parent = parent
        self._configuration_api = configuration_api
        self.initialize()

    def initialize(self):
        self.grid()
        label_text = StringVar()
        label_text.set("Enter a name for your printer")
        label = Label(self, textvariable = label_text )
        label.grid(column=0,row=0)
        self.entry = Entry(self)
        self.entry.grid(column=1, row=0)
        button = Button(self, text ="Submit", command = self._process)
        button.grid(column=2,row=0)


        self.grid_columnconfigure(1,weight=1)
        self.update()

    def _process(self):
        printer_name = self.entry.get()
        self._configuration_api.add_printer(printer_name)
        self.parent.start_main_window()

    def close(self):
        pass