from Tkinter import *
import tkMessageBox
from ui.ui_tools import *
from ui.main_ui import MainUI
from api.calibration_api import CalibrationAPI

class CalibrationPoint(object):
    def __init__(self,ref_x,ref_y,ref_z):
        self.ref_x = DoubleVar()
        self.ref_x.set(ref_x)
        self.ref_y = DoubleVar()
        self.ref_y.set(ref_y)
        self.ref_z = DoubleVar()
        self.ref_z.set(ref_z)

        self.actual_x = DoubleVar()
        self.actual_x.set(0.0)
        self.actual_y = DoubleVar()
        self.actual_y.set(0.0)
        self.actual_z = DoubleVar()
        self.actual_z.set(ref_z)

class CalibrationUI(PeachyFrame):

    def initialize(self):
        self._index = 0
        self._points = [[0.0,0.0,0.0],[1.0,1.0,0.0],[1.0,-1.0,0.0],[-1.0,-1.0,0.0],[-1.0,1.0,0.0]]
        self.data_points = []
        self.grid()

        self._calibrationAPI = CalibrationAPI(self._configuration_api.get_current_config())
        self._calibrationAPI.start()

        show_centre_button = Button(self, text="Show Center Point", command=self.show_centre_click)
        show_centre_button.grid(column=1,row=1)

        show_line_button = Button(self, text="Show Line", command=self.show_line_click)
        show_line_button.grid(column=1,row=2)

        for x,y,z in self._points:
            self.data_points.append(CalibrationPoint(x,y,z))

        start_row = 4
        for index in range(0,len(self.data_points)):
            x_label = Label(self,textvariable=self.data_points[index].ref_x)
            x_label.grid(column=2,row=start_row + index)
            y_label = Label(self,textvariable=self.data_points[index].ref_y)
            y_label.grid(column=3,row=start_row + index)
            x_entry = Entry(self,textvariable=self.data_points[index].actual_x)
            x_entry.grid(column=4,row=start_row + index)
            y_entry = Entry(self,textvariable=self.data_points[index].actual_y)
            y_entry.grid(column=5,row=start_row + index)



        button = Button(self,text=u"Back", command=self._back_button_click)
        button.grid(column=5,row=50)

        button = Button(self,text=u"Save", command=self._save_click)
        button.grid(column=7,row=50)

        self._reference_x.set("%.2f" % 0.0)
        self._reference_y.set("%.2f" % 0.0)
        self.update()

    def save_click(self):
        next_xyz = self._points[self._index]
        self._reference_x.set("%.2f" % next_xyz[0])
        self._reference_y.set("%.2f" % next_xyz[1])
        self._calibrationAPI.move_to(next_xyz)
        self._index = self._index + 1
        if self._index > len(self._points) - 1:
            self._index = 0

    def show_centre_click(self):
        self._calibrationAPI.change_pattern('Single Point')
        self._reference_x.set("%.2f" % 0.0)
        self._reference_y.set("%.2f" % 0.0)
        self._calibrationAPI.move_to([0,0,0])

    def show_line_click(self):
        self._calibrationAPI.change_pattern('Grid Alignment Line')

    def _back_button_click(self):
        from ui.configuration_ui import SetupUI
        self.navigate(SetupUI)

    def close(self):
        self._calibrationAPI.stop()
