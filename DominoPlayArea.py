#!/usr/bin/env python3

# from random import shuffle
# from sys import argv
# from ask_number_from_one_to import ask_number_from_one_to
# import tkinter as tk
# from PlayedDomino import printPlayedDominos
# from drawDomino import drawDomino
# from tkDomino import tkDominoBoard
from typing import List, Tuple

# from DominoBoard import DominoBoard
from PlayedDomino import PlayedDomino

""" Removed:
pick_from_boneyard
get_fresh_copy
"""


class DominoPlayArea:
    def __init__(self, domino_board: "DominoBoard"):
        self.domino_board = domino_board
        self.played_dominos: List[PlayedDomino] = []

    def __str__(self):
        return (
            f"Playable numbers: {self.playable_numbers}, value = {self.get_value}\n"
            f"{self.played_dominos}"
        )

    def refresh(self, played_dominos: List[PlayedDomino]) -> int:
        self.played_dominos = played_dominos
        self.print_played_dominos()
        self.set_tk_locations()
        print(self)  # TODO: Remove this in production
        return self.get_value

    @property
    def get_value(self) -> int:
        return sum(d.played_value for d in self.played_dominos)

    @property
    def get_points(self) -> int:
        value = self.get_value
        return 0 if value % 5 else value // 5

    @property
    def playable_numbers(self) -> List[int]:
        if not self.played_dominos:
            return list(range(self.domino_board.max_die + 1))
        number_list: List = []  # adding lists, not .append()
        for d in self.played_dominos:
            number_list += d.playable_numbers
        return sorted(set(number_list))

    def playable_dominos(self, domino: List[int]) -> List[PlayedDomino]:
        playable_dominos = []  # Python 3.8 walrus operator might help here
        for d in self.played_dominos:
            pn = d.playable_numbers
            if domino[0] in pn or domino[1] in pn:
                playable_dominos.append(d)
        return playable_dominos

    def is_domino_playable(self, domino: List[int]) -> bool:
        if not self.played_dominos:
            return True  # on an empty board, all dominos are playable
        for d in self.played_dominos:
            pn = d.playable_numbers
            if domino[0] in pn or domino[1] in pn:
                return True
        return False

    def set_locations(self):
        if not self.played_dominos:
            return
        for domino in self.played_dominos:
            domino.location = None
        self.played_dominos[0].location = [0, 0]
        horiz = []
        verts = []
        for domino in self.played_dominos:
            if not domino.location:  # for all but firstPlayedDomino
                domino.set_location()
            horiz.append(domino.location[0])
            verts.append(domino.location[1])
        assert min(horiz) < 1
        assert min(verts) < 1
        h_offset = abs(min(horiz))
        v_offset = abs(min(verts))
        if h_offset or v_offset:
            for domino in self.played_dominos:
                domino.location[0] += h_offset
                domino.location[1] += v_offset
        dimensions = tuple(
            [(max(horiz) - min(horiz)) + 5, (max(verts) - min(verts)) + 3]
        )
        return build_canvas(dimensions)

    def set_tk_locations(self):
        if not self.played_dominos:
            return
        for domino in self.played_dominos:
            domino.tk_location = None
        self.played_dominos[0].tk_location = [0, 0]
        horiz = []
        verts = []
        for domino in self.played_dominos:
            if not domino.tk_location:  # for all but firstPlayedDomino
                domino.set_tk_location()
            horiz.append(domino.tk_location[0])
            verts.append(domino.tk_location[1])
        assert min(horiz) < 1
        assert min(verts) < 1
        h_offset = abs(min(horiz))
        v_offset = abs(min(verts))
        if h_offset or v_offset:
            for domino in self.played_dominos:
                domino.tk_location[0] += h_offset
                domino.tk_location[1] += v_offset

    def fill_canvas(self, inCanvas: List[List[str]]) -> None:
        for domino in self.played_dominos:
            domino.fill_canvas(inCanvas)

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


def build_canvas(dimensions: Tuple[int, int]) -> List[List[str]]:
    canvas: List = []
    for j in range(dimensions[1] + 5):
        canvas.append([])
        for _ in range(dimensions[0] + 5):
            canvas[j].append(" ")
    return canvas


def print_canvas(canvas: Tuple[List[str]]) -> None:
    lines = ["".join(line).rstrip() for line in canvas]
    longest_line = max(len(line) for line in lines)
    border = "=" * longest_line
    print(border)
    print("\n".join(line for line in lines if line))
    print(border)


if __name__ == "__main__":
    from DominoBoard import DominoBoard

    # from DominoWorld import main
    # main()
    LEFT, RIGHT, UP, DOWN = range(4)
    from DominoPlayer import DominoPlayer

    board = DominoBoard(max_die=6)
    player = DominoPlayer("test dummy", board)
    played_dominos = [PlayedDomino(player, [6, 4])]
    play_area = DominoPlayArea(board)
    play_area.refresh(played_dominos)
    played_dominos.append(PlayedDomino(player, [6, 6], played_dominos[0], LEFT))
    play_area.refresh(played_dominos)
    played_dominos.append(PlayedDomino(player, [4, 3], played_dominos[0], RIGHT))
    play_area.refresh(played_dominos)
    played_dominos.append(PlayedDomino(player, [2, 6], played_dominos[1], LEFT))
    play_area.refresh(played_dominos)
    played_dominos.append(PlayedDomino(player, [5, 6], played_dominos[0], UP))
    play_area.refresh(played_dominos)
