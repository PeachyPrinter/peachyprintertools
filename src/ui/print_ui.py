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
        self._printer_selection_current = StringVar()
        if not self._configuration_api.get_available_printers():
            self._configuration_api.add_printer("Peachy Printer")
        available_printers = self._configuration_api.get_available_printers() 

        self._printer_selection_current.set(available_printers[0])
        self._printer_selected(available_printers[0])

        OptionMenu(self, self._printer_selection_current, *available_printers, command = self._printer_selected).grid(column=1,row=10,sticky=N+S+E+W)
        Label(self).grid(column=1,row=20)
        Button(self,text=u"Print From G Code", command=self.print_g_code_click).grid(column=1,row=30,sticky=N+S+E+W)
        Label(self).grid(column=1,row=40)
        Button(self,text=u"Back", command=self._back).grid(column=0,row=50)

        self.update()

    def _printer_selected(self, selection):
        self._configuration_api.load_printer(selection)

    def print_g_code_click(self):
        filename = tkFileDialog.askopenfile(**self.file_opt)
        self.navigate(PrintStatusUI, printer =self._printer_selection_current.get(), filename = filename, config = self._configuration_api.get_current_config(), calling_class = PrintUI)

    def _back(self):
        self.navigate(MainUI)

    def close(self):
        pass

class PrintStatusUI(PeachyFrame):

    def initialize(self):
        self.grid()
        
        self._elapsed_time = StringVar()
        self._current_layer = IntVar()
        self._current_height = StringVar()
        self._current_model_height = StringVar()
        self._current_drips = IntVar()
        self._waiting_for_drips = StringVar()
        self._skipped_layers = IntVar()
        self._status = StringVar()
        self._stop_button_text = StringVar()
        self._stop_button_text.set("Abort Print")

        self._print_api = PrintAPI(self.kwargs['config'],status_call_back = self.status_call_back)
        if 'filename' in self.kwargs:
            file_to_print = self.kwargs['filename']
            self._print_api.print_gcode(file_to_print)
        else:
            self._print_api.print_layers(self.kwargs['layer_generator'])


        Label(self, text = "Elapsed Time" ).grid(column=0,row=10)
        Label(self, textvariable = self._elapsed_time ).grid(column=1,row=10)

        Label(self, text = "Layer" ).grid(column=0,row=20)
        Label(self, textvariable = self._current_layer ).grid(column=1,row=20)

        Label(self, text = "Actual Height (mm)" ).grid(column=0,row=30)
        Label(self, textvariable = self._current_height ).grid(column=1,row=30)

        Label(self, text = "Model Height (mm)" ).grid(column=0,row=35)
        Label(self, textvariable = self._current_model_height ).grid(column=1,row=35)

        Label(self, text = "Drips" ).grid(column=0,row=40)
        Label(self, textvariable = self._current_drips ).grid(column=1,row=40)

        Label(self, text = "Waiting for drips" ).grid(column=0,row=50)
        Label(self, textvariable = self._waiting_for_drips ).grid(column=1,row=50)

        Label(self, text = "Skipped Layers" ).grid(column=0,row=55)
        Label(self, textvariable = self._skipped_layers ).grid(column=1,row=55)

        Label(self, text = "Status").grid(column=0,row=60)
        Label(self, textvariable = self._status).grid(column=1,row=60)

        Label(self).grid(column=0,row=70)
        
        Button(self,textvariable=self._stop_button_text, command=self._stop_button_click).grid(column=2,row=80)
        
        self.update()

    def _stop_button_click(self):
        self._print_api.stop()
        self.navigate(self.kwargs['calling_class'], printer = self.kwargs['printer'])

    def status_call_back(self,status):
        total_seconds = int(status['elapsed_time'].total_seconds())
        hours, remainder = divmod(total_seconds,60*60)
        minutes, seconds = divmod(remainder,60)

        self._elapsed_time.set("%02d:%02d:%02d" % (hours,minutes,seconds))
        self._current_layer.set(status['current_layer'])
        self._current_height.set("%.2f" % status['height'])
        self._current_model_height.set("%.2f" % status['model_height'])
        self._current_drips.set(status['drips'])
        self._waiting_for_drips.set("Yes" if status['waiting_for_drips'] else "No")
        self._skipped_layers.set(status['skipped_layers'])
        self._status.set(status['status'])
        if (status['status'] == "Complete"):
            self._stop_button_text.set("Finished")

    def close(self):
        self._print_api.stop()