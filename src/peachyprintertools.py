import Tkinter
from Tkinter import *
import os

root = Tk()
root.title("Peachy Printer Tools")
menubar = Menu(root)

# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)

a = Label(root, text ='Hello World!')
a.pack(side = "bottom", fill = "both", expand = "yes")

root.config(menu=menubar)

root.mainloop()