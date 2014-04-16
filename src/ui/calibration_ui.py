from Tkinter import *
import tkMessageBox
from ui.ui_tools import *
from ui.main_ui import MainUI
from api.calibration_api import CalibrationAPI


class CalibrationUI(PeachyFrame):

    def initialize(self):
        self._index = 0
        self._points = [[0.0,0.0,0.0],[1.0,1.0,0.0],[1.0,-1.0,0.0],[-1.0,-1.0,0.0],[-1.0,1.0,0.0]]
        self.grid()
        printer_selection_current = StringVar()
        self._current_xy = StringVar()

        self._calibrationAPI = CalibrationAPI(self._configuration_api.get_current_config())
        self._calibrationAPI.start()

        show_centre_button = Button(self, text="Show Center Point", command=self.show_centre_click)
        show_centre_button.grid(column=1,row=1)

        show_line_button = Button(self, text="Show Line", command=self.show_line_click)
        show_line_button.grid(column=1,row=2)

        next_button = Button(self,text=u"Next Point", command=self.next_click)
        next_button.grid(column=2,row=4)

        label = Label(self,textvariable=self._current_xy)
        label.grid(column=1,row=4)

        button = Button(self,text=u"Back", command=self._back_button_click)
        button.grid(column=3,row=5)

        self.grid_columnconfigure(1,weight=1)
        self.update()

    def next_click(self):
        next_xyz = self._points[self._index]
        self._current_xy.set("X: %.2f, Y: %.2f" % (next_xyz[0],next_xyz[1]))
        self._calibrationAPI.move_to(next_xyz)
        self._index = self._index + 1
        if self._index > len(self._points) - 1:
            self._index = 0

    def show_centre_click(self):
        self._calibrationAPI.move_to([0,0,0])

    def show_line_click(self):
        pass

    def _back_button_click(self):
        from ui.configuration_ui import SetupUI
        self.navigate(SetupUI)

    def close(self):
        self._calibrationAPI.stop()
