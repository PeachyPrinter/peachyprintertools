from Tkinter import *
import tkMessageBox
from ui.ui_tools import *
from ui.main_ui import MainUI
from api.calibration_api import CalibrationAPI
import numpy as np

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

class CalibrationUI(PeachyFrame, FieldValidations):

    def initialize(self):
        self._printer = self.kwargs['printer']
        self._zero = [0.5,0.5,0.0]
        self._calibrationAPI = CalibrationAPI(self._configuration_manager,self._printer )

        self._index = 0
        self._patterns = self._calibrationAPI.get_patterns()
        self.data_points = []
        self.parent.geometry("%dx%d" % (500,700))
        self.grid()

        instructions = '''Amazing Instructions'''
        Label(self,text = instructions, background='snow').grid(column=1, row=0, columnspan=6 )

        self._current_selection = IntVar()
        Radiobutton(self, command = self._option_changed, text="Center Point", variable=self._current_selection, value=0).grid(column = 1, row = 1, sticky=W)
        Radiobutton(self, command = self._option_changed, text="Alignment", variable=self._current_selection, value=1).grid(column = 1, row = 2, sticky=W)
        Radiobutton(self, command = self._option_changed, text="Calibrate",  variable=self._current_selection, value=2).grid(column = 1, row = 3, sticky=W)
        Radiobutton(self, command = self._option_changed, text="Calibrated Patterns", variable=self._current_selection, value=3).grid(column = 1, row = 4, sticky=W)


        self._current_pattern = StringVar()
        self._current_pattern.set(self._patterns[0])
        
        self.pattern_options = OptionMenu(self, self._current_pattern, *self._patterns, command = self._pattern_changed)
        self.pattern_options.grid(column=2,row=4,sticky=W)
        
        self._setup_calibration_grid()

        Button(self,text=u"Back", command=self._back_button_click).grid(column=1,row=100)

        self._calibrationAPI.start()
        self._option_changed()
        self.update()

    def _setup_calibration_grid(self):
        options = {'borderwidth':2 }
        data = self._calibrationAPI.load()
        
        for ((rx,ry),(ax,ay)) in data['upper_points'].items():
            self.data_points.append(CalibrationPoint(rx,ry,data['height'],ax,ay,data['height']))
        for ((rx,ry),(ax,ay)) in data['lower_points'].items():
            self.data_points.append(CalibrationPoint(rx,ry,0.0,ax,ay,0.0))




        self.calibration_fields = {}
        self.upper_z = DoubleVar()
        self.upper_z.set(data['height'])

        self.calibration_fields['r_z_h'] = Label(self,text="Upper Calibration Height (mm)" ,**options )
        self.calibration_fields['r_z_h'].grid(column=1,row=50,columnspan=2)
        self.calibration_fields['a_z'] = Entry(self, 
                validate = 'key', validatecommand=self.validate_float_command(), 
                textvariable=self.upper_z, width=8 ,**options)
        self.calibration_fields['a_z'].grid(column=3,row=50)
        self.calibration_fields['a_z'].bind('<FocusOut>', self._upper_z_change)

        self.calibration_fields['r_x_h'] = Label(self,text="Calibration Point" ,**options )
        self.calibration_fields['r_x_h'].grid(column=1,row=60)

        self.calibration_fields['a_x_h'] = Label(self,text="Actual X (mm)",**options)
        self.calibration_fields['a_x_h'].grid(column=2,row=60)
        self.calibration_fields['a_y_h'] = Label(self,text="Actual Y (mm)",**options)
        self.calibration_fields['a_y_h'].grid(column=3,row=60)
        self.calibration_fields['a_z_h'] = Label(self,text="Actual Z (mm)",**options)
        self.calibration_fields['a_z_h'].grid(column=4,row=60)

        start_row = 70
        for index in range(0,len(self.data_points)):
            self.calibration_fields['r_x_%s' % index] = Label(self,text=str(index + 1), width=8 ,**options )
            self.calibration_fields['r_x_%s' % index].grid(column=1,row=start_row + index)
            self.calibration_fields['a_x_%s' % index] = Entry(self, 
                validate = 'key', validatecommand=self.validate_float_command(), 
                textvariable=self.data_points[index].actual_x, width=8 ,**options)
            self.calibration_fields['a_x_%s' % index].grid(column=2,row=start_row + index)
            self.calibration_fields['a_x_%s' % index].bind('<FocusIn>', 
                lambda event, point=self.data_points[index]: 
                    self._point_change(point))
            self.calibration_fields['a_y_%s' % index] = Entry(self,
                validate = 'key', validatecommand=self.validate_float_command(), 
                textvariable=self.data_points[index].actual_y, width=8 ,**options)
            self.calibration_fields['a_y_%s' % index].grid(column=3,row=start_row + index)
            self.calibration_fields['a_y_%s' % index].bind('<FocusIn>', 
                lambda event, point=self.data_points[index]:
                    self._point_change(point))
            self.calibration_fields['r_z_%s' % index] = Label(self,textvariable=self.data_points[index].ref_z, width=8 ,**options)
            self.calibration_fields['r_z_%s' % index].grid(column=4,row=start_row + index)


        self.save_button = Button(self,text=u"Save", command=self._save_click,**options)
        self.save_button.grid(column=4,row=(start_row + len(self.data_points) + 1))

    def _point_change(self,data):
        self._calibrationAPI.move_to(data.ref_xyz_float)

    def _hide_calibration(self):
        for (key,value) in self.calibration_fields.items():
            value.grid_remove()
        self.save_button.grid_remove()

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

    def _show_calibration(self):
        for key,value in self.calibration_fields.items():
            value.grid()
        self.save_button.grid()

    def _hide_patterns(self):
        self.pattern_options.grid_remove()

    def _show_patterns(self):
        self.pattern_options.grid()

    def _apply_calibration(self):
        self._calibrationAPI.apply_calibration()

    def _unapply_calibration(self):
        self._calibrationAPI.unapply_calibration()

    def _pattern_changed(self, pattern):
            self._calibrationAPI.change_pattern(pattern)

    def _option_changed(self):
        if self._current_selection.get() == 0:
            self._unapply_calibration()
            self._hide_patterns()
            self._hide_calibration()
            self._calibrationAPI.change_pattern('Single Point')
            self._calibrationAPI.move_to(self._zero)
        elif self._current_selection.get() == 1:
            self._unapply_calibration()
            self._hide_calibration()
            self._hide_patterns()
            self._pattern_changed('Grid Alignment Line')
        elif self._current_selection.get() == 2:
            self._hide_patterns()
            self._show_calibration()
            self._unapply_calibration()
            self._calibrationAPI.change_pattern('Single Point')
            self._calibrationAPI.move_to(self._zero)
        elif self._current_selection.get() == 3:
            self._show_patterns()
            self._hide_calibration()
            self._apply_calibration()
            self._pattern_changed('Grid Alignment Line')

        else:
            raise Exception("Programmer Error")


    def _save_click(self):
        config = {}
        config['height'] = self.upper_z.get()
        lower_points = [ ((float(point.ref_x.get()),float(point.ref_y.get())),(float(point.actual_x.get()),float(point.actual_y.get()))) for point in self.data_points if point.ref_z.get() == 0.0 ]
        upper_points = [ ((float(point.ref_x.get()),float(point.ref_y.get())),(float(point.actual_x.get()),float(point.actual_y.get()))) for point in self.data_points if point.ref_z.get() == self.upper_z.get() ]
        print(lower_points)
        print(upper_points)
        config['lower_points'] = dict(lower_points)
        config['upper_points'] = dict(upper_points)

        self._calibrationAPI.save(config)

    def _back_button_click(self):
        from ui.configuration_ui import SetupUI
        self.navigate(SetupUI)

    def close(self):
        if hasattr(self, '_calibrationAPI') and self._calibrationAPI:
            try:
                self._calibrationAPI.stop()
            except:
                pass
