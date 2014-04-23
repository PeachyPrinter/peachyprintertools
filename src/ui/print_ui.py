from Tkinter import *
import tkMessageBox
import tkFileDialog
from ui.ui_tools import *
from ui.main_ui import MainUI
from api.print_api import PrintAPI
from api.configuration_api import ConfigurationAPI

class PrintUI(PeachyFrame):

    def initialize(self):
        self.grid()
        self.file_opt = options = {}
        options['defaultextension'] = '.gcode'
        options['filetypes'] = [('GCode files', '.gcode'),('all files', '.*'), ]
        options['initialdir'] = '.'
        options['parent'] = self
        options['title'] = 'Select file to print'

        self._configuration_api = ConfigurationAPI(self._configuration_manager)
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

        button = Button(self,text=u"Back", command=self._back)
        button.grid(column=0,row=5)

        self.grid_columnconfigure(1,weight=1)
        self.update()

    def _printer_selected(self, selection):
        self._configuration_api.load_printer(selection)

    def print_g_code_click(self):
        filename = tkFileDialog.askopenfile(**self.file_opt)
        self.navigate(PrintStatusUI, filename = filename, config = self._configuration_api.get_current_config())

    def _back(self):
        self.navigate(MainUI)

    def close(self):
        pass

class PrintStatusUI(PeachyFrame):

    def initialize(self):
        self.grid()
        self._update_status_job = None
        self._print_api = PrintAPI(self.kwargs['config'])
        file_to_print = self.kwargs['filename']
        self._print_api.print_gcode(file_to_print)
        self.status = self._print_api.get_status()

        self.elapsed_time = StringVar()
        self.current_layer = StringVar()
        self.current_height = StringVar()
        self.current_drips = StringVar()
        self.laser_state = StringVar()
        self.waiting_for_drips = StringVar()
        self.complete = StringVar()

        self._update_status()

        label = Label(self, text = "Elapsed Time" )
        label.grid(column=0,row=0)
        label = Label(self, textvariable = self.elapsed_time )
        label.grid(column=1,row=0)

        label = Label(self, text = "Layer" )
        label.grid(column=0,row=1)
        label = Label(self, textvariable = self.current_layer )
        label.grid(column=1,row=1)

        label = Label(self, text = "Height" )
        label.grid(column=0,row=2)
        label = Label(self, textvariable = self.current_height )
        label.grid(column=1,row=2)

        label = Label(self, text = "Drips" )
        label.grid(column=0,row=3)
        label = Label(self, textvariable = self.current_drips )
        label.grid(column=1,row=3)

        label = Label(self, text = "Laser" )
        label.grid(column=0,row=4)
        label = Label(self, textvariable = self.laser_state )
        label.grid(column=1,row=4)

        label = Label(self, text = "Waiting for drips" )
        label.grid(column=0,row=5)
        label = Label(self, textvariable = self.waiting_for_drips )
        label.grid(column=1,row=5)

        label = Label(self, textvariable = self.complete )
        label.grid(column=1,row=6)

        button = Button(self,text=u"Stop", command=self._stop_button_click)
        button.grid(column=2,row=7)

        self.grid_columnconfigure(1,weight=1)
        self.update()

    def _stop_button_click(self):
        self._print_api.stop()
        self.navigate(PrintUI)

    def _update_status(self):
        if not self.status.complete:
            if self._update_status_job:
                self.after_cancel(self._update_status_job)
                self._update_status_job = None
            self.elapsed_time.set(self.status.elapsed_time)
            self.current_layer.set(self.status.current_layer)
            self.current_height.set(self.status.z_posisition)
            self.current_drips.set(self.status.drips)
            self.laser_state.set("On" if self.status.laser_state else "Off")
            self.waiting_for_drips.set("Yes" if self.status.waiting_for_drips else "No")
            self._update_status_job=self.after(1000, self._update_status)
        else:
            self.complete.set("Done")

    def close(self):
        self._print_api.stop()