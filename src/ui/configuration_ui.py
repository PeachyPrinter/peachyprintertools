import Tkinter
from Tkinter import *

class SetupAudioUI(Frame):
    def __init__(self,parent, configuration_api):
        Frame.__init__(self, parent)
        self.parent = parent
        self._configuration_api = configuration_api
        self.initialize()

    def initialize(self):
        self.grid()
        audio_options = self._configuration_api.get_available_audio_options()

        input_label_text = StringVar()
        input_label_text.set("Audio Input Settings")
        input_label = Label(self, textvariable = input_label_text )
        input_label.grid(column=0,row=0)


        self.input_options = audio_options['inputs']
        self.input_audio_selection_current = Tkinter.StringVar()

        self.input_audio_selection_current.set(self.input_options.keys()[self._get_recommend_audio_index(self.input_options.keys())])
        input_audio_selection_menu = Tkinter.OptionMenu(
            self,
            self.input_audio_selection_current, 
            *self.input_options.keys())
        input_audio_selection_menu.grid(column=1,row=0)

        output_label_text = StringVar()
        output_label_text.set("Audio Output Settings")
        output_label = Label(self, textvariable = output_label_text )
        output_label.grid(column=0,row=1)

        self.output_options = audio_options['outputs']
        self.output_audio_selection_current = Tkinter.StringVar()
        self.output_audio_selection_current.set(self.output_options.keys()[self._get_recommend_audio_index(self.output_options.keys())])
        output_audio_selection_menu = Tkinter.OptionMenu(
            self,
            self.output_audio_selection_current, 
            *self.output_options.keys())
        output_audio_selection_menu.grid(column=1,row=1)

        button = Button(self, text ="Submit", command = self._process)
        button.grid(column=2,row=2)

        self.grid_columnconfigure(1,weight=1)
        self.update()

    def _get_recommend_audio_index(self, options):
        for i in range(0,len(options)):
            if options[i].endswith('(Recommended)'):
                return i
        return 0

    def _process(self):
        input_option = self.input_options[self.input_audio_selection_current.get()]
        output_option = self.output_options[self.output_audio_selection_current.get()]
        
        self._configuration_api.set_audio_input_options(input_option['sample_rate'],input_option['depth'])
        self._configuration_api.set_audio_output_options(output_option['sample_rate'],output_option['depth'])

        self.parent.start_main_window()

    def close(self):
        pass