from Tkinter import *
import tkMessageBox
from ui.ui_tools import *
from ui.main_ui import MainUI
from ui.calibration_ui import *
from api.configuration_api import ConfigurationAPI
from print_ui import PrintStatusUI
from infrastructure.print_test_layer_generators import HalfVaseTestGenerator
from api.test_print_api import TestPrintAPI
import help_text
import traceback


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
            command=self._printer_selected)
        printer_selection_menu.grid(column=1, row=10, sticky=NSEW)

        Button(self,text=u"Add Printer", command=self._add_printer).grid(column=2, row=10, sticky=NSEW)
        Label(self).grid(column=0, row=15)
        Button(self,text=u"Setup Circut", command=self._setup_circut).grid(column=1, row=20, sticky=NSEW)
        Button(self,text=u"Setup Options", command=self._setup_options).grid(column=1, row=30, sticky=NSEW)
        Button(self,text=u"Setup Drip Calibration", command=self._drip_calibration).grid(column=1, row=40, sticky=NSEW)
        Button(self,text=u"Setup Calibration", command=self._calibration).grid(column=1, row=50, sticky=NSEW)
        Button(self,text=u"Run Cure Test", command=self._cure_test).grid(column=1, row=60, sticky=NSEW)
        Button(self,text=u"Print Test Print", command=self._test_print).grid(column=1, row=65, sticky=NSEW)
        Label(self).grid(column=0, row=70)
        Button(self,text=u"Back", command=self._back).grid(column=0, row=100)

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

    def _setup_circut(self):
        self.navigate(SetupCircutUI, printer = self._current_printer)

    def _calibration(self):
        self.navigate(CalibrationUI, printer = self._current_printer)

    def _cure_test(self):
        self.navigate(CureTestUI, printer = self._current_printer)

    def _test_print(self):
        self.navigate(TestPrintUI, printer = self._current_printer)

    def close(self):
        pass


class AddPrinterUI(PeachyFrame):
    def initialize(self):
        self.grid()
        self._configuration_api = ConfigurationAPI(self._configuration_manager)
        
        self._printer_name = StringVar()

        Label(self, text="Enter a name for your printer").grid(column=0, row=10)
        Entry(self, textvariable=self._printer_name).grid(column=1, row=10)

        Label(self).grid(column=1, row=20)

        Button(self, text ="Save", command=self._save).grid(column=1, row=30, sticky=N+S+E)

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

        self.laser_thickness_entry_text=DoubleVar()
        self.laser_thickness_entry_text.set(self._configuration_api.get_laser_thickness_mm())
        self.max_lead_distance_entry_text=DoubleVar()
        self.max_lead_distance_entry_text.set(self._configuration_api.get_max_lead_distance_mm())
        self.scaling_factor_entry_text=DoubleVar()
        self.scaling_factor_entry_text.set(self._configuration_api.get_scaling_factor())
        self.wait_after_move_entry_text =IntVar()
        self.wait_after_move_entry_text.set(self._configuration_api.get_wait_after_move_milliseconds())
        self.post_fire_delay_entry_text =IntVar()
        self.post_fire_delay_entry_text.set(self._configuration_api.get_post_fire_delay())

        self._use_sublayers = IntVar()
        self._use_sublayers.set(self._configuration_api.get_use_sublayers())
        self._use_shufflelayers = IntVar()
        self._use_shufflelayers.set(self._configuration_api.get_use_shufflelayers())
        self._use_overlap = IntVar()
        self._use_overlap.set(self._configuration_api.get_use_overlap())

        self.sublayer_height_entry_text=DoubleVar()
        self.sublayer_height_entry_text.set(self._configuration_api.get_sublayer_height_mm())
        self._shuffle_layers_amount = DoubleVar()
        self._shuffle_layers_amount.set(self._configuration_api.get_shuffle_layers_amount())
        self.overlap_amount_entry_text=DoubleVar()
        self.overlap_amount_entry_text.set(self._configuration_api.get_overlap_amount_mm())

        Label(self, text='Printer: ').grid(column=0, row=10)
        Label(self, text=self._configuration_api.current_printer()).grid(column=1, row=10)
        Button(self, text='?', command=self._help).grid(column=2, row=10,stick=N+E)

        Label(self).grid(column=1, row=15)

        Label(self, text="Spot Diameter (mm) [0.5]").grid(column=0, row=20, sticky=N+S+E)
        Entry(self, textvariable=self.laser_thickness_entry_text, width=6).grid(column=1, row=20, sticky=N+S+W)

        Label(self, text="Maximum Lead Distance (mm) [0.5]").grid(column=0, row=40, sticky=N+S+E)
        Entry(self, textvariable=self.max_lead_distance_entry_text, width=6).grid(column=1, row=40, sticky=N+S+W)

        Label(self, text="Scale Image [1.0]").grid(column=2, row=20, sticky=N+S+E)
        Entry(self, textvariable=self.scaling_factor_entry_text, width=6).grid(column=3, row=20, sticky=N+S+W)

        Label(self, text="Wait After Move (milliseconds) [5]").grid(column=2, row=40, sticky=N+S+E)
        Entry(self, textvariable=self.wait_after_move_entry_text, width=6).grid(column=3, row=40, sticky=N+S+W)

        Label(self, text="Laser Post Fire Delay (milliseconds) [5]").grid(column=2, row=45, sticky=N+S+E)
        Entry(self, textvariable=self.post_fire_delay_entry_text, width=6).grid(column=3, row=45, sticky=N+S+W)

        Label(self).grid(column=1, row=50)

        Checkbutton(self, text="Use Sublayers", variable = self._use_sublayers, command=self._update_field_visibility).grid(column=0, row=60, sticky=W)
        Entry(self, textvariable=self.sublayer_height_entry_text).grid(column=1, row=60)
        Label(self, text="Sublayer Size (mm) [0.01]").grid(column=2, row=60, sticky=N+S+W)

        Checkbutton(self, text="Use Overlap", variable = self._use_overlap, command=self._update_field_visibility).grid(column=0, row=70, sticky=W)
        Entry(self, textvariable=self.overlap_amount_entry_text).grid(column=1, row=70)
        Label(self, text="Overlap Amount (mm) [1.0]").grid(column=2, row=70, sticky=N+S+W)

        Checkbutton(self, text="Use Spirialed Starting Points", variable = self._use_shufflelayers, command=self._update_field_visibility).grid(column=0, row=80, sticky=W)
        Entry(self, textvariable=self._shuffle_layers_amount).grid(column=1, row=80)
        Label(self, text="Spiral Amount Per Layer [1.0]").grid(column=2, row=80, sticky=N+S+W)

        Label(self).grid(column=1, row=90)

        serial_frame = LabelFrame(self, text="Serial Options (for hackers)", padx=5, pady=5)
        serial_frame.grid(column=0, row=100, columnspan=3, sticky=N+S+W+E)
        # ----------------------Frame Start---------------------------
        self._use_serial = IntVar()
        self._use_serial.set(self._configuration_api.get_serial_enabled())
        self._serial_on_command=StringVar()
        self._serial_on_command.set(self._configuration_api.get_serial_on_command())
        self._serial_off_command=StringVar()
        self._serial_off_command.set(self._configuration_api.get_serial_off_command())
        
        self._serial_layer_start_command=StringVar()
        self._serial_layer_start_command.set(self._configuration_api.get_layer_started_command())
        self._serial_layer_end_command=StringVar()
        self._serial_layer_end_command.set(self._configuration_api.get_layer_ended_command())
        self._serial_print_end_command=StringVar()
        self._serial_print_end_command.set(self._configuration_api.get_print_ended_command())



        self._serial_port = StringVar()
        self._serial_port.set(self._configuration_api.get_serial_port())

        Checkbutton(serial_frame, text="Use Serial Drip Control", variable = self._use_serial, command=self._showhide_serial).grid(column=0, row=10, columnspan=4, sticky=N+S+W)
        Label(serial_frame,text=" Port").grid(column=0, row=20, sticky=N+S+E)
        self._serial_port_entry = Entry(serial_frame,textvariable=self._serial_port)
        self._serial_port_entry.grid(column=1, row=20, columnspan= 3)

        Label(serial_frame,text="Dripper On").grid(column=0, row=30, sticky=N+S+E)
        self._serial_on_entry = Entry(serial_frame,textvariable=self._serial_on_command, width=2)
        self._serial_on_entry.grid(column=1, row=30)
        Label(serial_frame,text="Dripper Off").grid(column=0, row=40, sticky=N+S+E)
        self._serial_off_entry = Entry(serial_frame,textvariable=self._serial_off_command, width=2)
        self._serial_off_entry.grid(column=1, row=40)

        Label(serial_frame,text="Layer Started").grid(column=2, row=30, sticky=N+S+E)
        self._serial_layer_start_entry = Entry(serial_frame,textvariable=self._serial_layer_start_command, width=2)
        self._serial_layer_start_entry.grid(column=3, row=30)
        Label(serial_frame,text="Layer Ended").grid(column=2, row=40, sticky=N+S+E)
        self._serial_layer_end_entry = Entry(serial_frame,textvariable=self._serial_layer_end_command, width=2)
        self._serial_layer_end_entry.grid(column=3, row=40)
        Label(serial_frame,text="Print Ended").grid(column=2, row=50, sticky=N+S+E)
        self._serial_print_end_entry = Entry(serial_frame,textvariable=self._serial_print_end_command, width=2)
        self._serial_print_end_entry.grid(column=3, row=50)

        self._showhide_serial()

        # ----------------------Frame End---------------------------

        Label(self).grid(column=1, row=103)
        devmode_options_frame = LabelFrame(self, text="Development Mode Options", padx=5, pady=5)
        devmode_options_frame.grid(column=0, row=105, columnspan=3, sticky=N+S+W+E)
        # ----------------------Frame Start---------------------------
        self._print_queue_delay = DoubleVar()
        self._print_queue_delay.set(self._configuration_api.get_print_queue_delay())
        self._pre_layer_delay = DoubleVar()
        self._pre_layer_delay.set(self._configuration_api.get_pre_layer_delay())
        self._write_wav_files = IntVar()
        self._write_wav_files.set(self._configuration_api.get_write_wav_files())
        self._write_wav_files_folder = StringVar()
        self._write_wav_files_folder.set(self._configuration_api.get_write_wav_files_folder())

        
        Label(devmode_options_frame,text="Print Queue Delay (Seconds)").grid(column=0, row=70)
        Entry(devmode_options_frame,textvariable=self._print_queue_delay, width=6).grid(column=1, row=70)

        Label(devmode_options_frame,text="Pre Layer Delay (Seconds)").grid(column=2, row=70)
        Entry(devmode_options_frame,textvariable=self._pre_layer_delay, width=6).grid(column=3, row=70)

        Checkbutton(devmode_options_frame, text="Print To Wave Files", variable = self._write_wav_files).grid(column=0, row=71, sticky=N+S+W)
        Label(devmode_options_frame,text="Wav Folder").grid(column=2, row=71)
        Entry(devmode_options_frame,textvariable=self._write_wav_files_folder, width=60).grid(column=2, row=71)


        if not devmode:
            devmode_options_frame.grid_remove()
        else:
            Label(self).grid(column=1, row=110)

        # ----------------------Frame End---------------------------

        Label(self).grid(column=1, row=106)
        email_options_frame = LabelFrame(self, text="Email Notification Options", padx=5, pady=5)
        email_options_frame.grid(column=0, row=107, columnspan=3, sticky=N+S+W+E)

        # ----------------------Frame Start---------------------------
        self._email_on = IntVar()
        self._email_port = IntVar()
        self._email_host = StringVar()
        self._email_sender = StringVar()
        self._email_recipient = StringVar()

        self._email_on.set(self._configuration_api.get_email_on())
        self._email_port.set(self._configuration_api.get_email_port())
        self._email_host.set(self._configuration_api.get_email_host())
        self._email_sender.set(self._configuration_api.get_email_sender())
        self._email_recipient.set(self._configuration_api.get_email_recipient())

        Checkbutton(email_options_frame, text="Use Email Notifications", variable = self._email_on).grid(column=0, row=10)
        Label(email_options_frame,text="SMPTP Host Name").grid(column=0, row=20)
        Entry(email_options_frame,textvariable=self._email_host).grid(column=1, row=20)
        Label(email_options_frame,text="SMTP Port").grid(column=0, row=30)
        Entry(email_options_frame,textvariable=self._email_port).grid(column=1, row=30)
        Label(email_options_frame,text="Sender Email Address").grid(column=0, row=40)
        Entry(email_options_frame,textvariable=self._email_sender).grid(column=1, row=40)
        Label(email_options_frame,text="Recipient Email Address").grid(column=0, row=50)
        Entry(email_options_frame,textvariable=self._email_recipient).grid(column=1, row=50)


        # ----------------------Frame End---------------------------


        Button(self, text ="Back", command=self._back).grid(column=0, row=120, sticky=N+S+W)
        Button(self, text ="Save", command=self._save).grid(column=2, row=120, sticky=N+S+E)
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
        self._configuration_api.set_wait_after_move_milliseconds(self.wait_after_move_entry_text.get())
        self._configuration_api.set_post_fire_delay(self.post_fire_delay_entry_text.get())

        self._configuration_api.set_sublayer_height_mm(float(self.sublayer_height_entry_text.get()))
        self._configuration_api.set_shuffle_layers_amount(float(self._shuffle_layers_amount.get()))
        self._configuration_api.set_overlap_amount_mm(float(self.overlap_amount_entry_text.get()))

        self._configuration_api.set_use_sublayers(bool(self._use_sublayers.get()))
        self._configuration_api.set_use_shufflelayers(bool(self._use_shufflelayers.get()))
        self._configuration_api.set_use_overlap(bool(self._use_overlap.get()))

        self._configuration_api.set_email_on(bool(self._email_on.get()))
        self._configuration_api.set_email_port(self._email_port.get())
        self._configuration_api.set_email_host(self._email_host.get())
        self._configuration_api.set_email_sender(self._email_sender.get())
        self._configuration_api.set_email_recipient(self._email_recipient.get())

        self._configuration_api.set_serial_enabled(bool(self._use_serial.get()))
        self._configuration_api.set_serial_port(self._serial_port.get())
        self._configuration_api.set_serial_on_command(self._serial_on_command.get())
        self._configuration_api.set_serial_off_command(self._serial_off_command.get())
        self._configuration_api.set_layer_started_command(self._serial_layer_start_command.get())
        self._configuration_api.set_layer_ended_command(self._serial_layer_end_command.get())
        self._configuration_api.set_print_ended_command(self._serial_print_end_command.get())
        if devmode:
            self._configuration_api.set_print_queue_delay(self._print_queue_delay.get())
            self._configuration_api.set_pre_layer_delay(self._pre_layer_delay.get())
            self._configuration_api.set_write_wav_files(bool(self._write_wav_files.get()))
            self._configuration_api.set_write_wav_files_folder(  self._write_wav_files_folder.get())

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

        Label(self, text='Printer: ').grid(column=0, row=10)
        Label(self, text=self._configuration_api.current_printer()).grid(column=1, row=10)
        Button(self, text='?', command=self._help).grid(column=2, row=10,stick=N+E)
        
        Label(self).grid(column=1, row=15)

        Radiobutton(self, text="Microphone", variable=self._dripper_type, value="audio", command=self._dripper_type_changed).grid(column=0, row=20, sticky=N+S+E+W)
        Radiobutton(self, text="Microcontroller", variable=self._dripper_type, value="microcontroller", command=self._dripper_type_changed).grid(column=1, row=20, sticky=N+S+E+W)
        Radiobutton(self, text="Emulated", variable=self._dripper_type, value="emulated", command=self._dripper_type_changed).grid(column=2, row=20, sticky=N+S+E+W)
        if devmode:
            Radiobutton(self, text="Photo Z Axis ", variable=self._dripper_type, value="photo", command=self._dripper_type_changed).grid(column=3, row=20, sticky=N+S+E+W)

        
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
        self.real_dripper_frame.grid(column=0, row=30, columnspan=3)

        Label(self.real_dripper_frame,text='Drips', anchor=CENTER).grid(column=0, row=20, sticky=N+S+E+W)
        Label(self.real_dripper_frame,text='Drips/Second', anchor=CENTER).grid(column=1, row=20, sticky=N+S+E+W)
        Label(self.real_dripper_frame,text='Target Height(mm)', anchor=W,justify="right").grid(column=2, row=20, sticky=N+S+E+W)
        Label(self.real_dripper_frame,text="Drips/mm", anchor=W, justify="right").grid(column=4, row=20, sticky=N+S+E+W)
        Label(self.real_dripper_frame,text="Current Height(mm)", anchor=W, justify="right").grid(column=5, row=20, sticky=N+S+E+W)

        Label(self.real_dripper_frame,textvariable=self._drip_count,  anchor=CENTER, justify=CENTER).grid(column=0, row=30, sticky=N+S+E+W)
        Label(self.real_dripper_frame,textvariable=self._average_drips,  anchor=CENTER, justify=CENTER).grid(column=1, row=30, sticky=N+S+E+W)
        Entry(self.real_dripper_frame, width=5, justify=LEFT, textvariable=self._target_height_mm, validate = 'key').grid(column=2, row=30, sticky=N+S+E+W)
        Label(self.real_dripper_frame,text=" -> ", anchor=W, justify=RIGHT).grid(column=3, row=30, sticky=N+S+E+W)
        dripper_drips_per_mm_field = Entry(self.real_dripper_frame,textvariable=self._drips_per_mm)
        dripper_drips_per_mm_field.grid(column=4, row=30, sticky=N+S+E+W)
        Label(self.real_dripper_frame,textvariable=self._current_height_mm,  anchor=CENTER, justify=CENTER).grid(column=5, row=30, sticky=N+S+E+W)

        Label(self.real_dripper_frame).grid(column=1, row=40)

        Button(self.real_dripper_frame,text="Reset", command=self._reset).grid(column=0, row=50, sticky=N+S+E+W)
        Button(self.real_dripper_frame,text="Calculate", command=self._calculate , justify=CENTER).grid(column=2, row=50, columnspan=3)

        Label(self.real_dripper_frame).grid(column=1, row=60)

        if self._configuration_api.get_serial_enabled:
            Label(self.real_dripper_frame, text="Serial Dripper Tests").grid(column = 0, row=65)
            Button(self.real_dripper_frame, text="Turn On dripper", command=self._dripper_on).grid(column = 1, row=65)
            Button(self.real_dripper_frame, text="Turn Off dripper", command=self._dripper_off).grid(column = 2, row=65)
            Label(self.real_dripper_frame).grid(column=1, row=70)


        self.real_dripper_frame.grid_remove()
        # ---------------- Microphone Dripper Frame Stop -------------------------
        # ---------------- Manual Dripper Frame Start ----------------------------
        self._drips_per_second = DoubleVar()
        self._drips_per_second.set(self._configuration_api.get_emulated_drips_per_second())

        self.fake_dripper_frame = LabelFrame(self, text="Emulated Dripper Setup", padx=5, pady=5)
        self.fake_dripper_frame.grid(column=0, row=40, columnspan=3, sticky=N+S+E+W)
        self.fake_dripper_frame.grid_remove()

        Label(self.fake_dripper_frame, text="Drips per second").grid(column=1, row=10)
        Entry(self.fake_dripper_frame, textvariable=self._drips_per_second).grid(column=2, row=10)

        Label(self.fake_dripper_frame, text="Drips per mm").grid(column=1, row=20)
        emulated_drips_per_mm_field = Entry(self.fake_dripper_frame, textvariable=self._drips_per_mm)
        emulated_drips_per_mm_field.grid(column=2, row=20, sticky=N+S+E+W)

        # ---------------- Manual Dripper Frame Stop ----------------------------
        # ---------------- Photo Dripper Frame Start ----------------------------
        self._layer_delay = DoubleVar()
        self._layer_delay.set(self._configuration_api.get_photo_zaxis_delay())

        self.photo_zaxis_frame = LabelFrame(self, text="Photo Z Axis Setup", padx=5, pady=5)
        self.photo_zaxis_frame.grid(column=0, row=42, columnspan=3, sticky=N+S+E+W)
        self.photo_zaxis_frame.grid_remove()

        Label(self.photo_zaxis_frame, text="Layer Delay").grid(column=1, row=10)
        layer_delay_field = Entry(self.photo_zaxis_frame, textvariable=self._layer_delay)
        layer_delay_field.grid(column=2, row=20, sticky=N+S+E+W)

        # ---------------- Photo Dripper Frame Stop ----------------------------

        Label(self).grid(column=0, row=45)
        Button(self,text=u"Back", command=self._back, width=10).grid(column=0, row=50, sticky=N+S+W)
        Button(self,text=u"Save", command=self._save, width=10).grid(column=2, row=50, sticky=N+S+E)
        
        self.update()
        self._dripper_frames = [self.fake_dripper_frame, self.photo_zaxis_frame, self.real_dripper_frame]
        self._configuration_api.start_counting_drips(drip_call_back = self._drips_updated)
        self._dripper_type_changed()

    def _dripper_type_changed(self):
        [frame.grid_remove() for frame in self._dripper_frames]
        try:
            self._configuration_api.set_dripper_type(self._dripper_type.get())
        except Exception as ex:
            tkMessageBox.showwarning("Warning", ex)

        if self._dripper_type.get() == 'audio':
            self.real_dripper_frame.grid()
        elif self._dripper_type.get() == 'emulated':
            self.fake_dripper_frame.grid()
        elif self._dripper_type.get() == 'photo':
            self.photo_zaxis_frame.grid()
        elif self._dripper_type.get() == 'microcontroller':
            self.real_dripper_frame.grid()

    def _drips_updated(self, drips, height, drips_per_second, drip_history = []):
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
        self._configuration_api.stop_counting_drips()
        self._configuration_api.save()
        self.navigate(SetupUI, printer = self._current_printer)

    def _save(self):
        self._configuration_api.set_emulated_drips_per_second(self._drips_per_second.get())
        self._configuration_api.set_drips_per_mm(self._drips_per_mm.get())
        self._configuration_api.set_photo_zaxis_delay(self._layer_delay.get())
        self._configuration_api.save()
        self._configuration_api.stop_counting_drips()
        self.navigate(SetupUI, printer = self._current_printer)

    def _help(self):
        PopUp(self,'Help', help_text.setup_drip_calibration_help)

    def _calculate(self):
        if self._drip_count.get() > 0:
            drips_per_mm = (self._drip_count.get() * 1.0) / (self._target_height_mm.get() * 1.0)
            self._configuration_api.set_drips_per_mm(drips_per_mm)
            self._drips_per_mm.set(drips_per_mm)

    def close(self):
        self._configuration_api.stop_counting_drips()


class SetupCircutUI(PeachyFrame):

    def initialize(self):
        try:
            self.grid()
            self._current_printer = self.kwargs['printer']
            self._configuration_api = ConfigurationAPI(self._configuration_manager)
            self._configuration_api.load_printer(self._current_printer)

            Label(self, text='Printer: ').grid(column=0, row=10)
            Label(self, text=self._configuration_api.current_printer()).grid(column=1, row=10)
            Button(self, text='?', command=self._help).grid(column=2, row=10, stick=N+E)

            audio_options = self._configuration_api.get_available_audio_options()
            self._digital_frame = LabelFrame(self, text="Digital Circut", padx=5, pady=5)
            self._analog_frame = LabelFrame(self, text="Analog Circut", padx=5, pady=5)
            self._circut_type = StringVar()

            if (len(audio_options['inputs']) > 0 and len(audio_options['outputs']) > 0):
                self._audio_available = True
                self.initialize_audio(audio_options)
                Radiobutton(self, text="Analog Circut", variable=self._circut_type, value="Analog", command=self._circut_type_changed).grid(column=0, row=20, sticky=N+S+E+W)
            else:
                self._audio_available = False

            self.initialize_micro()
            Radiobutton(self, text="Microcontroller ", variable=self._circut_type, value="Digital", command=self._circut_type_changed).grid(column=1, row=20, sticky=N+S+E+W)

            Label(self).grid(column=0, row=50)
            Button(self, text="Back", command=self._back).grid(column=0, row=60, sticky=N+S+W)
            Button(self, text="Save", command=self._save).grid(column=1, row=60, sticky=N+S+E)
            self._circut_type_changed()
            self.update()
        except Exception as ex:
            traceback.print_exc()
            raise(ex)

    def initialize_micro(self):
        self._port = StringVar()
        self._rate = IntVar()
        self._header = StringVar()
        self._footer = StringVar()
        self._escape = StringVar()
        self._version = StringVar()

        self._circut_type.set(self._configuration_api.get_circut_type())
        self._port.set(self._configuration_api.get_micro_com_port())
        self._rate.set(self._configuration_api.get_micro_com_rate())
        self._header.set(self._configuration_api.get_micro_com_header())
        self._footer.set(self._configuration_api.get_micro_com_footer())
        self._escape.set(self._configuration_api.get_micro_com_escape())
        self._version.set(self._configuration_api.get_circut_version())

        self._digital_frame.grid(column=0, row=31, columnspan=3, sticky=NSEW)
        Label(self._digital_frame, text="Circut Port").grid(column=1, row=10, sticky=N+E+S)
        Entry(self._digital_frame, textvariable=self._port, width=40).grid(column=2, row=10, sticky=N+W+S)
        Label(self._digital_frame, text="Data Rate").grid(column=1, row=20, sticky=N+E+S)
        Entry(self._digital_frame, textvariable=self._rate, width=10).grid(column=2, row=20, sticky=N+W+S)
        Label(self._digital_frame, text="Header").grid(column=1, row=40, sticky=N+E+S)
        Entry(self._digital_frame, textvariable=self._header, width=4).grid(column=2, row=40, sticky=N+W+S)
        Label(self._digital_frame, text="Footer").grid(column=1, row=60, sticky=N+E+S)
        Entry(self._digital_frame, textvariable=self._footer, width=4).grid(column=2, row=60, sticky=N+W+S)
        Label(self._digital_frame, text="Escape").grid(column=1, row=70, sticky=N+E+S)
        Entry(self._digital_frame, textvariable=self._escape, width=4).grid(column=2, row=70, sticky=N+W+S)
        Label(self._digital_frame, text="Circut Version").grid(column=1, row=90, sticky=N+E+S)
        Entry(self._digital_frame, textvariable=self._version, width=40).grid(column=2, row=90, sticky=N+W+S)

    def initialize_audio(self, audio_options):
        self._input_options = dict([ (str(option), option) for option in audio_options['inputs']])
        self._output_options = dict([ (str(option), option) for option in audio_options['outputs']])

        self._input_audio_selection_current = StringVar()
        self._input_audio_selection_current.set(self._currently_selected(self._input_options))
        self._output_options = dict([ (str(option), option) for option in audio_options['outputs']])
        self._output_audio_selection_current = StringVar()
        self._output_audio_selection_current.set(self._currently_selected(self._output_options))

        self._analog_frame = LabelFrame(self, text="Analog Circut", padx=5, pady=5)
        self._analog_frame.grid(column=0, row=30, columnspan=3, sticky=NSEW)

        Label(self._analog_frame).grid(column=0, row=20)
        Label(self._analog_frame, text='Selecting a format not supported by your system may result in odd behaviour').grid(column=0, row=25, columnspan=3)
        Label(self._analog_frame).grid(column=0, row=26)
        Label(self._analog_frame, text="Audio Input Settings").grid(column=0, row=30)
        OptionMenu(self._analog_frame, self._input_audio_selection_current, *self._input_options.keys()).grid(column=1, row=30, sticky=NSEW)
        Label(self._analog_frame, text="Audio Output Settings").grid(column=0, row=40)
        OptionMenu(self._analog_frame, self._output_audio_selection_current, *self._output_options.keys()).grid(column=1, row=40, sticky=NSEW)




    def _currently_selected(self, audio_options):
        current_option = [ k for k, v in audio_options.iteritems() if v.current ]
        if (len(current_option) == 0):
            return audio_options[0]
        else:
            return current_option[0]

    def disable_frame(self, frame):
        for child in frame.winfo_children():
                child.configure(state='disabled')

    def enable_frame(self, frame):
        for child in frame.winfo_children():
                child.configure(state='normal')

    def _circut_type_changed(self):
        if self._circut_type.get() == 'Digital':
            self.enable_frame(self._digital_frame)
            self.disable_frame(self._analog_frame)
        else:
            self.enable_frame(self._analog_frame)
            self.disable_frame(self._digital_frame)

    def _get_recommend_audio_index(self, options):
        for i in range(0, len(options)):
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
        self._configuration_api.set_micro_com_port(self._port.get())
        self._configuration_api.set_micro_com_rate(self._rate.get())
        self._configuration_api.set_micro_com_header(self._header.get())
        self._configuration_api.set_micro_com_footer(self._footer.get())
        self._configuration_api.set_micro_com_escape(self._escape.get())
        self._configuration_api.set_circut_type(self._circut_type.get())
        self._configuration_api.set_circut_version(self._version.get())
        self._configuration_api.save()

        self.navigate(SetupUI)

    def close(self):
        pass


class CureTestUI(PeachyFrame):

    def initialize(self):
        self.grid()
        self._current_printer = self.kwargs['printer']
        self._configuration_api = ConfigurationAPI(self._configuration_manager)
        self._configuration_api.load_printer(self._current_printer)

        self._base_height = DoubleVar()
        self._base_height.set(self._configuration_api.get_cure_rate_base_height())
        self._total_height = DoubleVar()
        self._total_height.set(self._configuration_api.get_cure_rate_total_height())
        self._start_speed = DoubleVar()
        self._start_speed.set(self._configuration_api.get_cure_rate_start_speed())
        self._stop_speed = DoubleVar()
        self._stop_speed.set(self._configuration_api.get_cure_rate_finish_speed())
        self._best_height = DoubleVar()
        self._best_height.set(0)
        self._cure_speed = DoubleVar()
        self._cure_speed.set(self._configuration_api.get_cure_rate_draw_speed())
        self._use_cure_speed = IntVar()
        self._use_cure_speed.set(self._configuration_api.get_cure_rate_use_draw_speed())

        Label(self, text='Printer: ').grid(column=0, row=10)
        Label(self, text=self._configuration_api.current_printer()).grid(column=1, row=10)
        Button(self, text='?', command=self._help).grid(column=2, row=10,stick=N+E)

        Label(self).grid(column=1, row=15)

        self._cure_test_frame = LabelFrame(self, text="Cure Test", padx=5, pady=5)
        self._cure_test_frame.grid(column=0, row=20, columnspan=3)
        Label(self._cure_test_frame, text="Base Height (mm)").grid(column=0, row=20)
        Entry(self._cure_test_frame, textvariable=self._base_height).grid(column=1, row=20)

        Label(self._cure_test_frame, text="Total Height (mm)").grid(column=0, row=30)
        Entry(self._cure_test_frame, textvariable=self._total_height).grid(column=1, row=30)

        Label(self._cure_test_frame, text="Start Speed (mm)").grid(column=0, row=40)
        Entry(self._cure_test_frame, textvariable=self._start_speed).grid(column=1, row=40)

        Label(self._cure_test_frame, text="Finish Speed (mm)").grid(column=0, row=50)
        Entry(self._cure_test_frame, textvariable=self._stop_speed).grid(column=1, row=50)
        Label(self._cure_test_frame).grid(column=1, row=60)

        Button(self._cure_test_frame, text ="Run Test", command=self._start).grid(column=2, row=20, rowspan=40, sticky=E)
        Label(self._cure_test_frame).grid(column=1, row=80)

        Label(self._cure_test_frame, text="Best height above base (mm)").grid(column=0, row=90)
        self._best_height_field = Entry(self._cure_test_frame, textvariable=self._best_height)
        self._best_height_field.grid(column=1, row=90)
        Button(self._cure_test_frame, text ="Calculate Cure Speed", command=self._calculate).grid(column=2, row=90, sticky=N+S+E)

        Label(self).grid(column=1, row=94)

        Label(self, text="Maximum Speed (mm/second)").grid(column=0, row=95)
        Entry(self, textvariable=self._cure_speed).grid(column=1, row=95)

        Label(self).grid(column=1, row=96)
        
        Radiobutton(self, text="Override Speed", variable=self._use_cure_speed, value=True,).grid(column=0, row=97, sticky=N+S+E+W)
        Radiobutton(self, text="Use Source Speed ", variable=self._use_cure_speed, value=False,).grid(column=1, row=97, sticky=N+S+E+W)

        Label(self).grid(column=1, row=100)

        Button(self, text ="Save", command=self._save).grid(column=2, row=110, sticky=N+S+E)
        Button(self, text ="Back", command=self._back).grid(column=0, row=110, sticky=N+S+W)

        self.update()

    def _back(self):
        self.navigate(SetupUI, printer = self._current_printer)

    def _help(self):
        PopUp(self,'Help', help_text.cure_test_help)

    def _calculate(self):
        try:
            speed = self._configuration_api.get_speed_at_height(
                self._base_height.get(),
                self._total_height.get(),
                self._start_speed.get(),
                self._stop_speed.get(),
                self._best_height.get()
               )
            self._cure_speed.set(speed)

            self._save()
        except Exception as ex:
            tkMessageBox.showwarning("Error", ex.message)

    def _save(self):
        try:
            self._configuration_api.set_cure_rate_draw_speed(float(self._cure_speed.get()))
            self._configuration_api.set_cure_rate_use_draw_speed(True if self._use_cure_speed.get() == 1 else False)
            self._configuration_api.save()
            self.navigate(SetupUI)
        except Exception as ex:
            tkMessageBox.showwarning("Error", ex.message)

    def _start(self):
        try:
            self._configuration_api.set_cure_rate_base_height(float(self._base_height.get()))
            self._configuration_api.set_cure_rate_total_height(float(self._total_height.get()))
            self._configuration_api.set_cure_rate_start_speed(float(self._start_speed.get()))
            self._configuration_api.set_cure_rate_finish_speed(float(self._stop_speed.get()))
            self._configuration_api.save()

            cure_test = self._configuration_api.get_cure_test(
                self._base_height.get(),
                self._total_height.get(),
                self._start_speed.get(),
                self._stop_speed.get()
               )

            self.navigate(PrintStatusUI, layer_generator=cure_test, config=self._configuration_api.get_current_config(), calling_class = CureTestUI, printer = self._current_printer)
        except Exception as ex:
            tkMessageBox.showwarning("Error", ex.message)

    def close(self):
        pass


class TestPrintUI(PeachyFrame):

    def initialize(self):
        self.grid()
        self._current_printer = self.kwargs['printer']
        self._configuration_api = ConfigurationAPI(self._configuration_manager)
        self._configuration_api.load_printer(self._current_printer)
        self._test_print_api = TestPrintAPI()
        self._selected_print = StringVar()
        self._selected_print.set(self._test_print_api.test_print_names()[0])

        self._height = DoubleVar()
        self._height.set(20)
        self._width = DoubleVar()
        self._width.set(40)
        self._speed = DoubleVar()
        self._speed.set(self._configuration_api.get_cure_rate_draw_speed())
        self._layer_height = DoubleVar()
        self._layer_height.set(0.01)

        Label(self, text='Printer: ').grid(column=0, row=10)
        Label(self, text=self._configuration_api.current_printer()).grid(column=1, row=10)
        Button(self, text='?', command=self._help).grid(column=2, row=10, stick=N+E)

        Label(self).grid(column=1, row=15)

        self._cure_test_frame = LabelFrame(self, text="Test Print", padx=5, pady=5)
        self._cure_test_frame.grid(column=0, row=20, columnspan=3)

        Label(self._cure_test_frame, text="Print").grid(column=0, row=10)
        OptionMenu(self._cure_test_frame, self._selected_print, *self._test_print_api.test_print_names()).grid(column=1, row=10)

        Label(self._cure_test_frame, text="Height (mm)").grid(column=0, row=20)
        Entry(self._cure_test_frame, textvariable=self._height).grid(column=1, row=20)

        Label(self._cure_test_frame, text="Width (mm)").grid(column=0, row=30)
        Entry(self._cure_test_frame, textvariable=self._width).grid(column=1, row=30)

        Label(self._cure_test_frame, text="Speed (mm)").grid(column=0, row=40)
        Entry(self._cure_test_frame, textvariable=self._speed).grid(column=1, row=40)

        Label(self._cure_test_frame, text="Layer Height (mm)").grid(column=0, row=50)
        Entry(self._cure_test_frame, textvariable=self._layer_height).grid(column=1, row=50)
        Label(self._cure_test_frame).grid(column=1, row=60)

        Button(self._cure_test_frame, text="Run", command=self._start).grid(column=1, row=70, sticky=N+E+S)
        Label(self._cure_test_frame).grid(column=1, row=80)

        Label(self).grid(column=1, row=100)

        Button(self, text="Back", command=self._back).grid(column=0, row=110, sticky=N+S+W)

        self.update()

    def _back(self):
        self.navigate(SetupUI, printer=self._current_printer)

    def _help(self):
        PopUp(self, 'Help', "Help is unavailable on this topic at this time.")

    def _start(self):
        try:
            layers = self._test_print_api.get_test_print(
                self._selected_print.get(),
                self._height.get(),
                self._width.get(),
                self._layer_height.get(),
                self._speed.get()
            )
            print(dir(layers))
            self.navigate(PrintStatusUI, layer_generator=layers, config=self._configuration_api.get_current_config(), calling_class=TestPrintUI, printer=self._current_printer)
        except Exception as ex:
            tkMessageBox.showwarning("Error", ex.message)

    def close(self):
        pass
