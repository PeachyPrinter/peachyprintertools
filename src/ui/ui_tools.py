from Tkinter import *

class PeachyFrame(Frame):
    def __init__(self, parent, configuration_api, **kwargs):
        Frame.__init__(self, parent)
        self.parent = parent
        self.kwargs = kwargs
        self._configuration_api = configuration_api
        self.initialize()

    def navigate(self, next_frame , **kwargs):
        self.close()
        self.destroy()
        self.parent.current_frame = next_frame(self.parent, self._configuration_api, **kwargs) 

    def close(self):
        pass