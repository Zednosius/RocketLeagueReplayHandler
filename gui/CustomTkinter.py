from Tkinter import *
import tkFont
class ReplayManager:
    def __init__(self,parent):
        pass


class DragDropList(Listbox):
    def __init__(self, parent, **kw):
        kw['selectmode'] = SINGLE
        Listbox.__init__(self, parent, kw)
        self.bind('<Button-1>', self.setCurrent)
        self.bind('<B1-Motion>', self.shiftSelection)
        self.curIndex = None

    def setCurrent(self, event):
        self.curIndex = self.nearest(event.y)
        print event

    def shiftSelection(self, event):
        print event
        i = self.nearest(event.y)
        if i < self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i+1, x)
            self.curIndex = i
        elif i > self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i-1, x)
            self.curIndex = i

class ReplayInfoFrame(Frame):

    def __init__(self,parent,**kw):
        print "hurdurr"
        kw['background'] = "red"
        Frame.__init__(self,parent,kw)
        mFont = tkFont.Font(family="Helvetica",size=14,weight=tkFont.BOLD)
        print "Hurdrur"
        self.replay_header = Frame(self, background="red")
        Label(self.replay_header,font=mFont, text="Name").grid(row=0, column=0)
        Label(self.replay_header,font=mFont, text="Map").grid(row=0, column=1)
        Label(self.replay_header,font=mFont, text="Score").grid(row=0, column=2)
        Label(self.replay_header,font=mFont, text="Hello World!").grid(row=0, column=3)

        for i in range(0,4):
            self.replay_header.grid_columnconfigure(i,weight=1)

        self.team_body = Frame(self, width=200, height=200)
        Label(self.team_body,text="Blue Team", font=mFont, fg="Blue").grid(row=0, column=0)
        Label(self.team_body,text="Red Team" , font=mFont, fg="Red").grid(row=0, column=2)
        Frame(self.team_body,background="black",height=1).grid(row=1,columnspan=3,sticky="WE")
        Frame(self.team_body,background="black",width=1).grid(row=0,column=1,rowspan=5,sticky="SN")
        for i in range(1,4):
            Label(self.team_body,text="Player "+str(i), font=mFont, fg="Blue").grid(row=i+1, column=0)
            Label(self.team_body,text="Player "+str(i+3), font=mFont, fg="Red").grid(row=i+1, column=2)


        self.tag_body = Frame(self, background="green")
        self.note_body = Frame(self, background="red")
        self.replay_header.grid(row=0,sticky=N)
        self.team_body.grid(row=1,sticky=W)
        self.tag_body.grid(row=1,sticky=E)
        self.note_body.grid(row=2,sticky=S)

        for i in range(0,3):
            self.grid_columnconfigure(i,weight=1)
            self.grid_rowconfigure(i,weight=1)


