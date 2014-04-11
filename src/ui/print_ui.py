from Tkinter import *
import tkMessageBox
import tkFileDialog
from ui.ui_tools import *
from ui.main_ui import MainUI
from api.print_api import PrintAPI

class PrintUI(PeachyFrame):

    def initialize(self):
        self.grid()
        self.file_opt = options = {}
        options['defaultextension'] = '.gcode'
        options['filetypes'] = [('GCode files', '.gcode'),('all files', '.*'), ]
        options['initialdir'] = '.'
        options['parent'] = self
        options['title'] = 'Select file to print'

        printer_selection_current = StringVar()
        if not self._configuration_api.get_available_printers():
            self._configuration_api.add_printer("Peachy Printer")
        available_printers = self._configuration_api.get_available_printers() 

        printer_selection_current.set(available_printers[0])
        self._printer_selected(available_printers[0])
        printer_selection_menu = OptionMenu(
            self,
            printer_selection_current, 
            *available_printers,
            command = self._printer_selected)
        printer_selection_menu.grid(column=1,row=0)


        audio_setup_button = Button(self,text=u"Print From G Code", command=self.print_g_code_click)
        audio_setup_button.grid(column=1,row=1)

        button = Button(self,text=u"Back", command=self._back_button_click)
        button.grid(column=3,row=5)

        self.grid_columnconfigure(1,weight=1)
        self.update()

    def _printer_selected(self, selection):
        self._configuration_api.load_printer(selection)

    def print_g_code_click(self):
        filename = tkFileDialog.askopenfile(**self.file_opt)
        self.navigate(PrintStatusUI, filename = filename)

    def _back_button_click(self):
        self.navigate(MainUI)

    def close(self):
        pass

class PrintStatusUI(PeachyFrame):

    def initialize(self):
        self.grid()
        self._update_status_job = None
        self._print_api = PrintAPI(self._configuration_api.get_current_config())
        file_to_print = self.kwargs['filename']
        self._print_api.print_gcode(file_to_print)
        self.status = self._print_api.get_status()

        self.elapsed_time = StringVar()
        self._update_status()

        label = Label(self, text = "Elapsed Time" )
        label.grid(column=0,row=0)
        label = Label(self, textvariable = self.elapsed_time )
        label.grid(column=2,row=0)


        button = Button(self,text=u"Stop", command=self._stop_button_click)
        button.grid(column=3,row=5)

        self.grid_columnconfigure(1,weight=1)
        self.update()

    def _stop_button_click(self):
        self._print_api.stop()
        self.navigate(PrintUI)

    def _update_status(self):
        if self._update_status_job:
            self.after_cancel(self._update_status_job)
            self._update_status_job = None
        self.elapsed_time.set(self.status.elapsed_time)

        self._update_status_job=self.after(1000, self._update_status)

    def close(self):
        pass