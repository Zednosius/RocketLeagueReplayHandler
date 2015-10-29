#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information
from Tkinter import *
import ttk
import gui.CustomTkinter as cst
def output():
    print "Not implemented"
root = Tk()

menu = Menu(root)
root.config(menu=menu)

filemenu = Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="New", command=output)
filemenu.add_command(label="Open...", command=output)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=output)

helpmenu = Menu(menu)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="About...", command=output)

resultframe = Frame(root, background="red")
resultframe.grid(row=0,column=0,sticky="NSEW")

Lb1 = cst.DragDropList(root)


#Lb1.bind('<ButtonRelease-1>', output)
# Lb1.bind("<B1-Motion>",output)
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
# Lb2.bind("<B1-Motion>",output)
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
info.grid(row=0,column=1,sticky="NSWE")
Lb1.link(Lb2)
Lb2.link(Lb1)
Label(root,text="player 7",bg="purple").grid(row=1,column=1,sticky="WE")
root.grid_columnconfigure(0,weight=1)
root.grid_columnconfigure(1,weight=1)
root.grid_columnconfigure(2,weight=1)
root.grid_rowconfigure(0,weight=1)

root.mainloop()
