import Tkinter
from infrastructure.drip_based_zaxis import DripBasedZAxis
from api.drip_calibration import DripCalibrationAPI

class FieldValidations(object):
    def validate_int_command(self):
        return (self.register(self.validate_int), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

    def validate_int(self, action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
        if value_if_allowed == '' or value_if_allowed == None:
            return True
        elif text in '0123456789':
            try:
                int(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False

class DripCalibrationUI(Tkinter.Frame, FieldValidations):
    update_drips_job = None

    def __init__(self,parent):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.__drip_detector = DripBasedZAxis(1)
        self._drip_api = DripCalibrationAPI(self.__drip_detector)
        self.__drip_detector.start()
        self.drips = 0
        self.initialize()
        self.update_drips()

    def initialize(self):
        

        self.grid()
        
        self.instructions = u"Some much better text and instructions go here"
        instructions_label = Tkinter.Label(self,text=self.instructions, anchor="w",fg="pink",bg="green")
        instructions_label.grid(column=0,row=0,columnspan=4,sticky='EW')

        self.drip_count_label = Tkinter.StringVar()
        label = Tkinter.Label(self,textvariable=self.drip_count_label, anchor="w",fg="black",bg="white")
        label.grid(column=1,row=1,columnspan=2,sticky='EW')
        self.drip_count_label.set(str(self._drip_api.get_drips()))
        
        reset_button = Tkinter.Button(self,text=u"Reset Counter", command=self.reset_button_clicked)
        reset_button.grid(column=2,row=1)   

        height_mm_label = Tkinter.Label(self,text="End Height in Millimeters", anchor="w",fg="black",bg="white", justify="right")
        height_mm_label.grid(column=0,row=2,columnspan=1,sticky='EW')

        self.height_mm_entry = Tkinter.Entry(self, width=20, justify="left", text=str(10), validate = 'key', validatecommand=self.validate_int_command())
        self.height_mm_entry.grid(column=1,row=2)

        self.drips_per_mm_label_text = Tkinter.StringVar()
        drips_per_mm_label = Tkinter.Label(self,textvariable=self.drips_per_mm_label_text, anchor="w",fg="black",bg="white")
        drips_per_mm_label.grid(column=2,row=3,columnspan=1,sticky='EW')
        self.drips_per_mm_label_text.set("Booya")

        mark_button = Tkinter.Button(self,text=u"Mark", command=self.mark_button_clicked)
        mark_button.grid(column=2,row=2) 

        quit_button = Tkinter.Button(self,text=u"Save", command=self.close_button_clicked)
        quit_button.grid(column=3,row=4)    
       
        self.grid_columnconfigure(3,weight=1)
        self.update()

    def update_drips(self):
        if self.update_drips_job:
            self.after_cancel(self.update_drips_job)
            self.update_drips_job = None
        self.drips = self._drip_api.get_drips()
        self.drip_count_label.set("Drips: %d" % self.drips)
        self.update_drips_job=self.after(250, self.update_drips)

    def reset_button_clicked(self):
        self._drip_api.reset_drips()
        self.update_drips()

    def close_button_clicked(self):
        self.close()
        self.parent.start_main_window()

    def mark_button_clicked(self):
        if self.update_drips_job:
            self.after_cancel(self.update_drips_job)
        if self.height_mm_entry.get():
            drips_per_mm = self.drips * 1.0 / int(self.height_mm_entry.getint()) * 1.0
            print(drips_per_mm)
            self.drips_per_mm_label_text.set(str(drips_per_mm))

    def close(self):
        self.__drip_detector.stop()
        