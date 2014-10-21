#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'chenshini'

from Tkinter import *
root = Tk()
Label(root, text='Click at different\n locations in the frame below'). pack()
def mycallback(event):
    print dir(event)
    print 'you clicked at', event.x, event.y,event.time
myframe = Frame(root,bg='khaki',width= 130,height=80)
myframe.bind("<Button-1>",mycallback)
myframe.pack()
root.mainloop()
