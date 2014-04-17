from Tkinter import *
import logging

class PeachyFrame(Frame):
    def __init__(self, parent, configuration_api, **kwargs):
        Frame.__init__(self, parent)
        self.parent = parent
        self.kwargs = kwargs
        self.parent.protocol("WM_DELETE_WINDOW", self.quit)
        self._configuration_api = configuration_api
        self.initialize()

    def navigate(self, next_frame , **kwargs):
        self.close()
        self.destroy()
        self.parent.current_frame = next_frame(self.parent, self._configuration_api, **kwargs) 

    def close(self):
        pass

    def quit(self):
        self.close()
        exit(0)

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

    def validate_float_command(self):
        return (self.register(self.validate_float), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

    def validate_float(self, action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
        if value_if_allowed == '' or value_if_allowed == None:
            return True
        elif text in '-.0123456789':
            try:
                if value_if_allowed != "-":
                    float(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False