#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
from tkinter import dnd  # type: ignore
from typing import Any, Tuple

from drawDomino import draw_domino


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

    def __init__(
        self, master, width: int = 101, height: int = 100, bg_color: str = "lightblue"
    ) -> None:
        """uses tkinter.dnd to enable Draggables to be Drag and Dropped."""
        self.master = master
        # if not inHeight:
        height or int(9 / 16 * width)  # HiDef aspect ratio is 9/16
        tk.Canvas.__init__(self, master, width=width, height=height, bg=bg_color)
        self.dnd_id = None
        self.grid()

    def dnd_accept(self, inSource, inEvent):
        # print('dnd_accept:', inEvent)
        return self

    def dnd_enter(self, source, event) -> None:
        # print('dnd_enter:', inEvent)
        self.focus_set()  # Show highlight border
        x, y = source.where(self, event)
        # inSource.canvas.bbox(inSource.window_id)
        x1, y1, x2, y2 = source.window_coords()
        width = x2 - x1
        height = y2 - y1
        self.dnd_id = self.create_rectangle(x, y, x + width, y + height)
        self.dnd_motion(source, event)

    def dnd_motion(self, source, event) -> None:
        # print('dnd_motion:', inEvent)
        x, y = source.where(self, event)
        x1, y1, x2, y2 = self.bbox(self.dnd_id)
        self.move(self.dnd_id, x - x1, y - y1)

    def dnd_leave(self, source, event) -> None:
        # print('dnd_leave:', inEvent)
        self.master.focus_set()  # Hide highlight border
        self.delete(self.dnd_id)
        self.dnd_id = None

    def dnd_commit(self, source, event) -> None:
        # print('dnd_commit:', inEvent)
        self.dnd_leave(source, event)
        x, y = source.where(self, event)
        source.attach(self, x, y)

    def arrange(self) -> None:
        children = self.find_all()
        if len(children) == 1:
            self.arrange_first()
            return
        if int(self["width"]) > int(self["height"]):
            orientation = tk.HORIZONTAL
            longer_dimension = int(self["width"])
        else:
            orientation = tk.VERTICAL
            longer_dimension = int(self["height"])

        padding = max(10, (longer_dimension - len(children) * 75) / 2)
        for i, child in enumerate(children):
            if orientation == tk.HORIZONTAL:
                self.coords(child, padding + i * 75, 10)
            else:
                self.coords(child, 10, padding + i * 75)

            # print(self.type(child), self.coords(child) # window [10.0, 10.0])
            # print(self, child, 'arrange child i:', i)
            # .4453228272.4457567080.4457567152 1 arrange child i: 0
            # print(self.show_config())
            # print('{} children in {}x{}'.format(len(self.children), self['width'], self.cget('height')))
            # 1 children in 1024x128
            # print(self.configure('width, -height'))

    def arrange_first(self) -> None:
        first_child = self.find_all()[0]
        # first_child.orientation = tk.HORIZONTAL
        longer_dimension = int(self["width"])
        padding = (longer_dimension - 75) / 2
        self.coords(first_child, padding, 10)

    def show_config(self) -> str:
        output = (str(self.config(key)) for key in sorted(self.config()))
        return "\t" + "\n\t".join(output)


class LabeledDropTarget(DropTarget):
    """LabeledDropTarget(inMaster, inName, inWidth=100, inHeight=100, inBgColor='lightblue')
    Proved less useful than originally thought."""

    def __init__(
        self, master, width: int = 101, height: int = 100, bg_color: str = "lightblue"
    ) -> None:
        theLabelframe = ttk.Labelframe(master, text=width, labelanchor=tk.N)
        theLabelframe.grid()
        DropTarget.__init__(
            self, theLabelframe, width=height, height=height, bg_color=bg_color
        )


def grid_slave_bind_propogate(in_slave, bind_type, callback) -> None:
    # print('theSlave:', str(type(theSlave)))
    in_slave.bind(bind_type, callback)
    for slave in in_slave.grid_slaves():
        grid_slave_bind_propogate(slave, bind_type, callback)


def build_a_domino(master, name: str = "[5, 6]", orientation: str = tk.VERTICAL):
    domino = eval(name)
    assert len(domino) == 2
    return draw_domino(master, domino, orientation)


def my_draw_routine(
    master, name: str = "????", orientation: str = tk.VERTICAL
) -> ttk.Label:
    return ttk.Label(master, text=name, borderwidth=2, relief=tk.RAISED)


class Draggable(object):
    """Draggable(inName): uses tkinter.dnd to enable the widget (self.widget_id) to be Drag and
    Dropped into DropTargets.  attach() must be called to initially add your Draggable to
    a DropTarget.  The widget will need to be modified to meet specific requirements.
    """

    def __init__(self, name, orientation=tk.VERTICAL, draw_routine=my_draw_routine):
        self.name = name
        self.orientation = orientation
        self.draw_routine = draw_routine
        self.canvas: Any = None
        self.widget_id: Any = None
        self.window_id = None
        self.x_offset: int = 0
        self.y_offset: int = 0
        self.x_origin: int = 0
        self.y_origin: int = 0

    def attach(self, canvas: tk.Canvas, x: int = 10, y: int = 10) -> None:
        # print('attach:', self.canvas, inCanvas)
        if canvas is self.canvas:
            self.canvas.coords(self.window_id, x, y)
            self.canvas.arrange()
            return
        if self.canvas:
            self.detach()
        if not canvas:
            return
        self.canvas = canvas
        # print('attach2:', self.canvas, inCanvas)
        # self.widget_id = ttk.Label(self.canvas, text=self.name, borderwidth=2,
        #                      relief="raised")
        self.widget_id = self.draw_routine(self.canvas, self.name, self.orientation)
        self.window_id = self.canvas.create_window(
            x, y, window=self.widget_id, anchor="nw"
        )
        # self.widget_id.grid(row=0, column=0)
        # self.widget_id.bind('<ButtonPress>', self.onMouseDown)
        grid_slave_bind_propogate(self.widget_id, "<ButtonPress>", self.onMouseDown)
        self.canvas.arrange()

        # self.canvas.bind("<ButtonPress>", self.onMouseDown)
        _ = """
        print(self.canvas, 'widget_id:', self.canvas.bbox(self.widget_id))
        print(self.canvas, 'window_id:', self.canvas.bbox(self.window_id))
        i = 0
        for theChild in self.canvas.children:
            print(self.canvas, 'child i:', i, self.canvas.bbox(theChild))
            i += 1

        i = 0
        for theSlave in inCanvas.grid_slaves():
            print(inCanvas, 'slave i:', i)
            #print(inCanvas)
            theSlave.grid(row=0, column=i)
            i += 1
         """

    def detach(self) -> None:
        # print('detach:', self.canvas)
        if not self.canvas:
            return
        self.canvas.delete(self.window_id)
        self.widget_id.destroy()
        self.canvas = self.widget_id = self.window_id = None

    def onMouseDown(self, event) -> None:
        # print('onMouseDown:', (event.x, event.x), event.widget)
        if dnd.dnd_start(self, event):
            # where the pointer is relative to the label widget:
            self.x_offset = event.x
            self.y_offset = event.y
            # where the widget is relative to the canvas:
            self.x_origin, self.y_origin = self.canvas.coords(self.window_id)

    def move(self, event) -> None:
        x, y = self.where(self.canvas, event)
        self.canvas.coords(self.window_id, x, y)

    def putback(self) -> None:
        self.canvas.coords(self.window_id, self.x_origin, self.y_origin)

    def where(self, canvas, event) -> Tuple[int, int]:
        # where the corner of the canvas is relative to the screen:
        x_origin = canvas.winfo_rootx()
        y_origin = canvas.winfo_rooty()
        # where the pointer is relative to the canvas widget:
        x = event.x_root - x_origin
        y = event.y_root - y_origin
        # compensate for initial pointer offset
        return x - self.x_offset, y - self.y_offset

    def window_coords(self):
        return self.canvas.bbox(self.window_id)

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
    t2 = LabeledDropTarget(top2, "Labelframe")

    top3 = tk.Toplevel(root)
    top3.geometry("+240+80")
    t3 = DropTarget(top3, width=1280, height=720)
    top3.geometry("1280x720")

    i1 = Draggable("ICON1")
    i2 = Draggable("ICON2", my_draw_routine)
    d1 = Draggable("[1,2]", build_a_domino)
    d2 = Draggable("[2,3]", build_a_domino)
    d3 = Draggable("[3,4]", build_a_domino)
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


if __name__ == "__main__":
    main()
