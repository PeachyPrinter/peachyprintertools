from Tkinter import *
import tkMessageBox
from ui.ui_tools import *
from ui.main_ui import MainUI
from ui.calibration_ui import *
from api.configuration_api import ConfigurationAPI
from print_ui import PrintStatusUI

class SetupUI(PeachyFrame):

    def initialize(self):
        self._configuration_api = ConfigurationAPI(self._configuration_manager)
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
        self.navigate(SetupUI)

    def close(self):
        pass

class SetupOptionsUI(PeachyFrame):
    def initialize(self):
        self.grid()
        self._current_printer = self.kwargs['printer']
        self._configuration_api = ConfigurationAPI(self._configuration_manager)
        self._configuration_api.load_printer(self._current_printer)

        self.laser_thickness_entry_text = StringVar()
        self.laser_thickness_entry_text.set(self._configuration_api.get_laser_thickness_mm())
        self.sublayer_height_entry_text = StringVar()
        self.sublayer_height_entry_text.set(self._configuration_api.get_sublayer_height_mm())

        Label(self, text = 'Printer: ').grid(column=0,row=10)
        Label(self, text = self._configuration_api.current_printer()).grid(column=1,row=10)

        Label(self).grid(column=1,row=15)

        Label(self, text = "Laser Thickness (mm)" ).grid(column=0,row=20)
        Entry(self, textvariable = self.laser_thickness_entry_text).grid(column=1, row=20)

        Label(self, text = "Sub Layer Height (mm)" ).grid(column=0,row=30)
        Entry(self, textvariable = self.sublayer_height_entry_text).grid(column=1, row=30)

        Label(self).grid(column=1,row=35)

        Button(self, text ="Back", command = self._back).grid(column=0,row=40,sticky=N+S+W)
        Button(self, text ="Save", command = self._save).grid(column=2,row=40,sticky=N+S+E)
        self.update()

    def _back(self):
        self.navigate(SetupUI)

    def _save(self):
        laser_thickness = self.laser_thickness_entry_text.get()
        sublayer_height = self.sublayer_height_entry_text.get()
        self._configuration_api.set_laser_thickness_mm(float(laser_thickness))
        self._configuration_api.set_sublayer_height_mm(float(sublayer_height))
        self.navigate(SetupUI)

    def close(self):
        pass

class DripCalibrationUI(PeachyFrame, FieldValidations):
    
    def initialize(self):
        self._current_printer = self.kwargs['printer']
        self._configuration_api = ConfigurationAPI(self._configuration_manager)
        self._configuration_api.load_printer(self._current_printer)

        self.update_drips_job = None
        self.drips = 0
        self._drip_count = IntVar()
        self.grid()

        self.drips_per_mm_field_text = DoubleVar()
        self.drips_per_mm_field_text.set(0.0)

        self._height_mm_entry = IntVar()
        self._height_mm_entry.set(10)

        Label(self, text = 'Printer: ').grid(column=0,row=0)
        Label(self, text = self._configuration_api.current_printer()).grid(column=1,row=0)
        
        self.instructions = u"Some much better text and instructions go here"
        Label(self,text=self.instructions, anchor="w",fg="black",bg="green").grid(column=0,row=10,columnspan=4)

        Label(self).grid(column=1,row=15)

        Label(self,text='Drips', anchor="w",fg="black",bg="white").grid(column=0,row=20,sticky=N+S+E+W)
        Label(self,textvariable=self._drip_count,  anchor="w",fg="black",bg="white").grid(column=1,row=20,sticky=N+S+E+W)
        Button(self,text=u"Reset Counter", command=self._reset).grid(column=2,row=20,sticky=N+S+E+W)

        Label(self,text="End Height in Millimeters", anchor="w",fg="black",bg="white", justify="right").grid(column=0,row=30,sticky=N+S+E+W)
        Entry(self, width=5, justify="left", textvariable=self._height_mm_entry, validate = 'key', validatecommand=self.validate_int_command()).grid(column=1,row=30,sticky=N+S+E+W)

        Label(self,text="Drips per mm", anchor="w",fg="black",bg="white", justify="right").grid(column=0,row=40,sticky=N+S+E+W)
        Label(self,textvariable=self.drips_per_mm_field_text, anchor="w",fg="black",bg="white").grid(column=1,row=40,sticky=N+S+E+W)
        Button(self,text=u"Mark", command=self._mark).grid(column=2,row=40,sticky=N+S+E+W)

        Label(self).grid(column=1,row=45)

        self._save_button = Button(self,text=u"Save", command=self._save, state=DISABLED)
        self._save_button.grid(column=2,row=50,sticky=NSEW) 
        Button(self,text=u"Back", command=self._back).grid(column=0,row=50,sticky=N+S+E+W)
        self._configuration_api.start_counting_drips(drip_call_back = self._drips_updated)
        self.update()

    def _drips_updated(self, drips, height):
        self._drip_count.set(drips)

    def _reset(self):
        self._configuration_api.reset_drips()

    def _back(self):
        self.navigate(SetupUI)

    def _mark(self):
        try:
            self._configuration_api.set_target_height(self._height_mm_entry.get())
            self._configuration_api.mark_drips_at_target()
            self.drips_per_mm_field_text.set(self._configuration_api.get_drips_per_mm())
            self._save_button.config(state = NORMAL)
        except Exception as ex:
            tkMessageBox.showwarning(
            "Error",
            ex.message
        )

    def _save(self):
        self._configuration_api.save()
        self.navigate(SetupUI)

    def close(self):
        self._configuration_api.stop_counting_drips()

class SetupAudioUI(PeachyFrame):

    def initialize(self):
        self.grid()
        self._current_printer = self.kwargs['printer']
        self._configuration_api = ConfigurationAPI(self._configuration_manager)
        self._configuration_api.load_printer(self._current_printer)

        audio_options = self._configuration_api.get_available_audio_options()

        self.input_options = audio_options['inputs']
        if (self.input_options < 1):
            logging.error("No inputs available")
            tkMessageBox.showwarning('Error','Audio card appears to have no inputs')
            self._back()

        self.input_audio_selection_current = StringVar()
        self.input_audio_selection_current.set(self.input_options.keys()[self._get_recommend_audio_index(self.input_options.keys())])

        self.output_options = audio_options['outputs']
        if (self.output_options < 1):
            logging.error("No outputs available")
            tkMessageBox.showwarning('Error','Audio card appears to have no outputs')
            self._back()

        self.output_audio_selection_current = StringVar()
        self.output_audio_selection_current.set(self.output_options.keys()[self._get_recommend_audio_index(self.output_options.keys())])
        
        Label(self, text = 'Printer: ').grid(column=0,row=0)
        Label(self, text = self._configuration_api.current_printer()).grid(column=1,row=0)

        Label(self).grid(column=0,row=20)
        
        Label(self, text = "Audio Input Settings" ).grid(column=0,row=30)
        OptionMenu( self, self.input_audio_selection_current, *self.input_options.keys()).grid(column=1,row=30,sticky=NSEW)

        Label(self, text = "Audio Output Settings" ).grid(column=0,row=40)
        OptionMenu(self, self.output_audio_selection_current, *self.output_options.keys()).grid(column=1,row=40,sticky=NSEW)

        Label(self).grid(column=0,row=50)

        Button(self, text ="Back", command = self._back).grid(column=0,row=60,sticky=N+S+W)
        Button(self, text ="Save", command = self._process).grid(column=1,row=60,sticky=N+S+E)

        self.update()

    def _get_recommend_audio_index(self, options):
        for i in range(0,len(options)):
            if options[i].endswith('(Recommended)'):
                return i
        return 0

    def _back(self):
        self.navigate(SetupUI)

    def _process(self):
        input_option = self.input_options[self.input_audio_selection_current.get()]
        output_option = self.output_options[self.output_audio_selection_current.get()]
        
        self._configuration_api.set_audio_input_options(input_option['sample_rate'],input_option['depth'])
        self._configuration_api.set_audio_output_options(output_option['sample_rate'],output_option['depth'])

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

        self._save_button = Button(self, text ="Save", command = self._save)
        self._save_button.grid(column=0,row=110,sticky=N+S+W)
        Button(self, text ="Back", command = self._back).grid(column=0,row=110,sticky=N+S+W)

        self.update()

    def _back(self):
        self.navigate(SetupUI)

    def _save(self):
        
        pass

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
            tkMessageBox.showwarning(
            "Error",
            ex.message
        )

    def close(self):
        pass