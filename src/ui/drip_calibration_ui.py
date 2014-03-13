import Tkinter
from infrastructure.drip_based_zaxis import DripBasedZAxis
from api.drip_calibration import DripCalibrationAPI

class DripCalibrationUI(Tkinter.Frame):

    def __init__(self,parent):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.__drip_detector = DripBasedZAxis(1)
        self._drip_api = DripCalibrationAPI(self.__drip_detector)
        self.__drip_detector.start()
        self.initialize()
        self.update_drips()

    def initialize(self):
        self.grid()
        
        self.instructions_label_var = Tkinter.StringVar()
        instructions_label = Tkinter.Label(self,textvariable=self.instructions_label_var, anchor="w",fg="pink",bg="green")
        instructions_label.grid(column=0,row=0,columnspan=2,sticky='EW')
        self.instructions_label_var.set(u"Some much better text and instructions go here")

        self.drip_count_label = Tkinter.StringVar()
        label = Tkinter.Label(self,textvariable=self.drip_count_label, anchor="w",fg="black",bg="white")
        label.grid(column=1,row=1,columnspan=2,sticky='EW')
        self.drip_count_label.set(str(self._drip_api.get_drips()))
        
        reset_button = Tkinter.Button(self,text=u"Reset Counter", command=self.reset_button_clicked)
        reset_button.grid(column=2,row=1)   

        quit_button = Tkinter.Button(self,text=u"Quit", command=self.close_button_clicked)
        quit_button.grid(column=2,row=2)        
        
        self.grid_columnconfigure(3,weight=1)
        self.update()

    def update_drips(self):
        self.drip_count_label.set("Drips: %d" % self._drip_api.get_drips())
        self.id=self.after(100, self.update_drips)

    def reset_button_clicked(self):
        self._drip_api.reset_drips()

    def close_button_clicked(self):
        self.close()
        self.parent.start_main_window()

    def close(self):
        self.__drip_detector.stop()
        