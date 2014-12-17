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

        Label(self, text = "Layer / Sublayer" ).grid(column=0,row=20)
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
        self._raw_status = None
        self.grid()
        self._print_api = None
        self._elapsed_time = StringVar()
        self._current_layer = IntVar()
        self._current_height = StringVar()
        self._current_model_height = StringVar()
        self._current_drips = IntVar()
        self._current_drips_per_second = DoubleVar()
        self._waiting_for_drips = StringVar()
        self._skipped_layers = IntVar()
        self._status = StringVar()
        self._stop_button_text = StringVar()
        self._stop_button_text.set("Abort Print")
        self._drips_per_second_setting = DoubleVar()
        self._canvas_height = 20
        self._canvas_width  = 600
        self._drip_circle_radius = (self._canvas_height - 4) / 2

        self.canvas = Canvas(self,height = self._canvas_height, width = self._canvas_width, bg = 'black')
        self.canvas.grid(column = 0 ,row = 51,columnspan = 4)
        self.canvas.grid_remove()

        Label(self, text = "Elapsed Time" ).grid(column=0,row=10)
        Label(self, textvariable = self._elapsed_time ).grid(column=1,row=10)

        Label(self, text = "Layer / Sublayer" ).grid(column=0,row=20)
        Label(self, textvariable = self._current_layer ).grid(column=1,row=20)

        Label(self, text = "Actual Height (mm)" ).grid(column=0,row=30)
        Label(self, textvariable = self._current_height ).grid(column=1,row=30)

        Label(self, text = "Model Height (mm)" ).grid(column=0,row=35)
        Label(self, textvariable = self._current_model_height ).grid(column=1,row=35)

        Label(self, text = "Drips" ).grid(column=0,row=40)
        Label(self, textvariable = self._current_drips ).grid(column=1,row=40)

        Label(self, text = "Drips Per Second" ).grid(column=0,row=45)
        Label(self, textvariable = self._current_drips_per_second).grid(column=1,row=45)

        Label(self, text = "Waiting for drips" ).grid(column=0,row=50)
        Label(self, textvariable = self._waiting_for_drips ).grid(column=1,row=50)

        Label(self, text = "Skipped Layers / Sublayers" ).grid(column=0,row=55)
        Label(self, textvariable = self._skipped_layers ).grid(column=1,row=55)

        Label(self, text = "Status").grid(column=0,row=60)
        Label(self, textvariable = self._status).grid(column=1,row=60)

        self.options_frame = LabelFrame(self, text="In Print Options", padx=5, pady=5)
        self.options_frame.grid(column=4,row=0,rowspan = 60,sticky=N+S+E+W)
        self.options_frame.grid_remove()

        Label(self.options_frame, text = 'Drips Per Second').grid(column=0,row=10)
        RylanSpinbox(self.options_frame, from_=0.0, to=100.0, increment= 0.1, command = self._dps_changed, textvariable = self._drips_per_second_setting).grid(column=1,row=10)

        Label(self).grid(column=0,row=64)

        self.settings_frame = LabelFrame(self, text="Current Settings", padx=5, pady=5)
        self.settings_frame.grid(column=0,row=65,columnspan = 13,sticky=N+S+E+W)
        CONFIG_OPTION = "NOTHING"
        self.setting_sublayers = StringVar()
        Label(self.settings_frame, text = "Sublayers (mm): ").grid(column=0,row=10, sticky=E)
        Label(self.settings_frame, textvariable = self.setting_sublayers ).grid(column=1,row=10,sticky=W, padx=10)
        self.setting_overlap = StringVar()
        Label(self.settings_frame, text = "Overlap (mm): ").grid(column=0,row=20, sticky=E)
        Label(self.settings_frame, textvariable = self.setting_overlap ).grid(column=1,row=20,sticky=W, padx=10)
        self.setting_shuffled = StringVar()
        Label(self.settings_frame, text = "Spiral Starting Points: ").grid(column=0,row=30, sticky=E)
        Label(self.settings_frame, textvariable = self.setting_shuffled ).grid(column=1,row=30,sticky=W, padx=10)
        self.setting_lead_distance = StringVar()
        Label(self.settings_frame, text = "Maximum Lead Distance (mm): ").grid(column=0,row=40, sticky=E)
        Label(self.settings_frame, textvariable = self.setting_lead_distance ).grid(column=1,row=40,sticky=W, padx=10)
        self.setting_wait_after_move = StringVar()
        Label(self.settings_frame, text = "Wait After Move (ms): ").grid(column=0,row=50, sticky=E)
        Label(self.settings_frame, textvariable = self.setting_wait_after_move ).grid(column=1,row=50,sticky=W, padx=10)
        self.setting_scale = StringVar()
        Label(self.settings_frame, text = "Scale: ").grid(column=0,row=60, sticky=E)
        Label(self.settings_frame, textvariable = self.setting_scale).grid(column=1,row=60,sticky=W, padx=10)
        self.setting_spot_size = StringVar()
        Label(self.settings_frame, text = "Laser Spot Diameter: ").grid(column=0,row=70, sticky=E)
        Label(self.settings_frame, textvariable = self.setting_spot_size ).grid(column=1,row=70,sticky=W, padx=10)
        self.setting_speed = StringVar()
        Label(self.settings_frame, text = "Speed (mm/s): ").grid(column=0,row=80, sticky=E)
        Label(self.settings_frame, textvariable = self.setting_speed ).grid(column=1,row=80,sticky=W, padx=10)
       
        self.setting_audio_depth = StringVar()
        Label(self.settings_frame, text = "Audio Depth: ").grid(column=3,row=10, sticky=E)
        Label(self.settings_frame, textvariable = self.setting_audio_depth ).grid(column=4,row=10,sticky=W, padx=10)
        self.setting_audio_hz = StringVar()
        Label(self.settings_frame, text = "Audio Frequency: ").grid(column=3,row=20, sticky=E)
        Label(self.settings_frame, textvariable = self.setting_audio_hz ).grid(column=4,row=20,sticky=W, padx=10)
        self.setting_mod_on = StringVar()
        Label(self.settings_frame, text = "Modulation on: ").grid(column=3,row=30, sticky=E)
        Label(self.settings_frame, textvariable = self.setting_mod_on ).grid(column=4,row=30,sticky=W, padx=10)
        self.setting_mod_off = StringVar()
        Label(self.settings_frame, text = "Modulation off: ").grid(column=3,row=40, sticky=E)
        Label(self.settings_frame, textvariable = self.setting_mod_off ).grid(column=4,row=40,sticky=W, padx=10)
        self.setting_dripmm = StringVar()
        Label(self.settings_frame, text = "Drips per mm: ").grid(column=3,row=50, sticky=E)
        Label(self.settings_frame, textvariable = self.setting_dripmm ).grid(column=4,row=50,sticky=W, padx=10)


        Label(self).grid(column=0,row=70)
        
        Button(self,text='Restart', command=self._restart_printing).grid(column=1,row=80)
        Button(self,textvariable=self._stop_button_text, command=self._stop_button_click).grid(column=2,row=80)

        self._start_printing()
        self.after(125,self.update_display)
        self.update()

    def _load_config_data(self):
        if self._print_api.configuration.options.use_sublayers:
            self.setting_sublayers.set(self._print_api.configuration.options.sublayer_height_mm)
        else:
            self.setting_sublayers.set("Disabled")
        if self._print_api.configuration.options.use_overlap:
            self.setting_overlap.set(self._print_api.configuration.options.overlap_amount)
        else:
            self.setting_overlap.set("Disabled")
        if self._print_api.configuration.options.use_shufflelayers:
            self.setting_shuffled.set("Enabled")
        else:
            self.setting_shuffled.set("Disabled")
        self.setting_lead_distance.set(self._print_api.configuration.dripper.max_lead_distance_mm)
        self.setting_wait_after_move.set(self._print_api.configuration.options.wait_after_move_milliseconds)
        self.setting_scale.set(self._print_api.configuration.options.scaling_factor)
        self.setting_spot_size.set(self._print_api.configuration.options.laser_thickness_mm)
        self.setting_speed.set(self._print_api.configuration.cure_rate.draw_speed)

        self.setting_audio_depth.set(self._print_api.configuration.audio.output.bit_depth)
        self.setting_audio_hz.set(self._print_api.configuration.audio.output.sample_rate)
        self.setting_mod_on.set(self._print_api.configuration.audio.output.modulation_on_frequency)
        self.setting_mod_off.set(self._print_api.configuration.audio.output.modulation_off_frequency)
        self.setting_dripmm.set(self._print_api.configuration.dripper.drips_per_mm)


    def _start_printing(self):
        self._stop_button_text.set("Abort Print")
        
        if 'filename' in self.kwargs:
            self._print_api = PrintAPI(self.kwargs['config'],status_call_back = self.status_call_back)
            self._load_config_data()
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

    def update_display(self):
        if self._raw_status:
            total_seconds = int(self._raw_status['elapsed_time'].total_seconds())
            hours, remainder = divmod(total_seconds,60*60)
            minutes, seconds = divmod(remainder,60)

            self._elapsed_time.set("%02d:%02d:%02d" % (hours,minutes,seconds))
            self._current_layer.set(self._raw_status['current_layer'])
            self._current_height.set("%.2f" % self._raw_status['height'])
            self._current_model_height.set("%.2f" % self._raw_status['model_height'])
            self._current_drips.set(self._raw_status['drips'])
            self._current_drips_per_second.set("%.2f" % self._raw_status['drips_per_second'])
            self._waiting_for_drips.set("Yes" if self._raw_status['waiting_for_drips'] else "No")
            self._skipped_layers.set(self._raw_status['skipped_layers'])
            self._status.set(self._raw_status['status'])
            if (self._raw_status['status'] == "Complete"):
                self._stop_button_text.set("Finished")
            if len(self._raw_status['drip_history']) > 2:
                self.canvas.grid()
                self.update_canvas()
        self.after(125,self.update_display)

    def update_canvas(self):
        self.canvas.delete('all')
        for value in self.map_values(
                        self._raw_status['drip_history'][0],
                        self._raw_status['drip_history'][-1],
                        self._drip_circle_radius + 1,
                        self._canvas_width - self._drip_circle_radius -1,
                        self._raw_status['drip_history']):
            self.canvas.create_line(value, 1, value , self._canvas_height - 1, fill="red", width=0)

    def map_values(self,old_lo,old_hi,new_lo,new_high,values):
        old_range = (old_hi - old_lo)  
        new_range = (new_high - new_lo)  
        return[ (((value - old_lo) * new_range) / old_range) + new_lo for value in values ]




    def status_call_back(self,status):
        self._raw_status = status

    def _dps_changed(self):
        self._print_api.set_drips_per_second(self._drips_per_second_setting.get())

    def close(self):
        if self._print_api:
            self._print_api.close()
