#!/usr/bin/env python3

# from random import shuffle
# from sys import argv
# from ask_number_from_one_to import ask_number_from_one_to
# import tkinter as tk
# from PlayedDomino import printPlayedDominos
# from drawDomino import drawDomino
# from tkDomino import tkDominoBoard
from typing import List, Tuple
from PlayedDomino import PlayedDomino


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
    def z_get_value(self) -> int:
        return sum(d.played_value for d in self.played_dominos)

    @property
    def z_get_points(self) -> int:
        value = self.z_get_value
        return 0 if value % 5 else value // 5

    def pick_from_boneyard(self):
        # not clear what the rule is for other values of self.max_die
        bones_available = len(self.boneyard) > (2 if self.max_die == 6 else 0)
        return self.boneyard.pop() if bones_available else None

    @property
    def z_playable_numbers(self) -> List[int]:
        if not self.played_dominos:
            return list(range(self.max_die + 1))
        number_list: List = []  # adding lists, not .append()
        for d in self.played_dominos:
            number_list += d.playable_numbers
        return sorted(set(number_list))

    def z_playable_dominos(self, domino: List[int]) -> List[PlayedDomino]:
        playable_dominos = []  # Python 3.8 walrus operator might help here
        for d in self.played_dominos:
            pn = d.playable_numbers
            if domino[0] in pn or domino[1] in pn:
                playable_dominos.append(d)
        return playable_dominos

    def z_is_domino_playable(self, domino: List[int]) -> bool:
        if not self.played_dominos:
            return True  # on an empty board, all dominos are playable
        for d in self.played_dominos:
            pn = d.playable_numbers
            if domino[0] in pn or domino[1] in pn:
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

    def z_set_locations(self):
        if not self.played_dominos:
            return
        for d in self.played_dominos:
            d.location = None
        self.played_dominos[0].location = [0, 0]
        horiz = []
        verts = []
        for d in self.played_dominos:
            if not d.location:  # for all but firstPlayedDomino
                d.set_location()
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
        return z_build_canvas(canvasDimensions)

    def z_set_tk_locations(self):
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

    def z_fill_canvas(self, inCanvas: List[List[str]]) -> None:
        for domino in self.played_dominos:
            domino.fill_canvas(inCanvas)

    @property
    def z_location_list(self):
        return [d.location for d in self.played_dominos]

    def z_print_played_dominos(self):
        if not self.played_dominos:
            return
        canvas = self.set_locations()
        self.fill_canvas(canvas)
        z_print_canvas(tuple(canvas))
        del canvas
        s = "Playable: {}, Value: {}"
        print(s.format(self.playable_numbers, self.get_value))


def z_build_canvas(dimensions: Tuple[int, int]) -> List[List[str]]:
    canvas: List = []
    for j in range(dimensions[1] + 5):
        canvas.append([])
        for _ in range(dimensions[0] + 5):
            canvas[j].append(" ")
    return canvas


def z_print_canvas(canvas: Tuple[List[str]]) -> None:
    lines = ["".join(line).rstrip() for line in canvas]
    longest_line = max(len(line) for line in lines)
    border = "=" * longest_line
    print(border)
    print("\n".join(line for line in lines if line))
    print(border)


if __name__ == "__main__":
    from DominoWorld import main

    main()
