from Tkinter import *
import ScrolledText
import tkMessageBox
import logging
import sys
import re

class RylanSpinbox(Spinbox):
    def __init__(self, parent, 
            to = None, 
            from_ = None, 
            command = None, 
            textvariable = None, 
            increment= 1.0,
            **kwargs):
        self.root = self.find_root(parent)

        self._mouse_command = command
        self._mouse_variable = textvariable
        self._to = to
        self._frm = from_
        self._increment = increment
        Spinbox.__init__(self, parent, 
            to =  self._to, 
            from_ = self._frm, 
            command = command, 
            textvariable = textvariable, 
            increment= self._increment,
            **kwargs)
        self.bind('<FocusIn>', self.on_focus)
        self.bind('<FocusOut>', self.off_focus)
        
    def find_root(self,start):
        if hasattr(start,'parent') and start.parent != None:
            return self.find_root(start.parent)
        elif hasattr(start, 'master') and start.master != None:
            return self.find_root(start.master)
        else:
            return start

    def on_focus(self,event = None):
        self.root.bind("<MouseWheel>", self.mouse_wheel)
        self.root.bind("<Button-4>", self.mouse_wheel)
        self.root.bind("<Button-5>", self.mouse_wheel)

    def off_focus(self,event = None):
        self.root.unbind("<MouseWheel>")
        self.root.unbind("<Button-4>")
        self.root.unbind("<Button-5>")

    def mouse_wheel(self,event):
        if event.num == 5 or event.delta == -120:
            if self._frm != None and self._mouse_variable.get() > self._frm:
                    self._mouse_variable.set(self._mouse_variable.get() - self._increment )
        if event.num == 4 or event.delta == 120:
            if self._to != None and self._mouse_variable.get() < self._to:
                self._mouse_variable.set(self._mouse_variable.get() + self._increment)
        self._mouse_command()

class UIHelpers(object):
    def strip_margin(self, text):
        return re.sub('\n[ \t]*\|', '\n', text)

class PopUp():
    def __init__(self,parent,title,text):
        tl = Toplevel()
        tl.title(title)
        tl.geometry('500x500')
        text_window = ScrolledText.ScrolledText(tl, wrap=WORD, height=50 )
        text_window.tag_configure("center", justify='center')
        text_window.tag_add("center", 1.0, "end")
        text_window.insert(INSERT, text)
        # text_window.tag_add("bold", "1.1", "1.20")
        text_window.pack()
        tl.focus_force()


class PeachyFrame(Frame):
    def __init__(self, parent, configuration_manager, **kwargs):
        logging.info("Peachy Frame kwargs: %s" % kwargs)
        Frame.__init__(self, parent)
        self.config(padx = 5, pady =5)
        self.parent = parent
        self.kwargs = kwargs
        self.parent.protocol("WM_DELETE_WINDOW", self.quit)
        self._configuration_manager = configuration_manager
        try:
            self.initialize()
        except Exception as ex:
            logging.error(ex)
            tkMessageBox.showwarning( "Error",ex)
            raise ex

    def navigate(self, next_frame , **kwargs):
        self.close()
        self.destroy()
        self.parent.current_frame = next_frame(self.parent, self._configuration_manager, **kwargs) 

    def close(self):
        pass

    def quit(self):
        self.close()
        sys.exit(0)

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