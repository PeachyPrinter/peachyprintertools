from Tkinter import *
import tkMessageBox
from ui.ui_tools import *
from ui.main_ui import MainUI
from ui.calibration_ui import *

class SetupUI(PeachyFrame):

    def initialize(self):
        
        self.grid()
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

        add_printer_button = Button(self,text=u"Add Printer", command=self._add_printer)
        add_printer_button.grid(column=2,row=0)

        audio_setup_button = Button(self,text=u"Setup Audio", command=self.setup_audio_button_click)
        audio_setup_button.grid(column=1,row=1)

        options_setup_button = Button(self,text=u"Setup Options", command=self._setup_options_button_click)
        options_setup_button.grid(column=1,row=2)

        drip_calibration_button = Button(self,text=u"Start Drip Calibration", command=self.drip_calibration_button_click)
        drip_calibration_button.grid(column=1,row=3)

        calibration_button = Button(self,text=u"Start Calibration", command=self.start_calibration_button_click)
        calibration_button.grid(column=1,row=4)

        button = Button(self,text=u"Back", command=self._back_button_click)
        button.grid(column=3,row=5)

        self.grid_columnconfigure(1,weight=1)
        self.update()

    def _printer_selected(self, selection):
        self._configuration_api.load_printer(selection)

    def _add_printer(self):
        self.navigate(AddPrinterUI)

    def _setup_options_button_click(self):
        self.navigate(SetupOptionsUI)

    def drip_calibration_button_click(self):
        self.navigate(DripCalibrationUI)

    def _back_button_click(self):
        self.navigate(MainUI)

    def setup_audio_button_click(self):
        self.navigate(SetupAudioUI)

    def start_calibration_button_click(self):
        self.navigate(CalibrationUI)

    def close(self):
        pass

class AddPrinterUI(PeachyFrame):
    def initialize(self):
        self.grid()
        label = Label(self, text = "Enter a name for your printer" )
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
        self.navigate(SetupUI)

    def close(self):
        pass

class SetupOptionsUI(PeachyFrame):
    def initialize(self):
        self.grid()
        laser_thickness_label = Label(self, text = "Laser Thickness (mm)" )
        laser_thickness_label.grid(column=0,row=0)
        self.laser_thickness_entry_text = StringVar()
        self.laser_thickness_entry_text.set(self._configuration_api.get_laser_thickness_mm())
        self.laser_thickness_entry = Entry(self, textvariable = self.laser_thickness_entry_text)
        self.laser_thickness_entry.grid(column=1, row=0)

        sublayer_height_label = Label(self, text = "Sub Layer Height (mm)" )
        sublayer_height_label.grid(column=0,row=1)
        self.sublayer_height_entry_text = StringVar()
        self.sublayer_height_entry_text.set(self._configuration_api.get_sublayer_height_mm())
        self.sublayer_height_entry = Entry(self, textvariable = self.sublayer_height_entry_text)
        self.sublayer_height_entry.grid(column=1, row=1)

        button = Button(self, text ="Save", command = self._process)
        button.grid(column=2,row=2)
        self.grid_columnconfigure(1,weight=1)
        self.update()

    def _process(self):
        laser_thickness = self.laser_thickness_entry_text.get()
        sublayer_height = self.sublayer_height_entry_text.get()
        self._configuration_api.set_laser_thickness_mm(float(laser_thickness))
        self._configuration_api.set_sublayer_height_mm(float(sublayer_height))
        self.navigate(SetupUI)

    def close(self):
        pass

class DripCalibrationUI(PeachyFrame, FieldValidations):
    
    def initialize(self):
        self.update_drips_job = None
        self._configuration_api.start_counting_drips()
        self.drips = 0
        self.drip_count_label = StringVar()
        self.update_drips()
        self.grid()
        
        self.instructions = u"Some much better text and instructions go here"
        instructions_label = Label(self,text=self.instructions, anchor="w",fg="pink",bg="green")
        instructions_label.grid(column=0,row=0,columnspan=4,sticky='EW')

        label = Label(self,textvariable=self.drip_count_label, anchor="w",fg="black",bg="white")
        label.grid(column=1,row=1,columnspan=2,sticky='EW')
        
        
        reset_button = Button(self,text=u"Reset Counter", command=self.reset_button_clicked)
        reset_button.grid(column=2,row=1)   

        height_mm_label = Label(self,text="End Height in Millimeters", anchor="w",fg="black",bg="white", justify="right")
        height_mm_label.grid(column=0,row=2,columnspan=1,sticky='EW')

        self.height_mm_entry = Entry(self, width=20, justify="left", text=str(10), validate = 'key', validatecommand=self.validate_int_command())
        self.height_mm_entry.grid(column=1,row=2)

        drips_per_mm_label = Label(self,text="Drips per mm", anchor="w",fg="black",bg="white", justify="right")
        drips_per_mm_label.grid(column=0,row=3,columnspan=1,sticky='EW')

        self.drips_per_mm_field_text = StringVar()
        drips_per_mm_field = Label(self,textvariable=self.drips_per_mm_field_text, anchor="w",fg="black",bg="white")
        drips_per_mm_field.grid(column=1,row=3,columnspan=1,sticky='EW')
        self.drips_per_mm_field_text.set("")

        mark_button = Button(self,text=u"Mark", command=self.mark_button_clicked)
        mark_button.grid(column=2,row=2) 

        quit_button = Button(self,text=u"Back", command=self._back_button_clicked)
        quit_button.grid(column=3,row=4)    
       
        self.grid_columnconfigure(3,weight=1)
        self.update()

    def update_drips(self):
        if self.update_drips_job:
            self.after_cancel(self.update_drips_job)
            self.update_drips_job = None
        self.drips = self._configuration_api.get_drips()
        self.drip_count_label.set("Drips: %d" % self.drips)
        self.update_drips_job=self.after(250, self.update_drips)

    def reset_button_clicked(self):
        self._configuration_api.reset_drips()
        self.update_drips()

    def _back_button_clicked(self):
        self.navigate(SetupUI)

    def mark_button_clicked(self):
        try:
            self._configuration_api.set_target_height(self.height_mm_entry.get())
            self._configuration_api.mark_drips_at_target()
            self.drips_per_mm_field_text.set("%.2f" %self._configuration_api.get_drips_per_mm())
        except Exception as ex:
            tkMessageBox.showwarning(
            "Error",
            ex.message
        )

    def close(self):
        self._configuration_api.stop_counting_drips()

class SetupAudioUI(PeachyFrame):

    def initialize(self):
        self.grid()
        audio_options = self._configuration_api.get_available_audio_options()

        input_label_text = StringVar()
        input_label_text.set("Audio Input Settings")
        input_label = Label(self, textvariable = input_label_text )
        input_label.grid(column=0,row=0)


        self.input_options = audio_options['inputs']
        self.input_audio_selection_current = StringVar()

        self.input_audio_selection_current.set(self.input_options.keys()[self._get_recommend_audio_index(self.input_options.keys())])
        input_audio_selection_menu = OptionMenu(
            self,
            self.input_audio_selection_current, 
            *self.input_options.keys())
        input_audio_selection_menu.grid(column=1,row=0)

        output_label_text = StringVar()
        output_label_text.set("Audio Output Settings")
        output_label = Label(self, textvariable = output_label_text )
        output_label.grid(column=0,row=1)

        self.output_options = audio_options['outputs']
        self.output_audio_selection_current = StringVar()
        self.output_audio_selection_current.set(self.output_options.keys()[self._get_recommend_audio_index(self.output_options.keys())])
        output_audio_selection_menu = OptionMenu(
            self,
            self.output_audio_selection_current, 
            *self.output_options.keys())
        output_audio_selection_menu.grid(column=1,row=1)

        button = Button(self, text ="Submit", command = self._process)
        button.grid(column=2,row=2)

        self.grid_columnconfigure(1,weight=1)
        self.update()

    def _get_recommend_audio_index(self, options):
        for i in range(0,len(options)):
            if options[i].endswith('(Recommended)'):
                return i
        return 0

    def _process(self):
        input_option = self.input_options[self.input_audio_selection_current.get()]
        output_option = self.output_options[self.output_audio_selection_current.get()]
        
        self._configuration_api.set_audio_input_options(input_option['sample_rate'],input_option['depth'])
        self._configuration_api.set_audio_output_options(output_option['sample_rate'],output_option['depth'])

        self.navigate(SetupUI)

    def close(self):
        pass
