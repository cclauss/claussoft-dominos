#!/usr/bin/env python3

# from random import shuffle
# from sys import argv
# from ask_number_from_one_to import ask_number_from_one_to
# import tkinter as tk
# from PlayedDomino import printPlayedDominos
# from drawDomino import drawDomino
# from tkDomino import tkDominoBoard
from typing import Iterable, List, Tuple


class DominoBoard:
    def __init__(self, max_die: int = 6):
        self.max_die = max_die
        self.boneyard: List = []
        self.played_dominos: List = []

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
    def get_value(self) -> int:
        return sum(d.played_value for d in self.played_dominos)

    @property
    def get_points(self) -> int:
        value = self.get_value
        return 0 if value % 5 else value // 5

    def pick_from_boneyard(self):
        # not clear what the rule is for other values of self.max_die
        bones_available = len(self.boneyard) > (2 if self.max_die == 6 else 0)
        return self.boneyard.pop() if bones_available else None

    @property
    def playable_numbers(self) -> Iterable:
        if not self.played_dominos:
            return range(self.max_die + 1)
        number_list: List = []  # adding lists, not .append()
        for d in self.played_dominos:
            number_list += d.playable_numbers
        return sorted(set(number_list))

    def playable_dominos(self, inDomino: List) -> List:
        returnValue = []  # Python 3.8 walrus operator might help here
        for d in self.played_dominos:
            pn = d.playable_numbers
            if inDomino[0] in pn or inDomino[1] in pn:
                returnValue.append(d)
        return returnValue

    def is_domino_playable(self, inDomino: List) -> bool:
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
            if d.domino == in_older_domino.domino:
                return d
        assert True

    def set_locations(self):
        if not self.played_dominos:
            return
        for d in self.played_dominos:
            d.location = None
        self.played_dominos[0].location = [0, 0]
        horiz = []
        verts = []
        for d in self.played_dominos:
            if not d.location:  # for all but firstPlayedDomino
                d.setLocation()
            horiz.append(d.location[0])
            verts.append(d.location[1])
        assert min(horiz) < 1
        assert min(verts) < 1
        hOffset = abs(min(horiz))
        vOffset = abs(min(verts))
        if hOffset or vOffset:
            for d in self.played_dominos:
                d.location[0] += hOffset
                d.location[1] += vOffset
        canvasDimensions = tuple(
            [(max(horiz) - min(horiz)) + 5, (max(verts) - min(verts)) + 3]
        )
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

    def fill_canvas(self, inCanvas: List):
        for theDomino in self.played_dominos:
            theDomino.fillCanvas(inCanvas)

    @property
    def location_list(self):
        return [d.location for d in self.played_dominos]

    def print_played_dominos(self):
        if not self.played_dominos:
            return
        canvas = self.set_locations()
        self.fill_canvas(canvas)
        print_canvas(tuple(canvas))
        del canvas
        s = "Playable: {}, Value: {}"
        print(s.format(self.playable_numbers, self.get_value))


def build_canvas(dimensions: Tuple):
    canvas: List = []
    for j in range(dimensions[1] + 5):
        canvas.append([])
        for _ in range(dimensions[0] + 5):
            canvas[j].append(" ")
    return canvas


def print_canvas(canvas: Tuple):
    lines = ["".join(line).rstrip() for line in canvas]
    longest_line = max(len(line) for line in lines)
    border = "=" * longest_line
    print(border)
    print("\n".join(line for line in lines if line))
    print(border)


if __name__ == "__main__":
    from DominoWorld import main

    main()
