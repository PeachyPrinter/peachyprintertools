import wx
import sys
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLUT import *


class PeachyPrinterApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect=False)

    def OnInit(self):
        frame = wx.Frame(None, -1, "Peachy Printer Tools", pos=(0,0),style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame.CreateStatusBar()

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        item = menu.Append(wx.ID_EXIT, "E&xit\tCtrl-Q", "Exit")
        self.Bind(wx.EVT_MENU, self.OnExitApp, item)
        menuBar.Append(menu, "&File")
        
        frame.SetMenuBar(menuBar)
        frame.Show(True)
        frame.Bind(wx.EVT_CLOSE, self.OnCloseFrame)

        win = self.run(frame)


        # set the frame to a good size for showing the two buttons
        frame.SetMinSize((800,600))
        win.SetFocus()
        self.window = win
        # frect = frame.GetRect()

        self.SetTopWindow(frame)
        self.frame = frame
        return True

        
    def OnExitApp(self, evt):
        self.frame.Close(True)

    def OnCloseFrame(self, evt):
        if hasattr(self, "window") and hasattr(self.window, "ShutdownDemo"):
            self.window.ShutdownDemo()
        evt.Skip()

    def run(self,frame):
        win = PrintPreviewPanel(frame)
        return win

class PrintPreviewPanel(wx.Panel):
    def __init__(self,parent):
        buttonDefs = {
            'Print': wx.NewId(),
            'Back' : wx.NewId(),
        }

        wx.Panel.__init__(self, parent, -1)

        #Status
        file_name_label         = wx.StaticText(self, label='File:', style=wx.ALIGN_RIGHT)
        file_name_text          = wx.StaticText(self, label='somefile.gcode', style=wx.ALIGN_LEFT )
        layers_label            = wx.StaticText(self, label='Layers:', style=wx.ALIGN_RIGHT)
        layers_text             = wx.StaticText(self, label='2000', style=wx.ALIGN_LEFT )
        current_height_label    = wx.StaticText(self, label='Height(mm):', style=wx.ALIGN_RIGHT)
        current_height_text     = wx.StaticText(self, label='50', style=wx.ALIGN_LEFT )
        width_label             = wx.StaticText(self, label='Width(mm):', style=wx.ALIGN_RIGHT)
        width_text              = wx.StaticText(self, label='49', style=wx.ALIGN_LEFT )
        depth_label             = wx.StaticText(self, label='Depth(mm):', style=wx.ALIGN_RIGHT)
        depth_text              = wx.StaticText(self, label='52', style=wx.ALIGN_LEFT )
        processing_time_label   = wx.StaticText(self, label='Approximate Time:', style=wx.ALIGN_RIGHT)
        processing_time_text    = wx.StaticText(self, label='12:25:12', style=wx.ALIGN_LEFT )

        # opengl_window           = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        layer_scroll            = wx.Slider(self, value=0, minValue=0, maxValue=1, style=wx.SL_VERTICAL)
        
        button_back             = wx.Button(self, id = buttonDefs['Back'],  label = 'Back')
        button_print            = wx.Button(self, id = buttonDefs['Print'], label = 'Print')
        repeat_checkbox         = wx.CheckBox(self, id = -1, label = 'Draw selected layer with peachy printer')

        opengl_window = GLCanvas(self)
        opengl_window.SetMinSize((400, 400))
        # box.Add(c, 0, wx.ALIGN_RIGHT|wx.ALL, 15)

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        outergrid           = wx.FlexGridSizer(2, 1, 10, 10)
        outerbottom         = wx.FlexGridSizer(1, 2, 10, 10)
        outertop            = wx.FlexGridSizer(1, 2, 10, 10)
        innerleft           = wx.FlexGridSizer(2, 1, 10, 10)
        innerright          = wx.FlexGridSizer(2, 1, 10, 10)
        opengl              = wx.FlexGridSizer(1, 2, 0, 0)
        info_label          = wx.StaticBox(self, -1, label = "Information")
        info_box_wrap       = wx.StaticBoxSizer(info_label, wx.VERTICAL )
        info_box            = wx.FlexGridSizer(8, 2, 5, 5)

        options_label       = wx.StaticBox(self, -1, label = "Options")
        options_box_wrap    = wx.StaticBoxSizer(options_label, wx.VERTICAL )
        options_box         = wx.FlexGridSizer(8, 2, 5, 5)

        outergrid.AddMany([(outertop,1,wx.EXPAND),(outerbottom,1,wx.EXPAND)])
        outertop.AddMany([(innerleft,1,wx.EXPAND),(innerright,1,wx.EXPAND)])
        innerleft.AddMany([(info_box_wrap,1,wx.EXPAND),(options_box_wrap,1,wx.EXPAND)])
        innerright.AddMany([(opengl,1,wx.EXPAND),(repeat_checkbox,3,wx.EXPAND)])
        outerbottom.AddMany([(button_back,1,wx.LEFT),(button_print,1,wx.ALIGN_RIGHT)])
        opengl.AddMany([(opengl_window,1,wx.EXPAND),(layer_scroll,0,wx.EXPAND)])

        info_box_wrap.Add(info_box)
        info_box.AddMany([(file_name_label,0,wx.ALIGN_RIGHT),(file_name_text,0,wx.ALIGN_LEFT),(layers_label,0,wx.ALIGN_RIGHT),(layers_text,0,wx.ALIGN_LEFT),(current_height_label,0,wx.ALIGN_RIGHT),(current_height_text,0,wx.ALIGN_LEFT),(width_label,0,wx.ALIGN_RIGHT),(width_text,0,wx.ALIGN_LEFT),(depth_label,0,wx.ALIGN_RIGHT),(depth_text,0,wx.ALIGN_LEFT),(processing_time_label,0,wx.ALIGN_RIGHT),(processing_time_text,0,wx.ALIGN_LEFT),])

        options_box_wrap.Add(options_box)
        options_box.AddMany([])

        outergrid.AddGrowableRow(0, 1)
        outergrid.AddGrowableCol(0, 1)
        outertop.AddGrowableRow(0,1)
        outertop.AddGrowableCol(1,1)
        outerbottom.AddGrowableCol(0,1)
        innerleft.AddGrowableRow(0,1)
        innerleft.AddGrowableRow(1,1)
        innerright.AddGrowableRow(0,1)
        innerright.AddGrowableCol(0, 1)
        opengl.AddGrowableRow(0,1)
        opengl.AddGrowableCol(0,1)
        hbox.Add(outergrid, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        self.SetSizer(hbox)

class GLCanvas(glcanvas.GLCanvas):
    def __init__(self, parent):
        glcanvas.GLCanvas.__init__(self, parent, -1)
        self.init = False
        self.context = glcanvas.GLContext(self)
        
        # initial mouse position
        self.lastx = self.x = 30
        self.lasty = self.y = 30
        self.size = None
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)

    def OnEraseBackground(self, event):
        pass # Do nothing, to avoid flashing on MSW.

    def OnSize(self, event):
        wx.CallAfter(self.DoSetViewport)
        event.Skip()

    def DoSetViewport(self):
        size = self.size = self.GetClientSize()
        self.SetCurrent(self.context)
        glViewport(0, 0, size.width, size.height)
        
    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.SetCurrent(self.context)
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()

    def OnMouseDown(self, evt):
        self.CaptureMouse()
        self.x, self.y = self.lastx, self.lasty = evt.GetPosition()

    def OnMouseUp(self, evt):
        self.ReleaseMouse()

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            self.lastx, self.lasty = self.x, self.y
            self.x, self.y = evt.GetPosition()
            self.Refresh(False)

    def InitGL(self):
        # set viewing projection
        glMatrixMode(GL_PROJECTION)
        glFrustum(-0.5, 0.5, -0.5, 0.5, 1.0, 3.0)

        # position viewer
        glMatrixMode(GL_MODELVIEW)
        glTranslatef(0.0, 0.0, -2.0)

        # position object
        glRotatef(self.y, 1.0, 0.0, 0.0)
        glRotatef(self.x, 0.0, 1.0, 0.0)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

    def OnDraw(self):
        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # draw six faces of a cube
        glBegin(GL_QUADS)
        glNormal3f( 0.0, 0.0, 1.0)
        glVertex3f( 0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5,-0.5, 0.5)
        glVertex3f( 0.5,-0.5, 0.5)

        glNormal3f( 0.0, 0.0,-1.0)
        glVertex3f(-0.5,-0.5,-0.5)
        glVertex3f(-0.5, 0.5,-0.5)
        glVertex3f( 0.5, 0.5,-0.5)
        glVertex3f( 0.5,-0.5,-0.5)

        glNormal3f( 0.0, 1.0, 0.0)
        glVertex3f( 0.5, 0.5, 0.5)
        glVertex3f( 0.5, 0.5,-0.5)
        glVertex3f(-0.5, 0.5,-0.5)
        glVertex3f(-0.5, 0.5, 0.5)

        glNormal3f( 0.0,-1.0, 0.0)
        glVertex3f(-0.5,-0.5,-0.5)
        glVertex3f( 0.5,-0.5,-0.5)
        glVertex3f( 0.5,-0.5, 0.5)
        glVertex3f(-0.5,-0.5, 0.5)

        glNormal3f( 1.0, 0.0, 0.0)
        glVertex3f( 0.5, 0.5, 0.5)
        glVertex3f( 0.5,-0.5, 0.5)
        glVertex3f( 0.5,-0.5,-0.5)
        glVertex3f( 0.5, 0.5,-0.5)

        glNormal3f(-1.0, 0.0, 0.0)
        glVertex3f(-0.5,-0.5,-0.5)
        glVertex3f(-0.5,-0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5,-0.5)
        glEnd()

        if self.size is None:
            self.size = self.GetClientSize()
        w, h = self.size
        w = max(w, 1.0)
        h = max(h, 1.0)
        xScale = 180.0 / w
        yScale = 180.0 / h
        glRotatef((self.y - self.lasty) * yScale, 1.0, 0.0, 0.0);
        glRotatef((self.x - self.lastx) * xScale, 0.0, 1.0, 0.0);

        self.SwapBuffers()

app = PeachyPrinterApp()
app.MainLoop()