import logging
import config
import argparse
import os
import sys

from api.configuration_api import ConfigurationAPI

import wx

class SettingsPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1,)
        parent.SendSizeEvent()
        # self.SetBackgroundColour(wx.GREEN)
        self.book = wx.Notebook(self)
        self.book.SetPadding((2,2))
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.book,2, wx.EXPAND | wx.ALL, 20) 
        self.SetSizer(sizer)

        self.SendSizeEvent()

        general = wx.Panel(self.book)
        audio = wx.Panel(self.book)
        dripper = wx.Panel(self.book)
        calibration = wx.Panel(self.book)
        curerate = wx.Panel(self.book)

        self.book.AddPage(general, '&General')
        self.book.AddPage(audio, '&Audio')
        self.book.AddPage(dripper, '&Dripper')
        self.book.AddPage(calibration, 'Cali&bration')
        self.book.AddPage(curerate, 'C&ure Rate')


class PeachyApp(wx.App):
    def __init__(self,path):
        wx.App.__init__(self, redirect=False)
        self.settings_panel = None

    def OnInit(self):
        self.frame = wx.Frame(None, -1, "Peachy Printer Tools", pos=(0,0),
                        style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        #self.frame.CreateStatusBar()

        menuBar = wx.MenuBar()

        #File
        file_menu = wx.Menu()
        item_print = wx.MenuItem(file_menu,2, "&Print...\tCtrl-P", "Print a Model")
        item_print.SetBitmap(wx.Bitmap(os.path.join('ui2','icons','draw.png')))
        file_menu.AppendItem(item_print)
        item_settings = wx.MenuItem(file_menu,3, "&Settings\tCtrl-S", "Edit printer settings")
        item_settings.SetBitmap(wx.Bitmap(os.path.join('ui2','icons','settings.png')))
        file_menu.AppendItem(item_settings)
        file_menu.AppendSeparator()
        item_exit_application = wx.MenuItem(file_menu,wx.ID_EXIT, "E&xit\tCtrl-Q", "Exit demo")
        item_exit_application.SetBitmap(wx.Bitmap(os.path.join('ui2','icons','exit.png')))
        file_menu.AppendItem(item_exit_application)
        
        self.Bind(wx.EVT_MENU, self.OnExitApp, item_exit_application)
        self.Bind(wx.EVT_MENU, self.open_settings, item_settings)
        self.Bind(wx.EVT_MENU, self.open_print, item_print)
        menuBar.Append(file_menu, "&File")

        #Help
        
        self.frame.SetMenuBar(menuBar)
        self.frame.Show(True)
        self.frame.Bind(wx.EVT_CLOSE, self.OnCloseFrame)
        self.frame.SetSize((800,600))

        frect = self.frame.GetRect()

        self.SetTopWindow(self.frame)

        return True

    def open_settings(self,evt):
        print('open_settings')
        if not self.settings_panel:
            self.settings_panel = SettingsPanel(self.frame)
        self.settings_panel.Show()
        self.frame.SendSizeEvent() #wx bug in panel creation 

    def open_print(self,evt):
        pass
        
    def OnExitApp(self, evt):
        self.frame.Close(True)

    def OnCloseFrame(self, evt):
        if hasattr(self, "window") and hasattr(self.window, "ShutdownDemo"):
            self.window.ShutdownDemo()
        evt.Skip()


def setup_logging(args):
    logfile = os.path.join(config.PEACHY_PATH,'peachyprinter.log' )
    if os.path.isfile(logfile):
        os.remove(logfile)
    logging_format = '%(levelname)s: %(asctime)s %(module)s - %(message)s'
    logging_level = getattr(logging, args.loglevel.upper(), "WARNING")
    if not isinstance(logging_level, int):
        raise ValueError('Invalid log level: %s' % args.loglevel)
    if args.console:
        logging.basicConfig(stream = sys.stdout,format=logging_format, level=logging_level)
    else:
        logging.basicConfig(filename = logfile ,format=logging_format, level=logging_level)

if __name__ == "__main__":
    if not os.path.exists(config.PEACHY_PATH):
        os.makedirs(config.PEACHY_PATH)

    parser = argparse.ArgumentParser("Configure and print with Peachy Printer")
    parser.add_argument('-l', '--log',     dest='loglevel', action='store',      required=False, default="WARNING", help="Enter the loglevel [DEBUG|INFO|WARNING|ERROR] default: WARNING" )
    parser.add_argument('-c', '--console', dest='console',  action='store_true', required=False, help="Logs to console not file" )
    parser.add_argument('-d', '--development', dest='devmode',  action='store_true', required=False, help="Enable Developer Testing Mode" )
    args, unknown = parser.parse_known_args()

    setup_logging(args)
    if args.devmode:
        config.devmode = True

    if getattr(sys, 'frozen', False):
        path = os.path.dirname(sys.executable)
    else:
        path = os.path.dirname(os.path.realpath(__file__))
    app = PeachyApp(path)
    app.MainLoop()