#!/usr/bin/env python3

# from random import shuffle
# from sys import argv
# from askNumberFromOneTo import askNumberFromOneTo
# import tkinter as tk
# from PlayedDomino import printPlayedDominos
# from drawDomino import drawDomino
# from tkDomino import tkDominoBoard


class DominoBoard:
    def __init__(self, max_die=6):
        # print(1, self.__class__.__name__)
        # print(2, self.super())
        # iprint(3, super(DominoBoard))
        # self.super(DominoBoard, self).__init__()
        # super().__init__()
        # print(2, super().__class__.__name__)
        self.max_die = max_die
        self.boneyard = []
        self.played_dominos = []

    def __str__(self):
        s = "{} dominos in {} = {}\nPlayable numbers: {}, value = {}\n{}"
        return s.format(
            len(self.boneyard),
            "Boneyard",
            self.boneyard,
            self.playable_numbers,
            self.get_value,
            self.played_dominos,
        )

    @property
    def get_value(self):
        return sum(d.played_value for d in self.played_dominos)

    @property
    def get_points(self):
        theValue = self.get_value
        return 0 if theValue % 5 else theValue / 5

    def pick_from_boneyard(self):
        # not clear what the rule is for other values of self.max_die
        bones_available = len(self.boneyard) > (2 if self.max_die == 6 else 0)
        return self.boneyard.pop() if bones_available else None

    @property
    def playable_numbers(self):
        if not self.played_dominos:
            return range(self.max_die + 1)
        number_list = []
        for d in self.played_dominos:
            number_list += d.playable_numbers
        return sorted(set(number_list))

    def playable_dominos(self, inDomino):
        returnValue = []
        for d in self.played_dominos:
            pn = d.playable_numbers
            if inDomino[0] in pn or inDomino[1] in pn:
                returnValue.append(d)
        return returnValue

    def is_domino_playable(self, inDomino):
        if not self.played_dominos:
            return True  # on an empty board, all dominos are playable
        for d in self.played_dominos:
            pn = d.playable_numbers
            if inDomino[0] in pn or inDomino[1] in pn:
                return True
        return False

    def get_fresh_copy(self, in_older_domino):
        if in_older_domino in self.played_dominos:
            # print('freshCopy NOT required')
            return in_older_domino
        print("freshCopy WAS required")
        for d in self.played_dominos:
            if d.mDomino == in_older_domino.mDomino:
                return d
        assert True

    def set_locations(self):
        if not self.played_dominos:
            return
        for d in self.played_dominos:
            d.mLocation = None
        self.played_dominos[0].mLocation = [0, 0]
        horiz = []
        verts = []
        for d in self.played_dominos:
            if not d.mLocation:  # for all but firstPlayedDomino
                d.setLocation()
            horiz.append(d.mLocation[0])
            verts.append(d.mLocation[1])
        assert min(horiz) < 1
        assert min(verts) < 1
        hOffset = abs(min(horiz))
        vOffset = abs(min(verts))
        if hOffset or vOffset:
            for d in self.played_dominos:
                d.mLocation[0] += hOffset
                d.mLocation[1] += vOffset
        canvasDimensions = [
            (max(horiz) - min(horiz)) + 5,
            (max(verts) - min(verts)) + 3,
        ]
        return build_canvas(canvasDimensions)

    def set_tk_locations(self):
        if not self.played_dominos:
            return
        for d in self.played_dominos:
            d.tk_location = None
        self.played_dominos[0].tk_location = [0, 0]
        horiz = []
        verts = []
        for d in self.played_dominos:
            if not d.tk_location:  # for all but firstPlayedDomino
                d.set_tk_location()
            horiz.append(d.tk_location[0])
            verts.append(d.tk_location[1])
        assert min(horiz) < 1
        assert min(verts) < 1
        hOffset = abs(min(horiz))
        vOffset = abs(min(verts))
        if hOffset or vOffset:
            for d in self.played_dominos:
                d.tk_location[0] += hOffset
                d.tk_location[1] += vOffset

    def fill_canvas(self, inCanvas):
        for theDomino in self.played_dominos:
            theDomino.fillCanvas(inCanvas)

    @property
    def location_list(self):
        return [d.mLocation for d in self.played_dominos]

    def print_played_dominos(self):
        if not self.played_dominos:
            return
        theCanvas = self.set_locations()
        self.fill_canvas(theCanvas)
        print_canvas(theCanvas)
        del theCanvas
        s = "Playable: {}, Value: {}"
        print(s.format(self.playable_numbers, self.get_value))


def build_canvas(dimensions):
    canvas = []
    for j in range(dimensions[1] + 5):
        canvas.append([])
        for _ in range(dimensions[0] + 5):
            canvas[j].append(" ")
    return canvas


def print_canvas(canvas):
    lines = ["".join(line).rstrip() for line in canvas]
    longest_line = max(len(line) for line in lines)
    border = "=" * longest_line
    print(border)
    print("\n".join(line for line in lines if line))
    print(border)


if __name__ == "__main__":
    from DominoWorld import main

    main()
