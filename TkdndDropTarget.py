#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
from tkinter import dnd

'''
try:    # Python3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import dnd
except:  # Python2
    import Tkinter as tk
    import ttk as ttk
    import Tkdnd as dnd
'''

from drawDomino import drawDomino


class DropTarget(tk.Canvas):
    """DropTarget(inMaster, inWidth=100, inHeight=100, inBgColor='lightblue'): uses tkinter.dnd
    to enable Draggables to be Drag and Dropped.

    See the somewhat confusing comments at the top of tkinter.dnd.py
    +---------------------------------------------------------+
    | oldTarget is  | newTarget is  | Action Taken is         |
    + ------------- | ------------- | ----------------------- +
    | None          | None          | None                    |
    + ------------- | ------------- | ----------------------- +
    | newTarget     | oldTarget     | newTarget.dnd_motion()  |
    + ------------- | ------------- | ----------------------- +
    | None          | not None      | newTarget.dnd_enter()   |
    + ------------- | ------------- | ----------------------- +
    | not None      | None          | oldTarget.dnd_leave()   |
    + ------------- | ------------- | ----------------------- +
    | not None and  | not None and  | oldTarget.dnd_leave()   |
    | not newTarget | not oldTarget | & newTarget.dnd_enter() |
    +---------------------------------------------------------+
    """

    def __init__(self, inMaster, inWidth=101, inHeight=100, inBgColor='lightblue'):
        self.mMaster = inMaster
        # if not inHeight:
        inHeight or 9 / 16 * inWidth  # HiDef aspect ratio is 9/16
        tk.Canvas.__init__(self, inMaster, width=inWidth,
                           height=inHeight, bg=inBgColor)
        self.grid()

    def dnd_accept(self, inSource, inEvent):
        # print('dnd_accept:', inEvent)
        return self

    def dnd_enter(self, inSource, inEvent):
        # print('dnd_enter:', inEvent)
        self.focus_set()  # Show highlight border
        (x, y) = inSource.where(self, inEvent)
        # inSource.mCanvas.bbox(inSource.mWindowID)
        (x1, y1, x2, y2) = inSource.windowCoords()
        width = x2 - x1
        height = y2 - y1
        self.dndid = self.create_rectangle(x, y, x + width, y + height)
        self.dnd_motion(inSource, inEvent)

    def dnd_motion(self, inSource, inEvent):
        # print('dnd_motion:', inEvent)
        (x, y) = inSource.where(self, inEvent)
        (x1, y1, x2, y2) = self.bbox(self.dndid)
        self.move(self.dndid, x - x1, y - y1)

    def dnd_leave(self, inSource, inEvent):
        # print('dnd_leave:', inEvent)
        self.mMaster.focus_set()  # Hide highlight border
        self.delete(self.dndid)
        self.dndid = None

    def dnd_commit(self, inSource, inEvent):
        # print('dnd_commit:', inEvent)
        self.dnd_leave(inSource, inEvent)
        (x, y) = inSource.where(self, inEvent)
        inSource.attach(self, x, y)

    def arrange(self):
        theChildren = self.find_all()
        if len(theChildren) == 1:
            self.arrangeFirst()
            return
        if int(self['width']) > int(self['height']):
            theOrientation = tk.HORIZONTAL
            longDimension = int(self['width'])
        else:
            theOrientation = tk.VERTICAL
            longDimension = int(self['height'])

        theBuffer = (longDimension - len(theChildren) * 75) / 2
        if theBuffer < 10:
            theBuffer = 10

        i = 0
        for theChild in theChildren:
            if theOrientation == tk.HORIZONTAL:
                self.coords(theChild, theBuffer + i * 75, 10)
            else:
                self.coords(theChild, 10, theBuffer + i * 75)

            # print(self.type(theChild), self.coords(theChild) # window [10.0, 10.0])
            # print(self, theChild, 'arrange child i:', i)
            # .4453228272.4457567080.4457567152 1 arrange child i: 0
            # print(self.showConfig())
            # print('{} children in {}x{}'.format(len(self.children), self['width'], self.cget('height')))
            # 1 children in 1024x128
            # print(self.configure('width, -height'))
            i += 1

    def arrangeFirst(self):
        theChild = self.find_all()[0]
        # theChild.mOrientation = tk.HORIZONTAL
        longDimension = int(self['width'])
        theBuffer = (longDimension - 75) / 2
        self.coords(theChild, theBuffer, 10)

    def showConfig(self):
        theOutput = []
        for theKey in sorted(self.config()):
            theOutput.append(str(self.config(theKey)))
        return '\t' + '\n\t'.join(theOutput)


class LabeledDropTarget(DropTarget):
    """LabeledDropTarget(inMaster, inName, inWidth=100, inHeight=100, inBgColor='lightblue')
    Proved less useful than originally thought."""

    def __init__(self, inMaster, inName, inWidth=100, inHeight=100, inBgColor='lightblue'):
        theLabelframe = ttk.Labelframe(inMaster, text=inName, labelanchor=tk.N)
        theLabelframe.grid()
        DropTarget.__init__(self, theLabelframe, inWidth=inWidth,
                            inHeight=inHeight, inBgColor=inBgColor)


def gridSlaveBindPropogate(inSlave, inBindType, inCallback):
    # print('theSlave:', str(type(theSlave)))
    inSlave.bind(inBindType, inCallback)
    for theSlave in inSlave.grid_slaves():
        gridSlaveBindPropogate(theSlave, inBindType, inCallback)


def buildADomino(inMaster, inName='[5, 6]', inOrientation=tk.VERTICAL):
    theDomino = eval(inName)
    assert len(theDomino) == 2
    return drawDomino(inMaster, theDomino, inOrientation)


def myDrawRoutine(inMaster, inName='????', inOrientation=tk.VERTICAL):
    return ttk.Label(inMaster, text=inName, borderwidth=2, relief=tk.RAISED)


class Draggable(object):
    """Draggable(inName): uses tkinter.dnd to enable the widget (self.mWidgetID) to be Drag and
    Dropped into DropTargets.  attach() must be called to initially add your Draggable to
    a DropTarget.  The widget will need to be modified to meet specific requirements.
    """

    def __init__(self, inName, inOrientation=tk.VERTICAL, inDrawRoutine=myDrawRoutine):
        self.mName = inName
        self.mOrientation = inOrientation
        self.mDrawRoutine = inDrawRoutine
        self.mCanvas = self.mWidgetID = self.mWindowID = None
        self.mXOffset = self.mYOffset = None
        self.mXOrigin = self.mYOrigin = None

    def attach(self, inCanvas, inX=10, inY=10):
        # print('attach:', self.mCanvas, inCanvas)
        if inCanvas is self.mCanvas:
            self.mCanvas.coords(self.mWindowID, inX, inY)
            self.mCanvas.arrange()
            return
        if self.mCanvas:
            self.detach()
        if not inCanvas:
            return
        self.mCanvas = inCanvas
        # print('attach2:', self.mCanvas, inCanvas)
        # self.mWidgetID = ttk.Label(self.mCanvas, text=self.mName, borderwidth=2,
        #                      relief="raised")
        self.mWidgetID = self.mDrawRoutine(
            self.mCanvas, self.mName, self.mOrientation)
        self.mWindowID = self.mCanvas.create_window(
            inX, inY, window=self.mWidgetID, anchor="nw")
        # self.mWidgetID.grid(row=0, column=0)
        # self.mWidgetID.bind('<ButtonPress>', self.onMouseDown)
        gridSlaveBindPropogate(
            self.mWidgetID, '<ButtonPress>', self.onMouseDown)
        self.mCanvas.arrange()

        # self.mCanvas.bind("<ButtonPress>", self.onMouseDown)
        _ = """
        print(self.mCanvas, 'mWidgetID:', self.mCanvas.bbox(self.mWidgetID))
        print(self.mCanvas, 'mWindowID:', self.mCanvas.bbox(self.mWindowID))
        i = 0
        for theChild in self.mCanvas.children:
            print(self.mCanvas, 'child i:', i, self.mCanvas.bbox(theChild))
            i += 1

        i = 0
        for theSlave in inCanvas.grid_slaves():
            print(inCanvas, 'slave i:', i)
            #print(inCanvas)
            theSlave.grid(row=0, column=i)
            i += 1
         """

    def detach(self):
        # print('detach:', self.mCanvas)
        if not self.mCanvas:
            return
        self.mCanvas.delete(self.mWindowID)
        self.mWidgetID.destroy()
        self.mCanvas = self.mWidgetID = self.mWindowID = None

    def onMouseDown(self, inEvent):
        # print('onMouseDown:', (inEvent.x, inEvent.x), inEvent.widget)
        if dnd.dnd_start(self, inEvent):
            # where the pointer is relative to the label widget:
            self.mXOffset = inEvent.x
            self.mYOffset = inEvent.y
            # where the widget is relative to the canvas:
            self.mXOrigin, self.mYOrigin = self.mCanvas.coords(self.mWindowID)

    def move(self, inEvent):
        x, y = self.where(self.mCanvas, inEvent)
        self.mCanvas.coords(self.mWindowID, x, y)

    def putback(self):
        self.canvas.coords(self.mWindowID, self.mXOrigin, self.mYOrigin)

    def where(self, inCanvas, inEvent):
        # where the corner of the canvas is relative to the screen:
        mXOrigin = inCanvas.winfo_rootx()
        mYOrigin = inCanvas.winfo_rooty()
        # where the pointer is relative to the canvas widget:
        x = inEvent.x_root - mXOrigin
        y = inEvent.y_root - mYOrigin
        # compensate for initial pointer offset
        return x - self.mXOffset, y - self.mYOffset

    def windowCoords(self):
        return self.mCanvas.bbox(self.mWindowID)

    def dnd_end(self, target, event):
        pass


def main():
    root = tk.Tk()
    root.geometry("+1+1")
    tk.Button(command=root.quit, text="Quit").grid()

    top1 = tk.Toplevel(root)
    top1.geometry("+1+80")
    t1 = DropTarget(top1)

    top2 = tk.Toplevel(root)
    top2.geometry("+120+80")
    # t2 = DropTarget(top2)
    t2 = LabeledDropTarget(top2, 'Labelframe')

    top3 = tk.Toplevel(root)
    top3.geometry("+240+80")
    t3 = DropTarget(top3, inWidth=1280, inHeight=720)
    top3.geometry("1280x720")

    i1 = Draggable("ICON1")
    i2 = Draggable("ICON2", myDrawRoutine)
    d1 = Draggable("[1,2]", buildADomino)
    d2 = Draggable("[2,3]", buildADomino)
    d3 = Draggable("[3,4]", buildADomino)
    i1.attach(t1)
    i2.attach(t2)
    d1.attach(t3)
    d2.attach(t3)
    d3.attach(t3)
    # print(len(t3.place_slaves()))   # 0
    # print(len(t3.pack_slaves()))    # 0
    # print(len(t3.grid_slaves()))    # 0
    # print(len(t3.winfo_children())) # 3
    # print(len(t3.children))         # 3
#    i = 0
#    for theChild in t3.winfo_children():
#        theChild.grid(row=0, column=i)
#        i += 1
#        print('voodooChild:', theChild.__class__, theChild.bbox())
#        for theAttribute in sorted(theChild.configure()):
#            print('    {}: {}'.format(theAttribute, theChild.configure(theAttribute)))
    root.mainloop()

if __name__ == '__main__':
    main()
