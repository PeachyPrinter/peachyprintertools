from Tkinter import *
import tkMessageBox
from ui.ui_tools import *
from ui.main_ui import MainUI
from api.calibration_api import CalibrationAPI
import numpy as np
import help_text
from config import devmode

class CalibrationPoint(object):
    def __init__(self,ref_x,ref_y,ref_z,actual_x,actual_y,actual_z):
        self.ref_x = DoubleVar()
        self.ref_x.set(ref_x)
        self.ref_y = DoubleVar()
        self.ref_y.set(ref_y)
        self.ref_z = DoubleVar()
        self.ref_z.set(ref_z)

        self.actual_x = DoubleVar()
        self.actual_x.set(actual_x)
        self.actual_y = DoubleVar()
        self.actual_y.set(actual_y)
        self.actual_z = DoubleVar()
        self.actual_z.set(actual_z)

    @property
    def ref_xyz_float(self):
        return [float(self.ref_x.get()),float(self.ref_y.get()),float(self.ref_z.get())]

    @property
    def actual_xyz_float(self):
        return  [float(self.actual_x.get()),float(self.actual_y.get()),float(self.actual_z.get())]


class CalibrationUI(PeachyFrame, FieldValidations, UIHelpers):

    def initialize(self):
        self._printer = self.kwargs['printer']
        self._zero = [0.5,0.5,0.0]
        self._calibrationAPI = CalibrationAPI(self._configuration_manager,self._printer )
        self._current_selection = StringVar()
        self._current_selection.set('Center Point')
        
        self.grid()

        Label(self, text = 'Printer: ').grid(column=1,row=5)
        Label(self, text = self._printer, width=30 ).grid(column=2,row=5)
        Button(self, text='?', command=self._help).grid(column=3, row=5,stick=N+E)

        Label(self).grid(column=1,row=7)

        Radiobutton(self, command = self._option_changed, text="Center Point", variable=self._current_selection, value='Center Point').grid(column = 1, row = 20, sticky=W)
        Radiobutton(self, command = self._option_changed, text="Alignment", variable=self._current_selection, value='Alignment').grid(column = 1, row = 30, sticky=W)
        Radiobutton(self, command = self._option_changed, text="Scale", variable=self._current_selection, value='Scale').grid(column = 1, row = 40,sticky=W)
        Radiobutton(self, command = self._option_changed, text="Offset", variable=self._current_selection, value='Offset').grid(column = 1, row = 50,sticky=W)
        Radiobutton(self, command = self._option_changed, text="Calibrate",  variable=self._current_selection, value='Calibrate').grid(column = 1, row = 60, sticky=W)
        Radiobutton(self, command = self._option_changed, text="Calibrated Patterns", variable=self._current_selection, value='Calibrated Patterns').grid(column = 1, row = 70, sticky=W)

        self.scale_frame = LabelFrame(self, text="Scale", padx=5, pady =5)
        self.scale_frame.grid(column =1 , row = 45, columnspan=4,sticky=N+S+E+W)
        self.scale_frame.grid_remove()
        self._setup_scale_grid(self.scale_frame)

        self.offset_frame = LabelFrame(self, text="Offset", padx=5, pady =5)
        self.offset_frame.grid(column =1 , row = 55, columnspan=4,sticky=N+S+E+W)
        self.offset_frame.grid_remove()
        self._setup_offset_grid(self.offset_frame)

        self.calibration_frame = LabelFrame(self,text="Calibration", padx=5, pady=5)
        self.calibration_frame.grid(column=1,row=65,columnspan=4,sticky=N+S+E+W)
        self.calibration_frame.grid_remove()
        self._setup_calibration_grid(self.calibration_frame)

        self.pattern_frame = LabelFrame(self, text="Patterns", padx=5, pady =5)
        self.pattern_frame.grid(column =1 , row = 75, columnspan=4,sticky=N+S+E+W)
        self.pattern_frame.grid_remove()
        self._setup_patterns_grid(self.pattern_frame)

        Label(self).grid(column=1,row=80)
        Button(self,text=u"Back", command=self._back_button_click).grid(column=1,row=90, sticky=N+S+W)

        self._option_changed()
        self.update()

    def _setup_scale_grid(self,frame):
        self._scale_value = IntVar()
        self._scale_value.set(int(self._calibrationAPI.get_max_deflection() * 100.0))

        self._scale_setting = RylanSpinbox(frame, width= 4,from_=1, to=75, command =self._scale_changed, textvariable=self._scale_value)
        self._scale_setting.bind('<Return>', self._scale_changed)
        self._scale_setting.grid(column=1, row=10,sticky=W)

    def _setup_offset_grid(self,frame):
        self._x_offset_value = IntVar()
        self._x_offset_value.set(self._calibrationAPI.get_laser_offset()[0] * 1000.0)
        self._y_offset_value = IntVar()
        self._y_offset_value.set(self._calibrationAPI.get_laser_offset()[1] * 1000.0)

        Label(frame, text="X Axis Offset").grid(column=1, row=10,sticky=W)
        self._x_offset_setting = RylanSpinbox(frame, width = 6, from_=-1000, to=1000, command = self._offset_changed, textvariable=self._x_offset_value)
        self._x_offset_setting.grid(column=2, row=10,sticky=W)
        self._x_offset_setting.bind('<Return>', self._offset_changed)

        Label(frame, text="Y Axis Offset").grid(column=1, row=20,sticky=W)
        self._y_offset_setting = RylanSpinbox(frame, width = 6, from_=-1000, to=1000, command =self._offset_changed, textvariable=self._y_offset_value)
        self._y_offset_setting.grid(column=2, row=20,sticky=W)
        self._y_offset_setting.bind('<Return>', self._offset_changed)

    def _setup_patterns_grid(self, frame):
        self._test_speed = DoubleVar()
        self._test_speed.set(100.0)
        self._test_patterns = self._calibrationAPI.get_test_patterns()
        self._current_pattern = StringVar()
        self._current_pattern.set(self._test_patterns[0])
        self._laser_off_override = BooleanVar()
        self._laser_off_override.set(False)

        self.pattern_options = OptionMenu(frame, self._current_pattern, *self._test_patterns, command = self._pattern_changed)
        self.pattern_options.grid(column=1,row=10,sticky=W)
        Label(frame, text ="Speed mm/second").grid(column=1, row = 20, sticky=N+S+W)
        self.pattern_speed_spin = RylanSpinbox(frame, width= 6, from_= 25, to = 8000, increment=5, command = self._speed_changed, textvariable=self._test_speed)
        self.pattern_speed_spin.grid(column=2,row=20,sticky=W+S)
        Scale(frame, from_=25, to = 8000, orient=HORIZONTAL,variable = self._test_speed, length=300, command=self._speed_changed).grid(column=3,row=20)
        if devmode:
            Label(frame, text="Force Laser Off",background="#FF9966").grid(column=1,row=25,sticky=N+S+E+W)
            Checkbutton(frame, variable=self._laser_off_override, background="#FF9966", command= self._set_laser_off_override ).grid(column=2,row=25,sticky=N+S+E+W)


    def _setup_calibration_grid(self, frame):
        options = {'borderwidth':2 }
        self.data_points = []
        data = self._calibrationAPI.current_calibration()

        for ((rx,ry),(ax,ay)) in data.upper_points.items():
            self.data_points.append(CalibrationPoint(rx,ry,data.height,ax,ay,data.height))
        for ((rx,ry),(ax,ay)) in data.lower_points.items():
            self.data_points.append(CalibrationPoint(rx,ry,0.0,ax,ay,0.0))

        self.calibration_fields = {}
        self.upper_z = DoubleVar()
        self.upper_z.set(data.height)

        self.calibration_fields['r_z_h'] = Label(frame,text="Upper Calibration Height (mm)" ,**options )
        self.calibration_fields['r_z_h'].grid(column=1,row=10,columnspan=2)
        self.calibration_fields['a_z'] = Entry(frame, 
                validate = 'key', validatecommand=self.validate_float_command(), 
                textvariable=self.upper_z, width=8 ,**options)
        self.calibration_fields['a_z'].grid(column=3,row=10)
        self.calibration_fields['a_z'].bind('<FocusOut>', self._upper_z_change)
        self.calibration_fields['a_z'].bind('<KeyRelease>', self._upper_z_change)

        Label(self).grid(column=0, row=20)

        self.calibration_fields['a_x_h'] = Label(frame,text="Actual X (mm)",**options)
        self.calibration_fields['a_x_h'].grid(column=1,row=30)
        self.calibration_fields['a_y_h'] = Label(frame,text="Actual Y (mm)",**options)
        self.calibration_fields['a_y_h'].grid(column=2,row=30)
        self.calibration_fields['a_z_h'] = Label(frame,text="Actual Z (mm)",**options)
        self.calibration_fields['a_z_h'].grid(column=3,row=30)

        start_row = 40
        for index in range(0,len(self.data_points)):
            current_row = start_row + index * 2
            if (index == len(self.data_points) / 2):
                Label(frame).grid(column=1,row=current_row-1)
            
            self.calibration_fields['a_x_%s' % index] = Entry(frame, 
                validate = 'key', validatecommand=self.validate_float_command(), 
                textvariable=self.data_points[index].actual_x, width=8 ,**options)
            self.calibration_fields['a_x_%s' % index].grid(column=1,row=current_row)
            self.calibration_fields['a_x_%s' % index].bind('<FocusIn>', 
                lambda event, point=self.data_points[index]: 
                    self._point_change(point))
            self.calibration_fields['a_y_%s' % index] = Entry(frame,
                validate = 'key', validatecommand=self.validate_float_command(), 
                textvariable=self.data_points[index].actual_y, width=8 ,**options)
            self.calibration_fields['a_y_%s' % index].grid(column=2,row=current_row)
            self.calibration_fields['a_y_%s' % index].bind('<FocusIn>', 
                lambda event, point=self.data_points[index]:
                    self._point_change(point))
            self.calibration_fields['r_z_%s' % index] = Label(self.calibration_frame,textvariable=self.data_points[index].ref_z, width=8 ,**options)
            self.calibration_fields['r_z_%s' % index].grid(column=3,row=current_row)

        self.save_button = Button(frame,text=u"Save", command=self._save_click,**options)
        self.save_button.grid(column=4,row=(start_row + len(self.data_points) * 2 + 10))

    def _point_change(self,data):
        self._calibrationAPI.show_point(data.ref_xyz_float)

    def _help(self):
        PopUp(self,'Help', help_text.calibration_help)

    def _upper_z_change(self,field):
        if self.upper_z.get() > 0.0:
            for point in self.data_points:
                if point.ref_z.get() > 0.0:
                    point.ref_z.set(self.upper_z.get())
                    point.actual_z.set(self.upper_z.get())
        else:
            self.upper_z.set(1.0)
            tkMessageBox.showwarning(
            'Dang!',
            '"Upper Calibration Height" must be a postive value in mm'
            )
            self._upper_z_change(None)

    def _pattern_changed(self, pattern):
        self._calibrationAPI.show_test_pattern(pattern)

    def _scale_changed(self, event = None):
        scale = self._scale_value.get()
        self._calibrationAPI.set_max_deflection( scale / 100.0 )

    def _offset_changed(self, event = None):
        offset = [ self._x_offset_value.get() / 1000.0 , self._y_offset_value.get() / 1000.0 ]
        self._calibrationAPI.set_laser_offset(offset)

    def _speed_changed(self, event= None):
        self._calibrationAPI.set_test_pattern_speed(self._test_speed.get())

    def _set_laser_off_override(self):
        self._calibrationAPI.set_laser_off_override(self._laser_off_override.get())

    def _option_changed(self):
        self.pattern_frame.grid_remove()
        self.scale_frame.grid_remove()
        self.calibration_frame.grid_remove()
        self.offset_frame.grid_remove()
        
        if self._current_selection.get() == 'Center Point':
            self._calibrationAPI.show_point(self._zero)
        elif self._current_selection.get() == 'Alignment':
            self._calibrationAPI.show_line()
        elif self._current_selection.get() == 'Calibrate':
            self.calibration_frame.grid()
            self._calibrationAPI.show_point(self._zero)
        elif self._current_selection.get() == 'Calibrated Patterns':
            self.pattern_frame.grid()
            self._pattern_changed(self._current_pattern.get())
        elif self._current_selection.get() == 'Scale':
            self.scale_frame.grid()
            self._calibrationAPI.show_scale()
        elif self._current_selection.get() == 'Offset':
            self.offset_frame.grid()
            self._calibrationAPI.show_blink()
        else:
            raise Exception("Programmer Error")


    def _save_click(self):
        height = self.upper_z.get()
        lower_points = dict([ ((float(point.ref_x.get()),float(point.ref_y.get())),(float(point.actual_x.get()),float(point.actual_y.get()))) for point in self.data_points if point.ref_z.get() == 0.0 ])
        upper_points = dict([ ((float(point.ref_x.get()),float(point.ref_y.get())),(float(point.actual_x.get()),float(point.actual_y.get()))) for point in self.data_points if point.ref_z.get() == self.upper_z.get() ])

        self._calibrationAPI.save_points(height,lower_points,upper_points)

    def _back_button_click(self):
        from ui.configuration_ui import SetupUI
        self.navigate(SetupUI)

    def close(self):
        if hasattr(self, '_calibrationAPI') and self._calibrationAPI:
            try:
                self._calibrationAPI.stop()
            except:
                pass
