#!/usr/bin/env python3

try:    # Python3
    import tkinter as tk
    from tkinter import ttk
except:  # Python2
    import Tkinter as tk
    import ttk as ttk


def coordInBbox(inCoord=(10, 10), inBbox=(0, 0, 20, 20)):  # like pointInRect() on the Mac
    (x, y) = inCoord
    (theLeft, theTop, theRight, theBottom) = inBbox
    print('coordInBbox(inCoord = {}, inBbox = {}'.format(inCoord, inBbox))
    return theLeft < x and x < theRight and theTop < y and y < theBottom


def tkEventAsString(inEvent):
    s = 'widget:{}, type:{}, x:{}, y:{}'
    return s.format(inEvent.widget, inEvent.type, inEvent.x, inEvent.y)

# ===============


class tkDraggableCanvas(tk.Canvas):

    def __init__(self, inDNDCanvas, inName):
        print('tkDraggableCanvas.__init__() starts')
        assert inDNDCanvas
        self.mDNDCanvas = inDNDCanvas
        master = self.mDNDCanvas  # .getCanvas()
        # print(class(master))
        # print(class(self))
        # super(tkDraggableFrame, self).__init__(self, master)
        tk.Canvas.__init__(self, master, bg='green', width=75,
                           height=75)  # , offset='100, 100')
        # self.geometry('75x75')
        self.grid()
        # self.pack()
        # self.pack(expand='yes', fill='both')
        theCanvas = tk.Canvas(self, width=1, height=1)
        theOval = theCanvas.create_oval(20, 20, 70, 70, outline='blue', fill='lightgray')
        theCanvas.grid(row=7, column=7)
        # self.bind("<ButtonPress>", self.onClick)
        self.mName = inName.replace(' ', '_')  # difficult bug to find!
        self.resetItemAndCoord()
        # self.bind('<ButtonPress-1>',   self.onClick)
        # self.bind('<B1-Motion>',       self.onDrag)
        # self.bind('<ButtonRelease-1>', self.onDrop)
        self.mDNDCanvas.addDraggableCanvas(self)
        print('tkDraggableCanvas.__init__() ends')

    def resetItemAndCoord(self):
        self.mItem = None
        self.mCoord = (0, 0)

    def onClick(self, inEvent):
        print('onClick() event:', tkEventAsString(inEvent))
        theCanvas = self.mDNDCanvas.getCanvas()
        self.mItem = theCanvas.find_closest(inEvent.x, inEvent.y)[0]
        self.mCoord = (inEvent.x, inEvent.y)
        return self.mCoord

    def onDrag(self, inEvent):
        (x, y) = self.mCoord
        delta_x = inEvent.x - x
        delta_y = inEvent.y - y
        theCanvas = self.mDNDCanvas.getCanvas()
        theCanvas.move(self.mItem, delta_x, delta_y)
        self.mCoord = (inEvent.x, inEvent.y)
        return self.mCoord

    def onDrop(self, inEvent):
        print(' onDrop() event:', tkEventAsString(inEvent))
        dropCoord = self.mCoord
        self.resetItemAndCoord()
        print(self.mName, 'was dropped in DropZone:',
              self.mDNDCanvas.whichDropZone(dropCoord))
        return dropCoord

# ===============


class tkDraggableFrame(ttk.Frame):

    def __init__(self, inDNDFrame, inName):
        print('tkDraggableFrame.__init__() starts')
        assert inDNDFrame
        self.mDNDFrame = inDNDFrame
        master = self.mDNDFrame.getCanvas()
        # print(class(master))
        # print(class(self))
        # super(tkDraggableFrame, self).__init__(self, master)
        # , bg='green', width=100, height=100) # , offset='100, 100')
        ttk.Frame.__init__(self, master)
        # self.geometry('75x75')
        # self.grid()
        self.pack(side=tk.BOTTOM)
        # self.pack(expand='yes', fill='both')
        theCanvas = tk.Canvas(self, width=100, height=100)
        theCanvas.pack()
        theOval = theCanvas.create_oval(
            20, 20, 70, 70, outline='blue', fill='lightgray')
        # theCanvas.grid(row=7, column=7)
        # self.bind("<ButtonPress>", self.onClick)
        self.mName = inName.replace(' ', '_')  # difficult bug to find!
        self.resetItemAndCoord()
        # self.bind('<ButtonPress-1>',   self.onClick)
        # self.bind('<B1-Motion>',       self.onDrag)
        # self.bind('<ButtonRelease-1>', self.onDrop)
        self.mDNDFrame.addDraggableFrame(self)
        print('tkDraggableFrame.__init__() ends')

    def resetItemAndCoord(self):
        self.mItem = None
        self.mCoord = (0, 0)

    def onClick(self, inEvent):
        print('onClick() event:', tkEventAsString(inEvent))
        theCanvas = self.mDNDFrame.getCanvas()
        self.mItem = theCanvas.find_closest(inEvent.x, inEvent.y)[0]
        self.mCoord = (inEvent.x, inEvent.y)
        return self.mCoord

    def onDrag(self, inEvent):
        (x, y) = self.mCoord
        delta_x = inEvent.x - x
        delta_y = inEvent.y - y
        theCanvas = self.mDNDFrame.getCanvas()
        theCanvas.move(self.mItem, delta_x, delta_y)
        self.mCoord = (inEvent.x, inEvent.y)
        return self.mCoord

    def onDrop(self, inEvent):
        print(' onDrop() event:', tkEventAsString(inEvent))
        dropCoord = self.mCoord
        self.resetItemAndCoord()
        print(self.mName, 'was dropped in DropZone:',
              self.mDNDFrame.whichDropZone(dropCoord))
        return dropCoord

# ===============


class tkDraggableWidget(object):

    def __init__(self, inDNDFrame, inWidget, inName):
        # print('tkDraggableWidget.__init__() starts')
        assert inDNDFrame
        self.mDNDFrame = inDNDFrame
        self.mWidget = inWidget
        self.mName = inName.replace(' ', '_')  # difficult bug to find!
        self.resetItemAndCoord()
        if not self.mWidget:
            theCanvas = self.mDNDFrame.getCanvas()
            self.mWidget = theCanvas.create_oval(150, 200, 200, 250,
                                                 outline='blue', fill='lightgray', tags=self.mName)
        self.mDNDFrame.addDraggableWidget(self)
        # print('tkDraggableWidget.__init__() ends')

    def resetItemAndCoord(self):
        self.mItem = None
        self.mCoord = (0, 0)

    def onClick(self, inEvent):
        # print('onClick() event:', tkEventAsString(inEvent)
        theCanvas = self.mDNDFrame.getCanvas()
        self.mItem = theCanvas.find_closest(inEvent.x, inEvent.y)[0]
        self.mCoord = (inEvent.x, inEvent.y)
        return self.mCoord

    def onDrag(self, inEvent):
        (x, y) = self.mCoord
        delta_x = inEvent.x - x
        delta_y = inEvent.y - y
        theCanvas = self.mDNDFrame.getCanvas()
        theCanvas.move(self.mItem, delta_x, delta_y)
        self.mCoord = (inEvent.x, inEvent.y)
        return self.mCoord

    def onDrop(self, inEvent):
        # print(' onDrop() event:', tkEventAsString(inEvent)
        dropCoord = self.mCoord
        self.resetItemAndCoord()
        print(self.mName, 'was dropped in DropZone:',
              self.mDNDFrame.whichDropZone(dropCoord))
        return dropCoord

# ===============


class tkDragAndDropFrame(ttk.Frame):

    def __init__(self, master=None, width=1280):
        ttk.Frame.__init__(self, master)
        # print('tkDragAndDropCanvas.__init__() starts')
        height = width * 9 / 16  # HiDef aspect ratio = 9/16
        # self.grid(row=4, column=4)
        self.pack()
        # self.mCanvas = tk.Canvas(self, width=width, height=height)
        self.mCanvas = tk.Canvas(self, width=width, height=height,  bg='gray')
        # self.mCanvas.pack()
        N = tk.N
        E = tk.E
        S = tk.S
        W = tk.W
        NSEW = (tk.N, tk.S, tk.E, tk.W)
        self.mCanvas.grid(column=0, row=0, columnspan=10,
                          rowspan=10, sticky=NSEW)
        # N = tk.N; E = tk.E; S = tk.S; W = tk.W
        # self.grid(column=0, row=0, columnspan=10, rowspan=10, sticky=(N,S,E,W))
        self.mDraggableCanvases = []  # Canvases that you can drap
        self.mDraggableFrames = []   # Frames that you can drap
        self.mDraggableWidgets = []  # widgets that you can drap
        self.mDropZones = []         # widgets that you can drop them on
        # print('tkDragAndDropCanvas.__init__() ends')

    def getCanvas(self):
        return self.mCanvas

    def addDraggableCanvas(self, inCanvas):
        # print('Binding:', inWidget.mName)
        # self.bind("<ButtonPress-1>",   inCanvas.onClick)
        # self.bind("<B1-Motion>",       inCanvas.onDrag)
        # self.bind("<ButtonRelease-1>", inCanvas.onDrop)
        inCanvas.bind("<ButtonPress-1>",   inCanvas.onClick)
        inCanvas.bind("<B1-Motion>",       inCanvas.onDrag)
        inCanvas.bind("<ButtonRelease-1>", inCanvas.onDrop)
        self.mDraggableCanvases.append(inCanvas)

    def addDraggableFrame(self, inFrame):
        # print('Binding:', inWidget.mName)
        self.mDraggableFrames.append(inFrame)

    def addDraggableWidget(self, inWidget):
        # print('Binding:', inWidget.mName)
        self.mCanvas.tag_bind(
            inWidget.mName, "<ButtonPress-1>",   inWidget.onClick)
        self.mCanvas.tag_bind(
            inWidget.mName, "<B1-Motion>",       inWidget.onDrag)
        self.mCanvas.tag_bind(
            inWidget.mName, "<ButtonRelease-1>", inWidget.onDrop)
        self.mDraggableWidgets.append(inWidget)

    def addDropZone(self, inDropZone, inName=None):
        print('self.mCanvas:', self.mCanvas)
        if not inName:
            inName = str(inDropZone)
        print('addDropZone({}, {}), coords: {}'.format(
            inDropZone, inName, self.bbox(inDropZone)))
        self.mDropZones.append([inDropZone, inName])

    def whichDropZone(self, inCoord):
        for dropZoneAndName in self.mDropZones:
            print('Checking zone:', dropZoneAndName[
                  1], self.bbox(dropZoneAndName[0]))
            if coordInBbox(inCoord, self.bbox(dropZoneAndName[0])):
                return dropZoneAndName[1]
        return None

# ===============


class SampleApp(tk.Tk):
    '''Illustrate how to drag items on a Tkinter canvas'''

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title('Drag and Drop target window')

        # first: Create the tkDragAndDropCanvas
        self.mDNDFrame = tkDragAndDropFrame()

        # second: create and register the DropZone(s)
        junk = """N = tk.N; E = tk.E; S = tk.S; W = tk.W
        self.r1 = tk.Frame(self.mDNDCanvas, bg='lightblue', bd=2)
        self.r1.grid(column=2, row=2, sticky=(N,S,E,W))
        self.mDNDCanvas.addDropZone(self.r1, 'Blue Rectangle')

        self.r2 = tk.Frame(self.mDNDCanvas, bg='lightyellow', bd=2)
        self.r2.grid(column=3, row=3, sticky=(N,S,E,W))
        self.mDNDCanvas.addDropZone(self.r2, 'Yellow Rectangle')
        """

        theCanvas = self.mDNDFrame.getCanvas()

        junk = """
        yellowFrame = ttk.Frame(theCanvas)
        yellowFrame.grid(row=3, column=3)
        yellowCanvas = tk.Canvas(yellowFrame, width=100, height=100,  bg='gray')
        yellowCanvas.pack()
        self.mDNDFrame.addDropZone(yellowCanvas, 'Yellow Frame')
        """

        theRect = (50, 50, 150, 150)  # Left, Top, Right, Bottom
        self.r1 = theCanvas.create_rectangle(
            theRect, fill="lightblue")  # name='Blue Rectangle',
        # print('Blue Rectangle:', self.r1, type(self.r1))
        self.mDNDFrame.addDropZone(self.r1, 'Blue Rectangle')
        theRect = (200, 50, 300, 150)  # Left, Top, Right, Bottom
        self.r2 = theCanvas.create_rectangle(
            theRect, fill="lightyellow")  # name='Yellow Rectangle',
        # print('Yellow Rectangle:', self.r2)
        # print('keys():', self.r2.keys())
        self.mDNDFrame.addDropZone(self.r2, 'Yellow Rectangle')
        # self.mDNDCanvas.pack()

        # third: create the tkDraggableWidget(s)
        # xxCanvas = tk.Canvas(self.mDNDCanvas, width=640, height=480)
        # xxCanvas.grid()
        # xxCanvas.pack()
        # theWidget = xxCanvas.create_oval(100, 200, 150, 250,
        #                outline='blue', fill='lightgray', tags='Widget 1')

        self.theWidgets = [tkDraggableWidget(self.mDNDFrame, None, 'Widget 1'),
                           tkDraggableWidget(self.mDNDFrame, None, 'Widget 2')]
        return

        self.theFrames = [tkDraggableFrame(self.mDNDFrame, 'Frame 1'),
                          tkDraggableFrame(self.mDNDFrame, 'Frame 2')]
#        for theFrame in self.theFrames:
#            theCanvas = tk.Canvas(theFrame, width=100, height=100, bd=2, relief=tk.RAISED)
#            theCanvas.pack()
#            theCanvas.create_oval(3, 3, 53, 53, outline='red', fill='lightgray')
#            theFrame.pack()

# self.theCanvases = [tkDraggableCanvas(self.mDNDCanvas, 'Canvas 1'),
# tkDraggableCanvas(self.mDNDCanvas, 'Canvas 2')]
#        for theCanvas in self.theCanvases:
#            theCanvas.create_oval(3, 3, 53, 53, outline='red', fill='lightgray')


# ===============

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
