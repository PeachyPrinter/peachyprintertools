from Tkinter import *
import tkMessageBox
import tkFileDialog
from ui.ui_tools import *
from ui.main_ui import MainUI
from api.print_api import PrintAPI, PrintQueueAPI
from api.configuration_api import ConfigurationAPI

from config import devmode

class PrintUI(PeachyFrame):

    def initialize(self):
        self.grid()
        self.file_opt = {}
        self.file_opt['initialdir'] = '.'
        self.file_opt['parent'] = self
        self.file_opt['title'] = 'Select file to print'
        self.file_opt['filetypes'] = [('GCode files', '.gcode'),('all files', '.*'), ]
        self.file_opt['defaultextension'] = '.gcode'
        self.folder_opt = {}
        self.folder_opt['initialdir'] = '.'
        self.folder_opt['parent'] = self
        self.folder_opt['title'] = 'Select file to print'
        
        
        self._configuration_api = ConfigurationAPI(self._configuration_manager)
        self._printer_selection_current = StringVar()

        if not self._configuration_api.get_available_printers():
            self._configuration_api.add_printer("Peachy Printer")
        available_printers = self._configuration_api.get_available_printers() 

        if 'printer' in self.kwargs.keys():
            printer = self.kwargs['printer']
        else:
            printer = available_printers[0]
        self._printer_selection_current.set(printer)
        self._printer_selected(printer)

        OptionMenu(self, self._printer_selection_current, *available_printers, command = self._printer_selected).grid(column=1,row=10,sticky=N+S+E+W)
        Label(self).grid(column=1,row=20)
        Button(self,text=u"Verify G Code", command=self.verify_g_code_click).grid(column=1,row=25,sticky=N+S+E+W)
        Button(self,text=u"Print G Code", command=self.print_g_code_click).grid(column=1,row=30,sticky=N+S+E+W)
        if devmode:
            Button(self,text=u"Print GCode Queue", command=self.print_g_code_queue_click).grid(column=1,row=35,sticky=N+S+E+W)
        Label(self).grid(column=1,row=40)
        Button(self,text=u"Back", command=self._back).grid(column=0,row=50)

        self.update()

    def _printer_selected(self, selection):
        self._configuration_api.load_printer(selection)

    def print_g_code_click(self):
        filename = tkFileDialog.askopenfilename(**self.file_opt)
        if filename:
            self.navigate(PrintStatusUI, printer =self._printer_selection_current.get(), filename = filename, config = self._configuration_api.get_current_config(), calling_class = PrintUI)

    def print_g_code_queue_click(self):
        foldername = tkFileDialog.askdirectory(**self.folder_opt)
        if foldername:
            self.navigate(PrintStatusUI, printer =self._printer_selection_current.get(), foldername = foldername, config = self._configuration_api.get_current_config(), calling_class = PrintUI)


    def verify_g_code_click(self):
        filename = tkFileDialog.askopenfilename(**self.file_opt)
        if filename:
            self.navigate(VerifyStatusUI, printer =self._printer_selection_current.get(), filename = filename, config = self._configuration_api.get_current_config(), calling_class = PrintUI)

    def _back(self):
        self.navigate(MainUI)

    def close(self):
        pass

class VerifyStatusUI(PeachyFrame):

    def initialize(self):
        self.grid()
        
        self._elapsed_time = StringVar()
        self._current_layer = IntVar()
        self._current_height = StringVar()
        self._current_model_height = StringVar()
        self._errors = IntVar()
        self._status = StringVar()
        self._stop_button_text = StringVar()
        self._stop_button_text.set("Abort Verification")
        self._current_status = {}

        self._print_api = PrintAPI(self.kwargs['config'],status_call_back = self.status_call_back)
        if 'filename' in self.kwargs:
            file_name = self.kwargs['filename']
            self._print_api.verify_gcode(file_name)
        else:
            self._print_api.verify_gcode(self.kwargs['layer_generator'])


        Label(self, text = "Verifying G-Code" ).grid(column=0,row=5)
        Label(self ).grid(column=0,row=8)

        Label(self, text = "Elapsed Time" ).grid(column=0,row=10)
        Label(self, textvariable = self._elapsed_time ).grid(column=1,row=10)

        Label(self, text = "Layer" ).grid(column=0,row=20)
        Label(self, textvariable = self._current_layer ).grid(column=1,row=20)

        Label(self, text = "Model Height (mm)" ).grid(column=0,row=35)
        Label(self, textvariable = self._current_model_height ).grid(column=1,row=35)

        Label(self, text = "Status").grid(column=0,row=60)
        Label(self, textvariable = self._status).grid(column=1,row=60)

        Label(self, text = "Errors" ).grid(column=0,row=70)
        Label(self, textvariable = self._errors ).grid(column=1,row=70)

        Label(self).grid(column=0,row=75)
        
        Button(self,textvariable=self._stop_button_text, command=self._stop_button_click).grid(column=2,row=80)
        Button(self,text="Show Errors", command=self._show_errors).grid(column=3,row=80)
        
        self.update()

    def _stop_button_click(self):
        self._print_api.close()
        self.navigate(self.kwargs['calling_class'], printer = self.kwargs['printer'])

    def _show_errors(self):
        PopUp(self,'Errors', '\n'.join([ "SubLayer %s : %s" % (err['layer'], err['message']) for err in self._current_status['errors'] ]))

    def status_call_back(self,status):
        total_seconds = int(status['elapsed_time'].total_seconds())
        hours, remainder = divmod(total_seconds,60*60)
        minutes, seconds = divmod(remainder,60)

        self._elapsed_time.set("%02d:%02d:%02d" % (hours,minutes,seconds))
        self._current_layer.set(status['current_layer'])
        self._current_model_height.set("%.2f" % status['model_height'])
        self._errors.set(len(status['errors']))
        self._current_status = status
        self._status.set(status['status'])
        if (status['status'] == "Complete"):
            self._stop_button_text.set("Finished")

    def close(self):
        self._print_api.close()

class PrintStatusUI(PeachyFrame):

    def initialize(self):
        self.grid()
        self._print_api = None
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
        self._drips_per_second_setting = DoubleVar()

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

        self.options_frame = LabelFrame(self, text="In Print Options", padx=5, pady=5)
        self.options_frame.grid(column=12,row=10,rowspan = 60,sticky=N+S+E+W)
        self.options_frame.grid_remove()

        Label(self.options_frame, text = 'Drips Per Second').grid(column=0,row=10)
        RylanSpinbox(self.options_frame, from_=0.0, to=100.0, increment= 0.1, command = self._dps_changed, textvariable = self._drips_per_second_setting).grid(column=1,row=10)

        Label(self).grid(column=0,row=70)
        
        Button(self,text='Restart', command=self._restart_printing).grid(column=1,row=80)
        Button(self,textvariable=self._stop_button_text, command=self._stop_button_click).grid(column=2,row=80)

        self._start_printing()
        
        self.update()

    def _start_printing(self):
        self._stop_button_text.set("Abort Print")
        
        if 'filename' in self.kwargs:
            self._print_api = PrintAPI(self.kwargs['config'],status_call_back = self.status_call_back)
            file_name = self.kwargs['filename']
            self._print_api.print_gcode(file_name)
            if self._print_api.can_set_drips_per_second():
                self.options_frame.grid()
                self._drips_per_second_setting.set(self._print_api.get_drips_per_second())
        elif 'foldername' in self.kwargs:
            self._print_api = PrintQueueAPI(self.kwargs['config'],status_call_back = self.status_call_back)
            foldername = self.kwargs['foldername']
            self._print_api.print_folder(foldername)
        else:
            self._print_api = PrintAPI(self.kwargs['config'],status_call_back = self.status_call_back)
            self._print_api.print_layers(self.kwargs['layer_generator'])

        

    def _stop_button_click(self):
        self._print_api.close()
        self.navigate(self.kwargs['calling_class'], printer = self.kwargs['printer'])

    def _restart_printing(self):
        self._print_api.close()
        self._start_printing()

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

    def _dps_changed(self):
        self._print_api.set_drips_per_second(self._drips_per_second_setting.get())

    def close(self):
        if self._print_api:
            self._print_api.close()
