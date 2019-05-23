#!/usr/bin/env python3

import tkinter as tk
from typing import List

# from tkinter import ttk


def on_mouse_down_in_die(event):
    print("on_mouse_down_in_die:", (event.x, event.y), event.widget)


# The locations of the dots on a 3x3 grid.
pip_locations: List[List[List[int]]] = [
    [[]],
    [[1, 1]],
    [[0, 0], [2, 2]],
    [[0, 0], [1, 1], [2, 2]],
    [[0, 0], [0, 2], [2, 0], [2, 2]],
    [[0, 0], [0, 2], [1, 1], [2, 0], [2, 2]],
    [[0, 0], [0, 1], [0, 2], [2, 0], [2, 1], [2, 2]],
]


def pip_canvas(in_canvas, outline: str = "blue", fill: str = "gray") -> tk.Canvas:
    canvas = tk.Canvas(in_canvas, width=13, height=13)
    canvas.create_oval(3, 3, 13, 13, outline=outline, fill=fill)
    return canvas


def draw_pip_in_grid(
    in_canvas, location: List[int], outline: str = "blue", fill: str = "gray"
) -> tk.Canvas:
    return pip_canvas(in_canvas, outline, fill).grid(
        row=location[0], column=location[1]
    )


def draw_die(
    in_canvas, die: int = 6, outline: str = "blue", fill: str = "gray"
) -> tk.Canvas:
    canvas = tk.Canvas(in_canvas)
    if die in (0, 1):  # draw invisible pips to correct grid spacing
        for location in pip_locations[2]:
            draw_pip_in_grid(canvas, location, "white", "")
    if die in (0, 2, 4, 6):  # draw invisible pips to correct grid spacing
        for location in pip_locations[1]:
            draw_pip_in_grid(canvas, location, "white", "")
    for location in pip_locations[die]:
        if location:
            draw_pip_in_grid(canvas, location, outline, fill)
    in_canvas.bind("<ButtonPress>", on_mouse_down_in_die)
    canvas.bind("<ButtonPress>", on_mouse_down_in_die)
    return canvas


def draw_domino_divider(
    in_canvas, orientation=tk.HORIZONTAL, fill: str = "gray"
) -> tk.Canvas:
    # return ttk.Separator(in_canvas, orient=orientation)
    if orientation == tk.HORIZONTAL:
        canvas = tk.Canvas(in_canvas, width=1, height=51)
        canvas.create_rectangle(2, 5, 3, 50, fill=fill)
    else:
        canvas = tk.Canvas(in_canvas, width=51, height=1)
        canvas.create_rectangle(5, 2, 50, 3, fill=fill)
    return canvas


def draw_domino(
    in_canvas,
    domino: List[int] = [5, 6],
    orientation: str = tk.HORIZONTAL,
    outline: str = "blue",
    fill: str = "gray",
) -> tk.Canvas:
    canvas = tk.Canvas(in_canvas)
    frame = tk.Frame(canvas, bd=4, bg=outline, relief=tk.GROOVE)
    frame.grid()  # pack(fill=tk.BOTH, padx=1, pady=1)

    if orientation == tk.HORIZONTAL:
        draw_die(frame, domino[0]).grid(row=0, column=0)
        draw_domino_divider(frame, orientation).grid(row=0, column=1)
        draw_die(frame, domino[1]).grid(row=0, column=2)
        canvas.grid(columnspan=3)
    else:
        draw_die(frame, domino[0]).grid(row=0, column=0)
        draw_domino_divider(frame, orientation).grid(row=1, column=0)
        draw_die(frame, domino[1]).grid(row=2, column=0)
        canvas.grid(rowspan=3)
    return canvas


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


def demo_play() -> None:
    window = tk.Toplevel()
    window.title("demo_play")
    draw_domino(window, [6, 6], tk.VERTICAL).grid(row=3, column=5)
    draw_domino(window, [6, 3], tk.HORIZONTAL).grid(row=4, column=6)
    draw_domino(window, [2, 6], tk.HORIZONTAL).grid(row=4, column=1)
    draw_domino(window, [2, 2], tk.VERTICAL).grid(row=3, column=0)
    draw_domino(window, [3, 1], tk.HORIZONTAL).grid(row=4, column=9)
    draw_domino(window, [5, 6], tk.VERTICAL).grid(row=0, column=5)
    draw_domino(window, [6, 4], tk.VERTICAL).grid(row=6, column=5)
    window.lift()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Claussoft Dominos")
    # drawDomino(root).pack()
    for i in range(7):
        for j in range(7):
            if not i > j:
                draw_domino(root, [i, j]).grid(row=j, column=i * 3)
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
                # drawDomino(root, [i, j], theOrientation).grid(row=theRow,
                #                                               column=theColumn)
    demo_play()
    root.lower()  # put demo on top
    root.mainloop()
