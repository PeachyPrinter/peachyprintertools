from Tkinter import *

class PeachyFrame(Frame):
    def __init__(self,parent, configuration_api):
        Frame.__init__(self, parent)
        self.parent = parent
        self._configuration_api = configuration_api
        self.initialize()

    def navigate(self, next_frame ):
        self.close()
        self.destroy()
        self.parent.current_frame = next_frame(self.parent, self._configuration_api) 

    def close(self):
        pass