# -*- coding: iso-8859-1 -*-

from Tkinter import *
from ui.ui_tools import *
from ui.main_ui import MainUI
from api.print_api import PrintAPI
from api.configuration_api import ConfigurationAPI

class LicenceUI(PeachyFrame):
    licence = '''Copyright 2014 Peachy Printer INC.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.'''

    def initialize(self):
        self.grid()

        scrollbar = Scrollbar(self, orient=VERTICAL)
        scrollbar.grid(column=1, sticky=N+S)

        text = Text(self, yscrollcommand=scrollbar.set, width =110, height=36, wrap =WORD)
        text.insert(INSERT, self.licence)
        text.grid(column=0, row=0, sticky=N+S+E+W)

        scrollbar.config(command=text.yview)
        button = Button(self,text=u"Back", command=self._back)
        button.grid(column=0,row=1, sticky=N+W)
        self.columnconfigure(0, weight=1)

        self.update()

    def _back(self):
        self.navigate(MainUI)

    def close(self):
        pass
