#!/usr/bin/env python3

import tkinter as tk
# from tkinter import ttk


def onMouseDownInDie(inEvent):
    print("onMouseDownInDie:", (inEvent.x, inEvent.x), inEvent.widget)


# The locations of the dots on a 3x3 grid.
pipLocs = [
    [[]],
    [[1, 1]],
    [[0, 0], [2, 2]],
    [[0, 0], [1, 1], [2, 2]],
    [[0, 0], [0, 2], [2, 0], [2, 2]],
    [[0, 0], [0, 2], [1, 1], [2, 0], [2, 2]],
    [[0, 0], [0, 1], [0, 2], [2, 0], [2, 1], [2, 2]],
]


def pipCanvas(inCanvas, inOutlineColor="blue", inFillColor="gray"):
    theCanvas = tk.Canvas(inCanvas, width=13, height=13)
    theCanvas.create_oval(3, 3, 13, 13, outline=inOutlineColor, fill=inFillColor)
    return theCanvas


def drawPipInGrid(inCanvas, inLoc, inOutlineColor="blue", inFillColor="gray"):
    pipCanvas(inCanvas, inOutlineColor, inFillColor).grid(row=inLoc[0], column=inLoc[1])


def drawDie(inCanvas, inDie=6, inOutlineColor="blue", inFillColor="gray"):
    theCanvas = tk.Canvas(inCanvas)
    if inDie in [0, 1]:  # draw invisible pips to correct grid spacing
        for theLoc in pipLocs[2]:
            drawPipInGrid(theCanvas, theLoc, "white", None)
    if inDie in [0, 2, 4, 6]:  # draw invisible pips to correct grid spacing
        for theLoc in pipLocs[1]:
            drawPipInGrid(theCanvas, theLoc, "white", None)
    for theLoc in pipLocs[inDie]:
        if theLoc:
            drawPipInGrid(theCanvas, theLoc, inOutlineColor, inFillColor)
    inCanvas.bind("<ButtonPress>", onMouseDownInDie)
    theCanvas.bind("<ButtonPress>", onMouseDownInDie)
    return theCanvas


def drawTheDominoDivider(inCanvas, theOrientation=tk.HORIZONTAL, inFillColor="gray"):
    # return ttk.Separator(inCanvas, orient=theOrientation)
    if theOrientation == tk.HORIZONTAL:
        theCanvas = tk.Canvas(inCanvas, width=1, height=51)
        theCanvas.create_rectangle(2, 5, 3, 50, fill=inFillColor)
    else:
        theCanvas = tk.Canvas(inCanvas, width=51, height=1)
        theCanvas.create_rectangle(5, 2, 50, 3, fill=inFillColor)
    return theCanvas


def drawDomino(
    inCanvas,
    inDomino=[5, 6],
    inOrientation=tk.HORIZONTAL,
    inOutlineColor="blue",
    inFillColor="gray",
):
    theCanvas = tk.Canvas(inCanvas)
    theFrame = tk.Frame(theCanvas, bd=4, bg=inOutlineColor, relief=tk.GROOVE)
    theFrame.grid()  # pack(fill=tk.BOTH, padx=1, pady=1)

    if inOrientation == tk.HORIZONTAL:
        drawDie(theFrame, inDomino[0]).grid(row=0, column=0)
        drawTheDominoDivider(theFrame, inOrientation).grid(row=0, column=1)
        drawDie(theFrame, inDomino[1]).grid(row=0, column=2)
        theCanvas.grid(columnspan=3)
    else:
        drawDie(theFrame, inDomino[0]).grid(row=0, column=0)
        drawTheDominoDivider(theFrame, inOrientation).grid(row=1, column=0)
        drawDie(theFrame, inDomino[1]).grid(row=2, column=0)
        theCanvas.grid(rowspan=3)
    return theCanvas


junk = """
      5
      -
      6
2     6
-[2,6]-[6,3][3,1]
2     6
      6
      -
      4
"""  # noqa: F841


def demoPlay():
    theWindow = tk.Toplevel()
    theWindow.title("demoPlay")
    drawDomino(theWindow, [6, 6], tk.VERTICAL).grid(row=3, column=5)
    drawDomino(theWindow, [6, 3], tk.HORIZONTAL).grid(row=4, column=6)
    drawDomino(theWindow, [2, 6], tk.HORIZONTAL).grid(row=4, column=1)
    drawDomino(theWindow, [2, 2], tk.VERTICAL).grid(row=3, column=0)
    drawDomino(theWindow, [3, 1], tk.HORIZONTAL).grid(row=4, column=9)
    drawDomino(theWindow, [5, 6], tk.VERTICAL).grid(row=0, column=5)
    drawDomino(theWindow, [6, 4], tk.VERTICAL).grid(row=6, column=5)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Claussoft Dominos")
    # drawDomino(root).pack()
    for i in range(7):
        for j in range(7):
            if not i > j:
                drawDomino(root, [i, j]).grid(row=j, column=i * 3)
                # theRow = j*3
                # if not theRow:
                #    theRow = 1
                # theColumn = i*3
                # if i and i == j:
                #    theRow -= 1
                #    #theColumn -= 1
                # if i == j:
                #    theOrientation = tk.VERTICAL
                # else:
                #    theOrientation = tk.HORIZONTAL
                # drawDomino(root, [i, j], theOrientation).grid(row=theRow, column=theColumn)
    demoPlay()
    root.mainloop()
