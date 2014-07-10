from Tkinter import *

class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master=master
        pad=3
        self._geom='200x200+0+0'
        self.master.geometry("{0}x{1}+0+0".format(
            self.master.winfo_screenwidth()-pad, 
            self.master.winfo_screenheight()-pad)
        )
        self.master.bind('<Escape>',self.toggle_geom)
        self.master.update()
        self.current_step = 0
        self.canvas_size = self.get_canvas_size()
        self.canvas_centre = self.canvas_size / 2
        self.canvas = Canvas(self.master, width=self.canvas_size, height=self.canvas_size, background="black")
        self.canvas.grid(column=3,row=0,rowspan = 500, padx=20, pady=10)
        self.next()

    def next(self):
        self.canvas.delete("all")
        self.canvas.grid_remove()
        self.current_step +=1
        if self.current_step == 1:
            self.step_one()
        elif self.current_step == 2:
            self.step_one_frame.grid_remove()
            self.step_two()
        elif self.current_step == 3:
            self.step_two_frame.grid_remove()
            self.step_three()
        else:
            exit(0)

    def step_one(self):
        self.step_one_frame = LabelFrame(self.master,text="Step 1", padx=5, pady=5)
        self.step_one_frame.grid(column=1,row=0,sticky=N+S+E+W)

        self.max_width  = IntVar()
        self.max_depth= IntVar()
        self.max_height= IntVar()
        self.rotate  = BooleanVar()
        self.flip_1= BooleanVar()
        self.flip_2= BooleanVar()

        self.max_width.set(50)
        self.max_depth.set(50)
        self.max_height.set(50)

        text = Text(self.step_one_frame, height = 5, width = 50,wrap = WORD)
        text.grid(column=1,row=0, padx=10, pady=10, columnspan=2)
        text.insert(INSERT, "Enter the maximums of your print area, and use the flip and rotate to make the triangle your printer is drawing clockwise and look similar to the example image")
        text.config(state =DISABLED)

        Label(self.step_one_frame,text="Maximum width (mm)").grid(column=1,row=1, padx=10, pady=10)
        Entry(self.step_one_frame,textvariable = self.max_width, width=5).grid(column=2,row=1, padx=10, pady=10)
        Label(self.step_one_frame,text="Maximum depth (mm)").grid(column=1,row=2, padx=10, pady=10)
        Entry(self.step_one_frame,textvariable = self.max_depth, width=5).grid(column=2,row=2, padx=10, pady=10)
        Label(self.step_one_frame,text="Maximum height (mm)").grid(column=1,row=3, padx=10, pady=10)
        Entry(self.step_one_frame,textvariable = self.max_height, width=5).grid(column=2,row=3, padx=10, pady=10)

        self.canvas.grid()
        Checkbutton(self.step_one_frame, text="Rotate"      , variable=self.rotate, justify=LEFT ).grid(column=2,row=4, padx=10, pady=10, sticky=W)
        Checkbutton(self.step_one_frame, text="Flip Axis 1" , variable=self.flip_1, justify=LEFT ).grid(column=2,row=5, padx=10, pady=10, sticky=W)
        Checkbutton(self.step_one_frame, text="Flip Axis 2" , variable=self.flip_2, justify=LEFT ).grid(column=2,row=6, padx=10, pady=10, sticky=W)
        x_size = self.canvas_size * 0.1
        y_size = self.canvas_size * 0.4
        self.canvas.create_line( 
            self.canvas_centre - x_size , self.canvas_centre + y_size,  
            self.canvas_centre - x_size , self.canvas_centre - y_size,
            fill="white")
        self.canvas.create_line( 
            self.canvas_centre - x_size , self.canvas_centre - y_size,  
            self.canvas_centre + x_size , self.canvas_centre - y_size,
            fill="white")
        self.canvas.create_line( 
            self.canvas_centre + x_size , self.canvas_centre - y_size,
            self.canvas_centre - x_size , self.canvas_centre + y_size,
             fill="white")

        Button(self.step_one_frame, text='Next', command = self.next).grid(column=2,row=8, padx=10, pady=10,sticky="NES")

    def step_two(self):
        self.step_two_frame = LabelFrame(self.master,text="Step 2", padx=5, pady=5)
        self.step_two_frame.grid(column=1,row=0,sticky=N+S+E+W)

        text = Text(self.step_two_frame, height = 5, width = 50,wrap = WORD)
        text.grid(column=1,row=0, padx=10, pady=10, columnspan=2)
        text.insert(INSERT, "Toggle between the center point and line to center your grid paper and align it at the lowest point your print, This willl be the top of the resin when you start printing.")
        text.config(state =DISABLED)

        centre = Radiobutton(self.step_two_frame, text="Centre Point"  ,  value=1)
        centre.grid(column=2,row=2, padx=10, pady=10, sticky=W)

        align = Radiobutton(self.step_two_frame, text="Alignment Line",  value=2)
        align.grid(column=2,row=3, padx=10, pady=10, sticky=W)
        centre.select()

        Button(self.step_two_frame, text='Next', command = self.next).grid(column=2,row=6, padx=10, pady=10,sticky="NES")

    def step_three(self):
        self.current_collection = 0
        self.collections = [(50,50),(50,-50),(-50,-50),(-50,50)]
        self.step_three_frame = LabelFrame(self.master,text="Step 3", padx=5, pady=5)
        self.step_three_frame.grid(column=1,row=0,sticky=N+S+E+W)

        text = Text(self.step_three_frame, height = 5, width = 50,wrap = WORD)
        text.grid(column=1,row=0, padx=10, pady=10, columnspan=2)
        text.insert(INSERT, "Use the mouse in the box on the screen to move the laser to the requested point on the grid paper")
        text.config(state =DISABLED)

        self.draw_point_collection_canvas()
        self.current_point = StringVar()
        self.clickxy(None)
        Label(self.step_three_frame, textvariable = self.current_point, font = "Verdana 10 bold").grid(column=1,row=2, padx=10, pady=10, columnspan=2)

        self.points_button = Button(self.step_three_frame, text='Next', command = self.next)
        self.points_button.grid(column=2,row=6, padx=10, pady=10,sticky="NES")
        self.points_button.config(state=DISABLED)


    def draw_point_collection_canvas(self):
        self.canvas.grid()
        
        for i in range(0,self.canvas_centre,10):
            ppos = self.canvas_centre + i
            npos = self.canvas_centre - i
            self.canvas.create_line( ppos,    0,  ppos, self.canvas_size, fill="dark slate gray")
            self.canvas.create_line( npos,    0,  npos, self.canvas_size, fill="dark slate gray")
            self.canvas.create_line(   0,  ppos,  self.canvas_size, ppos, fill="dark slate gray")
            self.canvas.create_line(   0,  npos,  self.canvas_size, npos, fill="dark slate gray")
        self.canvas.create_line( self.canvas_centre,    0,  self.canvas_centre, self.canvas_size, fill="white")
        self.canvas.create_line(   0,  self.canvas_centre,  self.canvas_size, self.canvas_centre, fill="white")
        # self.canvas.bind("<Motion>", self.showxy)
        self.canvas.bind("<Button-1>", self.clickxy)


    def clickxy(self,event):
        if self.collections:
            point = self.collections.pop()
            self.current_point.set("Move the laser to x: %smm, y: %smm and click" % point)
        else:
            self.current_point.set("Done")
            self.points_button.config(state=NORMAL)

    def get_canvas_size(self):
        width =  self.master.winfo_width()
        height = self.master.winfo_height()
        print("%sx%s" % (width,height))
        max_width = width - 200 - 15
        max_height = height - 15
        size = min(max_width,max_height)
        if size % 2 == 0:
            return size - 1
        else:
            return size



    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom

root=Tk()
app=FullScreenApp(root)
root.mainloop()
