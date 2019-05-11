#!/usr/bin/env python3

#           2          4     5
# [0,1][1,2]-[2,3][3,4]-[4,5]-
#           2          4     5
#           2
#           -
#           5
#

# from random import choice, shuffle
import tkinter as tk

# from sys import argv
# from ask_number_from_one_to import ask_number_from_one_to
# from PrintableDomino import lrNoDoublesOffset, lrMeDoubleOffset, lrOtherDoubleOffset, udNoDoublesOffset, udMeDoubleOffset,
# udOtherDoubleOffset
from random import choice
from typing import Dict, List, Optional

# from DominoPlayer import DominoPlayer

# print(argv)
LEFT, RIGHT, UP, DOWN = range(4)
LEFT_RIGHT = (LEFT, RIGHT)
UP_DOWN = (UP, DOWN)


def opposite_direction(direction):
    return {LEFT: RIGHT, RIGHT: LEFT, UP: DOWN, DOWN: UP}[direction]


def right_angles(direction):
    return UP_DOWN if direction in LEFT_RIGHT else LEFT_RIGHT


def which_die(direction):
    return direction in (RIGHT, DOWN)


# Text offsets when playing one domino next to the other
# (self_horiz, other_horiz): (LEFT, RIGHT, UP, DOWN)
# None: if self and other are both horizontal then UP and DOWN are invalid
#       if self and other are both vertical then LEFT and RIGHT are invalid
TEXT_OFFSETS = {
    (True, True): ((-5, 0), (5, 0), None, None),
    (True, False): ((-1, -1), (5, -1), (2, -3), (2, 1)),
    (False, True): ((-5, 1), (1, 1), (-2, -1), (-2, 3)),
    (False, False): (None, None, (0, -3), (0, 3)),
}


# tkinter offsets when playing one domino next to the other
# (self_horiz, other_horiz): (LEFT, RIGHT, UP, DOWN)
# None: if self and other are both horizontal then UP and DOWN are invalid
#       if self and other are both vertical then LEFT and RIGHT are invalid
TK_OFFSETS = {
    (True, True): ((-3, 0), (3, 0), None, None),
    (True, False): ((-1, -1), (3, -1), (1, -3), (1, 1)),
    (False, True): ((-3, 1), (1, 1), (-1, -1), (-1, 3)),
    (False, False): (None, None, (0, -3), (0, 3)),
}


class PlayedDomino(object):
    def __init__(
        self,
        player,
        domino,
        neighbor: Optional["PlayedDomino"] = None,
        direction: int = LEFT,
    ) -> None:
        self.player = player
        self.domino = domino
        self.location: List[int] = [0, 0]
        self.tk_location: List[int] = [0, 0]
        self.left_right: bool = direction in LEFT_RIGHT
        if self.is_double:
            self.left_right = not self.left_right
        self.orientation: str = tk.HORIZONTAL if self.left_right else tk.VERTICAL
        opp_dir = opposite_direction(direction)
        if neighbor:  # flip inDomino if required
            match_to_die = neighbor.domino[which_die(direction)]
            assert match_to_die in self.domino, "These dominos do not match!"
            if self.domino[which_die(opp_dir)] != match_to_die:
                self.domino.reverse()
        self.neighbors: List[Optional["PlayedDomino"]] = [None, None, None, None]
        self.neighbors[opp_dir] = neighbor

    def __str__(self) -> str:
        s = "Domino: {}, isD: {}, pd: {}, fv: {}, pv: {}, Neighbors: {}"
        return s.format(
            self.domino,
            self.is_double,
            self.playable_directions,
            self.face_value,
            self.played_value,
            self.neighbors,
        )

    @property
    def two_str(self) -> str:
        """For domino (5, 6), return '56'"""
        return "{}{}".format(*self.domino)

    @property
    def as_dict(self) -> Dict[str, Dict[str, str]]:
        """Return {self.two_str: dict of all neighbors plus orientation}"""
        keys = "left right up down".split()
        d = {key: n.two_str for key, n in zip(keys, self.neighbors) if n}
        d["orientation"] = self.orientation
        return {self.two_str: d}

    @property
    def is_double(self) -> bool:
        return self.domino[0] == self.domino[1]

    @property
    def face_value(self) -> int:
        return self.domino[0] + self.domino[1]

    @property
    def number_of_neighbors(self) -> int:
        return len(self.neighbors) - self.neighbors.count(None)

    def neighbor_as_string(self, inDirection) -> str:
        theNeighbor = self.neighbors[inDirection]
        return theNeighbor.domino if theNeighbor else theNeighbor

    @property
    def neighbors_as_string(self) -> List[str]:
        return [self.neighbor_as_string(i) for i in range(len(self.neighbors))]

    @property
    def played_value(self) -> int:
        neighbor_count = self.number_of_neighbors
        if neighbor_count > 1:  # already boxed in
            return 0
        if self.is_double or not neighbor_count:  # firstDominoPlayed
            return self.face_value
        for i, neighbor in enumerate(self.neighbors):
            if neighbor:
                return self.domino[which_die(opposite_direction(i))]
        assert False, "Error in played_value!"

    def notify_neighbors_of_undo(self) -> None:  # break neighbors' links to me
        for theDirection in range(len(self.neighbors)):
            if self.neighbors[theDirection]:
                oppDir = opposite_direction(theDirection)
                # print('Notify Before:', self.neighbors[theDirection].neighbors_as_string)
                self.neighbors[theDirection].neighbors[oppDir] = None  # type: ignore
                # print(' Notify After:', self.neighbors[theDirection].neighbors_as_string)

    @property
    def playable_directions(self) -> List[int]:
        if self.is_double:
            return self.playable_directions_for_a_double
        neighborCount = self.number_of_neighbors
        if neighborCount > 1:  # already boxed in
            return []
        if not neighborCount:  # firstDominoPlayed
            return list(LEFT_RIGHT if self.left_right else UP_DOWN)
        for i, neighbor in enumerate(self.neighbors):
            if neighbor:
                return [opposite_direction(i)]
        assert True, "Error in playable_directions!"
        return []  # Placate mypy

    @property
    def playable_directions_for_a_double(self) -> List[int]:
        neighborCount = self.number_of_neighbors
        if neighborCount == 4:
            return []
        if neighborCount == 3:
            return [self.neighbors.index(None)]
        if neighborCount == 2:
            for i, neighbor in enumerate(self.neighbors):
                if neighbor:
                    return list(right_angles(i))
        if neighborCount == 1:
            for i in range(len(self.neighbors)):
                if self.neighbors[i]:
                    return [opposite_direction(i)]
        if not neighborCount:  # firstDominoPlayed
            return right_angles(LEFT) if self.left_right else right_angles(UP)
        assert True, "Error in playable_directions_for_a_double!"
        return []  # Placate mypy

    @property
    def playable_numbers(self) -> List[int]:
        return sorted(
            set(
                self.domino[which_die(direction)]
                for direction in self.playable_directions
            )
        )

    def new_neighbor(self, player, domino: List[int]) -> "PlayedDomino":
        playable_directions = self.playable_directions
        assert playable_directions
        if self.is_double:
            direction = choice(playable_directions)
        else:
            direction = playable_directions[0]
            if len(playable_directions) > 1:
                if self.domino[1] in domino:
                    direction = playable_directions[1]
        d = PlayedDomino(player, domino, self, direction)
        self.neighbors[direction] = d
        # print('newN Older:', self.domino, self.neighbors_as_string)
        # print('newN Newer:',    d.domino,    d.neighbors_as_string)
        return d

    def get_offset(self, other: "PlayedDomino", inDirection: int) -> List[int]:
        offset = TEXT_OFFSETS[(self.left_right, other.left_right)][inDirection]
        assert (
            offset
        ), f"text_offset({self.left_right}, {other.left_right}, {inDirection})"
        return list(offset)

    def get_tk_offset(self, other: "PlayedDomino", inDirection: int) -> List[int]:
        offset = TK_OFFSETS[(self.left_right, other.left_right)][inDirection]
        assert (
            offset
        ), f"tk_offset({self.left_right}, {other.left_right}, {inDirection})"
        return list(offset)

    @property
    def domino_and_loc(self) -> str:
        return f"{self.domino} @ {self.location}"

    @property
    def domino_and_loc_and_neighbors(self) -> str:
        return f"{self.domino} @ {self.location} n: {self.neighbors_as_string}"

    def set_location(self) -> None:
        for i, neighbor in enumerate(self.neighbors):
            if neighbor and neighbor.location:
                self.location = neighbor.get_offset(self, opposite_direction(i))
                self.location[0] += neighbor.location[0]
                self.location[1] += neighbor.location[1]
                return

    def set_tk_location(self) -> None:
        for i, neighbor in enumerate(self.neighbors):
            if neighbor and neighbor.tk_location:
                self.tk_location = neighbor.get_tk_offset(self, opposite_direction(i))
                self.tk_location[0] += neighbor.tk_location[0]
                self.tk_location[1] += neighbor.tk_location[1]
                return

    def fill_canvas(self, canvas: List[List[str]]) -> None:
        # print(self.domino, '@', self.location, self.neighbors_as_string)
        if self.left_right:
            s = str(self.domino).replace(" ", "")
            for i, c in enumerate(s):
                canvas[self.location[1]][self.location[0] + i] = c
        else:  # type: ignore
            for i, s in enumerate((self.domino[0], "-", self.domino[1])):
                canvas[self.location[1] + i][self.location[0]] = str(s)


if __name__ == "__main__":
    # from DominoTest import main
    from DominoWorld import main

    main()
