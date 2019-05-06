#!/usr/bin/env python3

from random import shuffle
import tkinter as tk
import tkinter.ttk as ttk

# import Tkdnd as Tkdnd
from drawDomino import drawDomino

# from tkDragAndDropCanvas import tkDragAndDropFrame, tkDraggableWidget
# from TkdndDropTarget import DropTarget, LabeledDropTarget, Draggable
from TkdndDropTarget import Draggable, DropTarget


def initDominos(n=6):
    return [[x, y] for x in range(n + 1) for y in range(x, n + 1)]


def buildADomino(inMaster, inName="[5, 6]", inOrientation=tk.VERTICAL):
    theDomino = eval(inName)
    assert len(theDomino) == 2
    return drawDomino(inMaster, theDomino, inOrientation)


class tkDomino(Draggable):
    """GUI Domino as a Draggable that uses Tkdnd to support drag and drop"""

    def __init__(self, inDomino=[5, 6]):
        self.mDomino = inDomino
        self.mName = str(self.mDomino).replace(" ", "")
        self.mOrientation = tk.VERTICAL
        Draggable.__init__(
            self, self.mName, self.mOrientation, inDrawRoutine=buildADomino
        )

    def __lt__(self, other):
        return self.mDomino < other.mDomino


class tkDominoBoard(ttk.Frame):
    """GUI Domino Board as a ttk.Frame that uses Tkdnd to support drag and drop"""

    def __init__(self, inMaster=None, inWidth=1920, inHeight=None):
        NSEW = (tk.N, tk.S, tk.E, tk.W)
        inHeight = inHeight or 9 / 16 * inWidth  # HiDef aspect ratio is 9/16
        # super(tkDominoBoard, self).__init__()
        ttk.Frame.__init__(self, inMaster, width=inWidth, height=inHeight)
        self.grid(sticky=NSEW)
        self.mDropZoneBoneyard = None
        self.mDropZonePlayArea = None
        self.mDropZonePlayer0 = None
        self.mDropZonePlayer1 = None
        self.mDropZoneScoreBoard = None
        self.setupDropZones()

    def setupDropZones(self):
        # N = tk.N
        # E = tk.E
        # S = tk.S
        # W = tk.W
        NSEW = (tk.N, tk.S, tk.E, tk.W)
        # NEW = (tk.N, tk.E, tk.W)

        theStyle = ttk.Style()
        # theStyle.configure('TLabelframe', labelanchor=tk.N, borderwidth=2, relief=tk.RAISED)
        # theStyle.configure('TLabelframe.TLabelframe', labelanchor=tk.N, borderwidth=2, relief=tk.RAISED)
        # , borderwidth=9, relief=tk.RAISED)
        theStyle.configure("TLabelframe.Label", foreground="dark blue")

        theLabelframe = ttk.Labelframe(self, text="Player 0", labelanchor=tk.N)
        theLabelframe.grid(column=1, row=0, columnspan=8, sticky=NSEW)
        self.mDropZonePlayer0 = DropTarget(
            theLabelframe, inWidth=128 * 8, inHeight=128, inBgColor="pink"
        )

        theLabelframe = ttk.Labelframe(self, text="Player 1", labelanchor=tk.N)
        theLabelframe.grid(column=1, row=9, columnspan=8, sticky=NSEW)
        self.mDropZonePlayer1 = DropTarget(
            theLabelframe, inWidth=128 * 8, inHeight=128, inBgColor="lightblue"
        )

        theLabelframe = ttk.Labelframe(self, text="Boneyard", labelanchor=tk.N)
        theLabelframe.grid(column=0, row=1, rowspan=8, sticky=NSEW)
        self.mDropZoneBoneyard = DropTarget(
            theLabelframe, inWidth=128, inHeight=464, inBgColor="lightyellow"
        )

        theLabelframe = ttk.Labelframe(self, text="Score Board", labelanchor=tk.N)
        theLabelframe.grid(column=9, row=1, rowspan=8, sticky=NSEW)
        self.mDropZoneScoreBoard = tk.Canvas(
            theLabelframe, height=464, width=128, bg="lightgreen"
        )
        self.mDropZoneScoreBoard.grid()  # pack(fill=tk.BOTH, expand=tk.YES)

        theLabelframe = ttk.Labelframe(self, text="Play Area", labelanchor=tk.N)
        theLabelframe.grid(column=1, row=1, columnspan=8, sticky=NSEW)
        self.mDropZonePlayArea = DropTarget(
            theLabelframe, inWidth=128 * 8, inHeight=464, inBgColor="PeachPuff"
        )


class SampleApp(tk.Tk):
    """Illustrate how to drag items on a Tkinter canvas"""

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # NSEW = (tk.N, tk.S, tk.E, tk.W)
        # self.grid(sticky=NSEW)
        self.grid()
        self.title("Drag and Drop Dominos")
        # print('self.master', self.master) # None
        # print('self.children', self.children) # {}

        # first: Create the tkDragAndDropCanvas
        self.mDominoBoard = tkDominoBoard(self)
        # print('self.mDominoBoard.master', self.mDominoBoard.master) # .
        # print('self.mDominoBoard.children', self.mDominoBoard.children) # { labels }
        # for theChild in self.mDominoBoard.children:
        #    print(theChild, self.bbox(theChild)) # , theChild.misc

        self.mDominos = initDominos(6)
        for i in range(len(self.mDominos)):
            self.mDominos[i] = tkDomino(self.mDominos[i])
        self.deal()

        # self.theDomino1 = tkDomino([3, 4])
        # self.theDomino1.attach(self.mDominoBoard.mDropZonePlayer0)
        # print('self.theDomino1.master', self.theDomino1.master)
        # print('self.theDomino1.children', self.theDomino1.children)
        # self.theDomino = tkDomino([5, 6])
        # self.theDomino.attach(self.mDominoBoard.mDropZonePlayer0)
        # print('self.theDomino.master', self.theDomino.master)
        # print('self.theDomino.children', self.theDomino.children)
        # print('self.master', self.master) # None
        # print('self.children', self.children) # {tkDominoBoard}

    def deal(self, inDominosPerPlayer=7):
        shuffle(self.mDominos)
        shuffle(self.mDominos)
        shuffle(self.mDominos)
        # shuffle(shuffle(shuffle(self.mDominos)))
        d = 0  # start with the first domino.
        for thePlayer in [
            self.mDominoBoard.mDropZonePlayer0,
            self.mDominoBoard.mDropZonePlayer1,
        ]:
            theDominos = sorted(self.mDominos[d : d + inDominosPerPlayer])
            for theDomino in theDominos:
                theDomino.attach(thePlayer)
            d += inDominosPerPlayer
        theDominos = self.mDominos[d:]
        for theDomino in theDominos:
            theDomino.mOrientation = tk.HORIZONTAL
            theDomino.attach(self.mDominoBoard.mDropZoneBoneyard)


# ===============

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
