from Tkinter import *
import tkMessageBox
from ui.ui_tools import *
from ui.main_ui import MainUI
from ui.calibration_ui import *
from api.configuration_api import ConfigurationAPI
from print_ui import PrintStatusUI
import help_text

from config import devmode

class SetupUI(PeachyFrame):

    def initialize(self):
        self._configuration_api = ConfigurationAPI(self._configuration_manager)
        self.grid()
        printer_selection_current = StringVar()
        
        if not self._configuration_api.get_available_printers():
            self._configuration_api.add_printer("Peachy Printer")
        available_printers = self._configuration_api.get_available_printers() 

        if 'printer' in self.kwargs.keys():
            printer = self.kwargs['printer']
        else:
            printer = available_printers[0]
        printer_selection_current.set(printer)
        self._printer_selected(printer)
        printer_selection_menu = OptionMenu(
            self,
            printer_selection_current, 
            *available_printers,
            command = self._printer_selected)
        printer_selection_menu.grid(column=1,row=10,sticky=NSEW)

        Button(self,text=u"Add Printer", command=self._add_printer).grid(column=2,row=10,sticky=NSEW)
        Label(self).grid(column=0,row=15)
        Button(self,text=u"Setup Audio", command=self._setup_audio).grid(column=1,row=20,sticky=NSEW)
        Button(self,text=u"Setup Options", command=self._setup_options).grid(column=1,row=30,sticky=NSEW)
        Button(self,text=u"Setup Drip Calibration", command=self._drip_calibration).grid(column=1,row=40,sticky=NSEW)
        Button(self,text=u"Setup Calibration", command=self._calibration).grid(column=1,row=50,sticky=NSEW)
        Button(self,text=u"Run Cure Test", command=self._cure_test).grid(column=1,row=60,sticky=NSEW)
        Label(self).grid(column=0,row=70)
        Button(self,text=u"Back", command=self._back).grid(column=0,row=100)

        self.grid_columnconfigure(1,weight=1)
        self.update()

    def _printer_selected(self, selection):
        self._configuration_api.load_printer(selection)
        self._current_printer = selection

    def _add_printer(self):
        self.navigate(AddPrinterUI)

    def _setup_options(self):
        self.navigate(SetupOptionsUI, printer = self._current_printer)

    def _drip_calibration(self):
        self.navigate(DripCalibrationUI, printer = self._current_printer)

    def _back(self):
        self.navigate(MainUI, printer = self._current_printer)

    def _setup_audio(self):
        self.navigate(SetupAudioUI, printer = self._current_printer)

    def _calibration(self):
        self.navigate(CalibrationUI, printer = self._current_printer)

    def _cure_test(self):
        self.navigate(CureTestUI, printer = self._current_printer)

    def close(self):
        pass

class AddPrinterUI(PeachyFrame):
    def initialize(self):
        self.grid()
        self._configuration_api = ConfigurationAPI(self._configuration_manager)
        
        self._printer_name = StringVar()

        Label(self, text = "Enter a name for your printer" ).grid(column=0,row=10)
        Entry(self, textvariable = self._printer_name).grid(column=1, row=10)

        Label(self).grid(column=1,row=20)

        Button(self, text ="Save", command = self._save).grid(column=1,row=30, sticky=N+S+E)

        self.update()

    def _save(self):
        printer_name = self._printer_name.get()
        self._configuration_api.add_printer(printer_name)
        self.navigate(SetupUI, printer = printer_name)

    def close(self):
        pass

class SetupOptionsUI(PeachyFrame):
    def initialize(self):
        self.grid()
        self._current_printer = self.kwargs['printer']
        self._configuration_api = ConfigurationAPI(self._configuration_manager)
        self._configuration_api.load_printer(self._current_printer)
        self.option_add('*Dialog.msg.width', 50)

        self.laser_thickness_entry_text = DoubleVar()
        self.laser_thickness_entry_text.set(self._configuration_api.get_laser_thickness_mm())
        self.max_lead_distance_entry_text = DoubleVar()
        self.max_lead_distance_entry_text.set(self._configuration_api.get_max_lead_distance_mm())
        self.scaling_factor_entry_text = DoubleVar()
        self.scaling_factor_entry_text.set(self._configuration_api.get_scaling_factor())

        self._use_sublayers = IntVar()
        self._use_sublayers.set(self._configuration_api.get_use_sublayers())
        self._use_shufflelayers = IntVar()
        self._use_shufflelayers.set(self._configuration_api.get_use_shufflelayers())
        self._use_overlap = IntVar()
        self._use_overlap.set(self._configuration_api.get_use_overlap())

        self.sublayer_height_entry_text = DoubleVar()
        self.sublayer_height_entry_text.set(self._configuration_api.get_sublayer_height_mm())
        self.overlap_amount_entry_text = DoubleVar()
        self.overlap_amount_entry_text.set(self._configuration_api.get_overlap_amount_mm())

        Label(self, text = 'Printer: ').grid(column=0,row=10)
        Label(self, text = self._configuration_api.current_printer()).grid(column=1,row=10)
        Button(self, text='?', command=self._help).grid(column=2, row=10,stick=N+E)

        Label(self).grid(column=1,row=15)

        Label(self, text = "Spot Diameter (mm) [0.5]" ).grid(column=0,row=20,sticky=N+S+E)
        Entry(self, textvariable = self.laser_thickness_entry_text).grid(column=1, row=20)

        Label(self, text = "Maximum Lead Distance (mm) [0.5]" ).grid(column=0,row=40,sticky=N+S+E)
        Entry(self, textvariable = self.max_lead_distance_entry_text).grid(column=1, row=40)

        Label(self, text = "Scale Image [1.0]" ).grid(column=0,row=45,sticky=N+S+E)
        Entry(self, textvariable = self.scaling_factor_entry_text).grid(column=1, row=45)

        Label(self).grid(column=1,row=50)

        Checkbutton(self, text="Use Sublayers", variable = self._use_sublayers, command=self._update_field_visibility).grid(column=0, row = 60, sticky=W)
        Entry(self, textvariable = self.sublayer_height_entry_text).grid(column=1, row=60)
        Label(self, text = "Sublayer Size (mm) [0.01]" ).grid(column=2,row=60,sticky=N+S+W)

        Checkbutton(self, text="Use Overlap", variable = self._use_shufflelayers, command=self._update_field_visibility).grid(column=0, row = 70, sticky=W)
        Entry(self, textvariable = self.overlap_amount_entry_text).grid(column=1, row=70)
        Label(self, text = "Overlap Amount (mm) [1.0]" ).grid(column=2,row=70,sticky=N+S+W)

        Checkbutton(self, text="Use Shuffled Starting Points", variable = self._use_overlap, command=self._update_field_visibility).grid(column=0, row = 80, sticky=W)

        Label(self).grid(column=1,row=90)

        serial_frame = LabelFrame(self, text="Serial Options (for hackers)", padx=5, pady=5)
        serial_frame.grid(column=0,row=100, columnspan=3,sticky=N+S+W+E)
        # ----------------------Frame Start---------------------------
        self._use_serial = IntVar()
        self._use_serial.set(self._configuration_api.get_serial_enabled())
        self._serial_on_command = StringVar()
        self._serial_on_command.set(self._configuration_api.get_serial_on_command())
        self._serial_off_command = StringVar()
        self._serial_off_command.set(self._configuration_api.get_serial_off_command())
        
        self._serial_layer_start_command = StringVar()
        self._serial_layer_start_command.set(self._configuration_api.get_layer_started_command())
        self._serial_layer_end_command = StringVar()
        self._serial_layer_end_command.set(self._configuration_api.get_layer_ended_command())
        self._serial_print_end_command = StringVar()
        self._serial_print_end_command.set(self._configuration_api.get_print_ended_command())

        self._serial_port = StringVar()
        self._serial_port.set(self._configuration_api.get_serial_port())

        Checkbutton(serial_frame, text="Use Serial Drip Control", variable = self._use_serial, command=self._showhide_serial).grid(column=0, row = 10)
        Label(serial_frame,text="Serial Port").grid(column=0, row=20,sticky=N+S+E)
        self._serial_port_entry = Entry(serial_frame,textvariable=self._serial_port)
        self._serial_port_entry.grid(column=1, row=20)
        Label(serial_frame,text="Serial On Command").grid(column=0, row=30,sticky=N+S+E)
        self._serial_on_entry = Entry(serial_frame,textvariable=self._serial_on_command)
        self._serial_on_entry.grid(column=1, row=30)
        Label(serial_frame,text="Serial Off Command").grid(column=0, row=40,sticky=N+S+E)
        self._serial_off_entry = Entry(serial_frame,textvariable=self._serial_off_command)
        self._serial_off_entry.grid(column=1, row=40)

        Label(serial_frame,text="Serial Layer Started Command").grid(column=0, row=50,sticky=N+S+E)
        self._serial_layer_start_entry = Entry(serial_frame,textvariable=self._serial_layer_start_command)
        self._serial_layer_start_entry.grid(column=1, row=50)
        Label(serial_frame,text="Serial Layer Ended Command").grid(column=0, row=60,sticky=N+S+E)
        self._serial_layer_end_entry = Entry(serial_frame,textvariable=self._serial_layer_end_command)
        self._serial_layer_end_entry.grid(column=1, row=60)
        Label(serial_frame,text="Serial Print Ended Command").grid(column=0, row=70,sticky=N+S+E)
        self._serial_print_end_entry = Entry(serial_frame,textvariable=self._serial_print_end_command)
        self._serial_print_end_entry.grid(column=1, row=70)

        self._showhide_serial()

        # ----------------------Frame End---------------------------

        Label(self).grid(column=1,row=103)
        devmode_options_frame = LabelFrame(self, text="Development Mode Options", padx=5, pady=5)
        devmode_options_frame.grid(column=0,row=105, columnspan=3,sticky=N+S+W+E)
        # ----------------------Frame Start---------------------------
        self._print_queue_delay = DoubleVar()
        self._print_queue_delay.set(self._configuration_api.get_print_queue_delay())
        
        Label(devmode_options_frame,text="Print Queue Delay").grid(column=0, row=70)
        Entry(devmode_options_frame,textvariable=self._print_queue_delay).grid(column=1, row=70)

        if not devmode:
            devmode_options_frame.grid_remove()
        else:
            Label(self).grid(column=1,row=110)

        # ----------------------Frame End---------------------------

        

        Button(self, text ="Back", command = self._back).grid(column=0,row=120,sticky=N+S+W)
        Button(self, text ="Save", command = self._save).grid(column=2,row=120,sticky=N+S+E)
        self.update()

    def _update_field_visibility(self):
        pass

    def _showhide_serial(self):
        if self._use_serial.get():
            self._serial_off_entry.configure(state='normal')
            self._serial_on_entry.configure(state='normal')
            self._serial_port_entry.configure(state='normal')
            self._serial_layer_start_entry.configure(state='normal')
            self._serial_layer_end_entry.configure(state='normal')
            self._serial_print_end_entry.configure(state='normal')
        else:
            self._serial_off_entry.configure(state='disabled')
            self._serial_on_entry.configure(state='disabled')
            self._serial_port_entry.configure(state='disabled')
            self._serial_layer_start_entry.configure(state='disabled')
            self._serial_layer_end_entry.configure(state='disabled')
            self._serial_print_end_entry.configure(state='disabled')

    def _help(self):
        PopUp(self,'Help', help_text.options_help)

    def _back(self):
        self.navigate(SetupUI)

    def _save(self):
        self._configuration_api.set_laser_thickness_mm(float(self.laser_thickness_entry_text.get()))
        self._configuration_api.set_max_lead_distance_mm(float(self.max_lead_distance_entry_text.get()))
        self._configuration_api.set_scaling_factor(float(self.scaling_factor_entry_text.get()))

        self._configuration_api.set_sublayer_height_mm(float(self.sublayer_height_entry_text.get()))
        self._configuration_api.set_overlap_amount_mm(float(self.overlap_amount_entry_text.get()))

        self._configuration_api.set_use_sublayers(bool(self._use_sublayers.get()))
        self._configuration_api.set_use_shufflelayers(bool(self._use_shufflelayers.get()))
        self._configuration_api.set_use_overlap(bool(self._use_overlap.get()))

        self._configuration_api.set_serial_enabled(bool(self._use_serial.get()))
        self._configuration_api.set_serial_port(self._serial_port.get())
        self._configuration_api.set_serial_on_command(self._serial_on_command.get())
        self._configuration_api.set_serial_off_command(self._serial_off_command.get())
        self._configuration_api.set_layer_started_command(self._serial_layer_start_command.get())
        self._configuration_api.set_layer_ended_command(self._serial_layer_end_command.get())
        self._configuration_api.set_print_ended_command(self._serial_print_end_command.get())
        if devmode:
            self._configuration_api.set_print_queue_delay(self._print_queue_delay.get())

        self.navigate(SetupUI, printer = self._current_printer)

    def close(self):
        pass

class DripCalibrationUI(PeachyFrame, FieldValidations):
    
    def initialize(self):
        self._current_printer = self.kwargs['printer']
        self._configuration_api = ConfigurationAPI(self._configuration_manager)
        self._configuration_api.load_printer(self._current_printer)
        self.grid()

        self._dripper_type = StringVar()
        self._dripper_type.set(self._configuration_api.get_dripper_type())

        Label(self, text = 'Printer: ').grid(column=0,row=10)
        Label(self, text = self._configuration_api.current_printer()).grid(column=1,row=10)
        Button(self, text='?', command=self._help).grid(column=2, row=10,stick=N+E)
        
        Label(self).grid(column=1,row=15)

        Radiobutton(self, text="Microphone Dripper", variable=self._dripper_type, value="audio", command = self._dripper_type_changed).grid(column=0,row=20,sticky=N+S+E+W)
        Radiobutton(self, text="Emulated Dripper ", variable=self._dripper_type, value="emulated", command = self._dripper_type_changed).grid(column=1,row=20,sticky=N+S+E+W)

        
        # ---------------- Microphone Dripper Frame Start -------------------------
        self._drip_count = IntVar()

        self._drips_per_mm = DoubleVar()
        self._drips_per_mm.set(self._configuration_api.get_drips_per_mm())

        self._target_height_mm = IntVar()
        self._target_height_mm.set(100)

        self._current_height_mm = StringVar()
        self._current_height_mm.set(0)


        self._average_drips = StringVar()
        self._average_drips.set(0)

        self.real_dripper_frame = LabelFrame(self, text="Microphone Dripper Setup", padx=5, pady=5)
        self.real_dripper_frame.grid(column=0,row=30, columnspan=3)

        Label(self.real_dripper_frame,text='Drips', anchor=CENTER).grid(column=0,row=20,sticky=N+S+E+W)
        Label(self.real_dripper_frame,text='Drips/Second', anchor=CENTER).grid(column=1,row=20,sticky=N+S+E+W)
        Label(self.real_dripper_frame,text='Target Height(mm)', anchor=W,justify="right").grid(column=2,row=20,sticky=N+S+E+W)
        Label(self.real_dripper_frame,text="Drips/mm", anchor=W, justify="right").grid(column=4,row=20,sticky=N+S+E+W)
        Label(self.real_dripper_frame,text="Current Height(mm)", anchor=W, justify="right").grid(column=5,row=20,sticky=N+S+E+W)

        Label(self.real_dripper_frame,textvariable=self._drip_count,  anchor=CENTER, justify=CENTER).grid(column=0,row=30,sticky=N+S+E+W)
        Label(self.real_dripper_frame,textvariable=self._average_drips,  anchor=CENTER, justify=CENTER).grid(column=1,row=30,sticky=N+S+E+W)
        Entry(self.real_dripper_frame, width=5, justify=LEFT, textvariable=self._target_height_mm, validate = 'key').grid(column=2,row=30,sticky=N+S+E+W)
        Label(self.real_dripper_frame,text=" -> ", anchor=W, justify=RIGHT).grid(column=3,row=30,sticky=N+S+E+W)
        dripper_drips_per_mm_field = Entry(self.real_dripper_frame,textvariable=self._drips_per_mm)
        dripper_drips_per_mm_field.grid(column=4,row=30,sticky=N+S+E+W)
        dripper_drips_per_mm_field.bind('<Key>', self._drips_per_mm_changed)
        dripper_drips_per_mm_field.bind('<FocusOut>', self._drips_per_mm_changed)
        Label(self.real_dripper_frame,textvariable=self._current_height_mm,  anchor=CENTER, justify=CENTER).grid(column=5,row=30,sticky=N+S+E+W)

        Label(self.real_dripper_frame).grid(column=1,row=40)

        Button(self.real_dripper_frame,text="Reset", command=self._reset).grid(column=0,row=50,sticky=N+S+E+W)
        Button(self.real_dripper_frame,text="Calculate", command=self._calculate , justify=CENTER).grid(column=2,row=50, columnspan=3)

        Label(self.real_dripper_frame).grid(column=1,row=60)

        if self._configuration_api.get_serial_enabled:
            Label(self.real_dripper_frame, text="Serial Dripper Tests").grid(column = 0, row = 65)
            Button(self.real_dripper_frame, text="Turn On dripper", command=self._dripper_on).grid(column = 1, row = 65)
            Button(self.real_dripper_frame, text="Turn Off dripper", command=self._dripper_off).grid(column = 2, row = 65)
            Label(self.real_dripper_frame).grid(column=1,row=70)


        self.real_dripper_frame.grid_remove()
        # ---------------- Microphone Dripper Frame Stop -------------------------
        # ---------------- Manual Dripper Frame Start ----------------------------
        self._drips_per_second = DoubleVar()
        self._drips_per_second.set(self._configuration_api.get_emulated_drips_per_second())

        self.fake_dripper_frame = LabelFrame(self, text="Emulated Dripper Setup", padx=5, pady=5)
        self.fake_dripper_frame.grid(column=0,row=40, columnspan=3,sticky=N+S+E+W)
        self.fake_dripper_frame.grid_remove()

        Label(self.fake_dripper_frame, text="Drips per second").grid(column=1,row=10)
        Entry(self.fake_dripper_frame, textvariable=self._drips_per_second).grid(column=2,row=10)

        Label(self.fake_dripper_frame, text="Drips per mm").grid(column=1,row=20)
        emulated_drips_per_mm_field = Entry(self.fake_dripper_frame, textvariable=self._drips_per_mm)
        emulated_drips_per_mm_field.grid(column=2,row=20,sticky=N+S+E+W)
        emulated_drips_per_mm_field.bind('<Key>', self._drips_per_mm_changed)
        emulated_drips_per_mm_field.bind('<FocusOut>', self._drips_per_mm_changed)
        # ---------------- Manual Dripper Frame Stop ----------------------------
        Label(self).grid(column=0,row=45)
        Button(self,text=u"Back", command=self._back, width=10).grid(column=0,row=50,sticky=N+S+W)
        
        self.update()
        self._dripper_type_changed()
        

    def _dripper_type_changed(self):
        if self._dripper_type.get() == 'audio':
            self._configuration_api.set_dripper_type('audio')
            self.fake_dripper_frame.grid_remove()
            self.real_dripper_frame.grid()
            self._configuration_api.start_counting_drips(drip_call_back = self._drips_updated)
        elif self._dripper_type.get() == 'emulated':
            self._configuration_api.set_dripper_type('emulated')
            self._configuration_api.stop_counting_drips()
            self.real_dripper_frame.grid_remove()
            self.fake_dripper_frame.grid()
        else:
            raise Exception('Unsupported Dripper: %s ' % self._dripper_type.get() )

    def _drips_updated(self, drips, height, drips_per_second):
        self._drip_count.set(drips)
        self._current_height_mm.set('%.2F' % height)
        self._average_drips.set("%0.2f" % drips_per_second)

    def _dripper_on(self):
        self._configuration_api.send_dripper_on_command()

    def _dripper_off(self):
        self._configuration_api.send_dripper_off_command()

    def _reset(self):
        self._configuration_api.reset_drips()

    def _back(self):
        self._configuration_api.set_emulated_drips_per_second(self._drips_per_second.get())
        self._configuration_api.set_drips_per_mm(self._drips_per_mm.get())
        self._configuration_api.stop_counting_drips()
        self._configuration_api.save()
        self.navigate(SetupUI, printer = self._current_printer)

    def _help(self):
        PopUp(self,'Help', help_text.setup_drip_calibration_help)

    def _calculate(self):
        if self._drip_count.get() > 0:
            drips_per_mm = (self._drip_count.get() * 1.0) / (self._target_height_mm.get() * 1.0)
            self._configuration_api.set_drips_per_mm(drips_per_mm)
            self._drips_per_mm.set(drips_per_mm)

    def _drips_per_mm_changed(self, event):
        drips_per_mm = self._drips_per_mm.get()
        if drips_per_mm > 0.0:
            self._configuration_api.set_drips_per_mm(drips_per_mm)

    def close(self):
        self._configuration_api.stop_counting_drips()

class SetupAudioUI(PeachyFrame):

    def initialize(self):
        self.grid()
        self._current_printer = self.kwargs['printer']
        self._configuration_api = ConfigurationAPI(self._configuration_manager)
        self._configuration_api.load_printer(self._current_printer)

        audio_options = self._configuration_api.get_available_audio_options()

        self._input_options = dict([ (str(option), option) for option in audio_options['inputs']])
        self._output_options = dict([ (str(option), option) for option in audio_options['outputs']])

        if (len(self._input_options) < 1 or len(self._output_options) < 1):
            logging.error("No inputs available")
            tkMessageBox.showwarning('Error','Audio card appears to not be setup correctly, Have you plugged in your dripper and printer?')
            self._back()
            return
            
        self._input_audio_selection_current = StringVar()
        self._input_audio_selection_current.set(self._currently_selected(self._input_options))

        self._output_options = dict([ (str(option), option) for option in audio_options['outputs']])

        self._output_audio_selection_current = StringVar()
        self._output_audio_selection_current.set(self._currently_selected(self._output_options))
        
        Label(self, text = 'Printer: ').grid(column=0,row=10)
        Label(self, text = self._configuration_api.current_printer()).grid(column=1,row=10)
        Button(self, text='?', command=self._help).grid(column=2, row=10,stick=N+E)

        Label(self).grid(column=0,row=20)
        Label(self, text = 'Selecting a format not supported by your system may result in odd behaviour').grid(column=0,row=25,columnspan=3)
        Label(self).grid(column=0,row=26)

        Label(self, text = "Audio Input Settings" ).grid(column=0,row=30)
        OptionMenu( self, self._input_audio_selection_current, *self._input_options.keys()).grid(column=1,row=30,sticky=NSEW)

        Label(self, text = "Audio Output Settings" ).grid(column=0,row=40)
        OptionMenu(self, self._output_audio_selection_current, *self._output_options.keys()).grid(column=1,row=40,sticky=NSEW)

        Label(self).grid(column=0,row=50)

        Button(self, text ="Back", command = self._back).grid(column=0,row=60,sticky=N+S+W)
        Button(self, text ="Save", command = self._save).grid(column=1,row=60,sticky=N+S+E)

        self.update()

    def _currently_selected(self, audio_options):
        current_option = [ k for k, v in audio_options.iteritems() if v.current ]
        if (len(current_option) == 0):
            return audio_options[0]
        else:
            return current_option[0]

    def _get_recommend_audio_index(self, options):
        for i in range(0,len(options)):
            if options[i].endswith('(Recommended)'):
                return i
        return 0

    def _back(self):
        self.navigate(SetupUI, printer = self._current_printer)

    def _help(self):
        PopUp(self,'Help', help_text.setup_audio_help)

    def _save(self):
        input_option = self._input_options[self._input_audio_selection_current.get()]
        output_option = self._output_options[self._output_audio_selection_current.get()]
        
        self._configuration_api.set_audio_input_options(input_option)
        self._configuration_api.set_audio_output_options(output_option)

        self.navigate(SetupUI)

    def close(self):
        pass

class CureTestUI(PeachyFrame):

    def initialize(self):
        self.grid()
        self._current_printer = self.kwargs['printer']
        self._configuration_api = ConfigurationAPI(self._configuration_manager)
        self._configuration_api.load_printer(self._current_printer)

        self._base_height = IntVar()
        self._base_height.set(3)
        self._total_height = IntVar()
        self._total_height.set(23)
        self._start_speed = IntVar()
        self._start_speed.set(50)
        self._stop_speed = IntVar()
        self._stop_speed.set(250)
        self._best_height = IntVar()
        self._best_height.set(0)

        Label(self, text = 'Printer: ').grid(column=0,row=10)
        Label(self, text = self._configuration_api.current_printer()).grid(column=1,row=10)
        Button(self, text='?', command=self._help).grid(column=2, row=10,stick=N+E)

        Label(self).grid(column=1,row=15)

        Label(self, text = "Base Height (mm)" ).grid(column=0,row=20)
        Entry(self, textvariable = self._base_height).grid(column=1, row=20)

        Label(self, text = "Total Height (mm)" ).grid(column=0,row=30)
        Entry(self, textvariable = self._total_height).grid(column=1, row=30)

        Label(self, text = "Start Speed (mm)" ).grid(column=0,row=40)
        Entry(self, textvariable = self._start_speed).grid(column=1, row=40)

        Label(self, text = "Finish Speed (mm)" ).grid(column=0,row=50)
        Entry(self, textvariable = self._stop_speed).grid(column=1, row=50)
        Label(self).grid(column=1,row=60)

        Button(self, text ="Run Test", command = self._start).grid(column=2,row=70,sticky=N+S+E)

        Label(self).grid(column=1,row=80)

        Label(self, text = "Best height above base (mm)" ).grid(column=0,row=90)
        self._best_height_field = Entry(self, textvariable = self._best_height)
        self._best_height_field.grid(column=1, row=90)
        
        Label(self).grid(column=1,row=100)

        Button(self, text ="Save", command = self._save).grid(column=2,row=110,sticky=N+S+W)
        Button(self, text ="Back", command = self._back).grid(column=0,row=110,sticky=N+S+W)

        self.update()

    def _back(self):
        self.navigate(SetupUI, printer = self._current_printer)

    def _help(self):
        PopUp(self,'Help', help_text.cure_test_help)

    def _save(self):
        try:
            speed = self._configuration_api.get_speed_at_height(
                    self._base_height.get(),
                    self._total_height.get(),
                    self._start_speed.get(),
                    self._stop_speed.get(),
                    self._best_height.get()
                    )
            self._configuration_api.set_speed(speed)
            self.navigate(SetupUI)
        except Exception as ex:
            tkMessageBox.showwarning("Error", ex.message)

    def _start(self):
        try:
            cure_test = self._configuration_api.get_cure_test(
                self._base_height.get(),
                self._total_height.get(),
                self._start_speed.get(),
                self._stop_speed.get()
                )
            self.navigate(PrintStatusUI,layer_generator = cure_test, config = self._configuration_api.get_current_config(), calling_class = CureTestUI, printer = self._current_printer)
        except Exception as ex:
            tkMessageBox.showwarning("Error", ex.message)

    def close(self):
        pass