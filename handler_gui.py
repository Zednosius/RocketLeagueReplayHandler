#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information
from Tkinter import *
from ttk import *
import gui.CustomTkinter as cst
root = Tk()

resultframe = Frame(root)
resultframe.grid(row=0,column=0,sticky="NSEW")
Lb1 = Listbox(resultframe,selectmode=MULTIPLE)
Lb1.insert(1, "Python")
Lb1.insert(2, "Perl")
Lb1.insert(3, "C")
Lb1.insert(4, "PHP")
Lb1.insert(5, "JSP")
Lb1.insert(6, "Ruby")

Lb1.grid(row=0,column=0,sticky="NSWE")
resultframe.grid_rowconfigure(0,weight=1)
resultframe.grid_columnconfigure(0,weight=1)

Lb2 = cst.DragDropList(root)
Lb2.insert(1, "1Python")
Lb2.insert(2, "1PythonPerl")
Lb2.insert(3, "C2")
Lb2.insert(4, "P2HP")
Lb2.insert(5, "JS5P")
Lb2.insert(6, "Ru6by")

Lb2.grid(row=0,column=2,sticky="NSWE")
# tree = Treeview(root)
# id_ = tree.insert('','end','widgets',text='testing')
# tree.insert(id_,'end',text="Child")
# tree.pack(fill=Y,expand=1,side=RIGHT)
info = cst.ReplayInfoFrame(root)
info.grid(row=0,column=1)

root.grid_columnconfigure(0,weight=1)
root.grid_columnconfigure(1,weight=1)
root.grid_columnconfigure(2,weight=1)
root.grid_rowconfigure(0,weight=1)

root.mainloop()
