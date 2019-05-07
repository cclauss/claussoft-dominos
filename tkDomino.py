#!/usr/bin/env python3

from random import shuffle
import tkinter as tk
import tkinter.ttk as ttk

# import Tkdnd as Tkdnd
from drawDomino import draw_domino

# from tkDragAndDropCanvas import tkDragAndDropFrame, tkDraggableWidget
# from TkdndDropTarget import DropTarget, LabeledDropTarget, Draggable
from TkdndDropTarget import Draggable, DropTarget


def init_dominos(max_die: int = 6):
    return [[x, y] for x in range(max_die + 1) for y in range(x + 1)]


def build_a_domino(inMaster, inName="[5, 6]", inOrientation=tk.VERTICAL):
    domino = eval(inName)
    assert len(domino) == 2
    return draw_domino(inMaster, domino, inOrientation)


class tkDomino(Draggable):
    """GUI Domino as a Draggable that uses Tkdnd to support drag and drop"""

    def __init__(self, domino=[5, 6]):
        self.domino = domino
        self.name = str(self.domino).replace(" ", "")
        self.orientation = tk.VERTICAL
        Draggable.__init__(
            self, self.name, self.orientation, inDrawRoutine=build_a_domino
        )

    def __lt__(self, other):
        return self.domino < other.domino


class tkDominoBoard(ttk.Frame):
    """GUI Domino Board as a ttk.Frame that uses Tkdnd to support drag and drop"""

    def __init__(self, inMaster=None, inWidth: int = 1920, inHeight: int = 0):
        NSEW = (tk.N, tk.S, tk.E, tk.W)
        inHeight = inHeight or int(9 / 16 * inWidth)  # HiDef aspect ratio is 9/16
        # super(tkDominoBoard, self).__init__()
        ttk.Frame.__init__(self, inMaster, width=inWidth, height=inHeight)
        self.grid(sticky=NSEW)
        self.drop_zone_boneyard = None
        self.drop_zone_play_area = None
        self.drop_zone_player0 = None
        self.drop_zone_player1 = None
        self.drop_zone_score_board = None
        self.setup_drop_zones()

    def setup_drop_zones(self):
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
        self.drop_zone_player0 = DropTarget(
            theLabelframe, inWidth=128 * 8, inHeight=128, inBgColor="pink"
        )

        theLabelframe = ttk.Labelframe(self, text="Player 1", labelanchor=tk.N)
        theLabelframe.grid(column=1, row=9, columnspan=8, sticky=NSEW)
        self.drop_zone_player1 = DropTarget(
            theLabelframe, inWidth=128 * 8, inHeight=128, inBgColor="lightblue"
        )

        theLabelframe = ttk.Labelframe(self, text="Boneyard", labelanchor=tk.N)
        theLabelframe.grid(column=0, row=1, rowspan=8, sticky=NSEW)
        self.drop_zone_boneyard = DropTarget(
            theLabelframe, inWidth=128, inHeight=464, inBgColor="lightyellow"
        )

        theLabelframe = ttk.Labelframe(self, text="Score Board", labelanchor=tk.N)
        theLabelframe.grid(column=9, row=1, rowspan=8, sticky=NSEW)
        self.drop_zone_score_board = tk.Canvas(
            theLabelframe, height=464, width=128, bg="lightgreen"
        )
        self.drop_zone_score_board.grid()  # pack(fill=tk.BOTH, expand=tk.YES)

        theLabelframe = ttk.Labelframe(self, text="Play Area", labelanchor=tk.N)
        theLabelframe.grid(column=1, row=1, columnspan=8, sticky=NSEW)
        self.drop_zone_play_area = DropTarget(
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
        self.domino_board = tkDominoBoard(self)
        # print('self.domino_board.master', self.domino_board.master) # .
        # print('self.domino_board.children', self.domino_board.children) # { labels }
        # for theChild in self.domino_board.children:
        #    print(theChild, self.bbox(theChild)) # , theChild.misc

        self.dominos = init_dominos(6)
        for i in range(len(self.dominos)):
            self.dominos[i] = tkDomino(self.dominos[i])
        self.deal()

        # self.theDomino1 = tkDomino([3, 4])
        # self.theDomino1.attach(self.domino_board.drop_zone_player0)
        # print('self.theDomino1.master', self.theDomino1.master)
        # print('self.theDomino1.children', self.theDomino1.children)
        # self.theDomino = tkDomino([5, 6])
        # self.theDomino.attach(self.domino_board.drop_zone_player0)
        # print('self.theDomino.master', self.theDomino.master)
        # print('self.theDomino.children', self.theDomino.children)
        # print('self.master', self.master) # None
        # print('self.children', self.children) # {tkDominoBoard}

    def deal(self, dominos_per_player: int = 7):
        shuffle(self.dominos)
        shuffle(self.dominos)
        shuffle(self.dominos)
        # shuffle(shuffle(shuffle(self.dominos)))
        d = 0  # start with the first domino.
        for player in [
            self.domino_board.drop_zone_player0,
            self.domino_board.drop_zone_player1,
        ]:
            for domino in sorted(self.dominos[d : d + dominos_per_player]):
                domino.attach(player)
            d += dominos_per_player
        for domino in self.dominos[d:]:
            domino.mOrientation = tk.HORIZONTAL
            domino.attach(self.domino_board.drop_zone_boneyard)


# ===============

if __name__ == "__main__":
    SampleApp().mainloop()
