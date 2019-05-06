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
# from askNumberFromOneTo import askNumberFromOneTo
# from PrintableDomino import lrNoDoublesOffset, lrMeDoubleOffset, lrOtherDoubleOffset, udNoDoublesOffset, udMeDoubleOffset,
# udOtherDoubleOffset
from random import choice

# print(argv)
LEFT, RIGHT, UP, DOWN = range(4)
LEFT_RIGHT = (LEFT, RIGHT)
UP_DOWN = (UP, DOWN)


def oppositeDirection(direction):
    return {LEFT: RIGHT, RIGHT: LEFT, UP: DOWN, DOWN: UP}[direction]


def rightAngles(direction):
    return UP_DOWN if direction in LEFT_RIGHT else LEFT_RIGHT


def whichDie(direction):
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


def tk_offset(self_horiz, other_horiz, direction):
    offset = TK_OFFSETS[(self_horiz, other_horiz)][direction]
    assert offset, f"tk_offset({self_horiz}, {other_horiz}, {direction})"
    return offset


class PlayedDomino(object):
    def __init__(self, inPlayer, inDomino, inNeighbor=None, inDirection=LEFT):
        self.mPlayer = inPlayer
        self.mDomino = inDomino
        self.mLocation = [0, 0]
        self.tk_location = [0, 0]
        self.mLeftRight = inDirection in LEFT_RIGHT
        if self.is_double:
            self.mLeftRight = not self.mLeftRight
        self.mOrientation = tk.HORIZONTAL if self.mLeftRight else tk.VERTICAL
        oppDir = oppositeDirection(inDirection)
        if inNeighbor:  # flip inDomino if required
            matchToDie = inNeighbor.mDomino[whichDie(inDirection)]
            assert matchToDie in self.mDomino, "These dominos do not match!"
            if self.mDomino[whichDie(oppDir)] != matchToDie:
                self.mDomino.reverse()
        self.mNeighbors = [None, None, None, None]
        self.mNeighbors[oppDir] = inNeighbor

    def __str__(self):
        s = "Domino: {}, isD: {}, pd: {}, fv: {}, pv: {}, Neighbors: {}"
        return s.format(
            self.mDomino,
            self.is_double,
            self.playable_directions,
            self.face_value,
            self.played_value,
            self.mNeighbors,
        )

    @property
    def is_double(self):
        return self.mDomino[0] == self.mDomino[1]

    @property
    def face_value(self):
        return self.mDomino[0] + self.mDomino[1]

    @property
    def number_of_neighbors(self):
        return len(self.mNeighbors) - self.mNeighbors.count(None)

    def neighborAsString(self, inDirection):
        theNeighbor = self.mNeighbors[inDirection]
        return theNeighbor.mDomino if theNeighbor else theNeighbor

    @property
    def neighbors_as_string(self):
        return [self.neighborAsString(i) for i in range(len(self.mNeighbors))]

    @property
    def played_value(self):
        neighborCount = self.number_of_neighbors
        if neighborCount > 1:  # already boxed in
            return 0
        if self.is_double or not neighborCount:  # firstDominoPlayed
            return self.face_value
        for i, neighbor in enumerate(self.mNeighbors):
            if neighbor:
                return self.mDomino[whichDie(oppositeDirection(i))]
        assert False, "Error in played_value!"

    def notifyNeighborsOfUndo(self):  # break neighbors' links to me
        for theDirection in range(len(self.mNeighbors)):
            if self.mNeighbors[theDirection]:
                oppDir = oppositeDirection(theDirection)
                # print('Notify Before:', self.mNeighbors[theDirection].neighbors_as_string)
                self.mNeighbors[theDirection].mNeighbors[oppDir] = None
                # print(' Notify After:', self.mNeighbors[theDirection].neighbors_as_string)

    @property
    def playable_directions(self):
        if self.is_double:
            return self.playable_directions_for_a_double
        neighborCount = self.number_of_neighbors
        if neighborCount > 1:  # already boxed in
            return []
        if not neighborCount:  # firstDominoPlayed
            return LEFT_RIGHT if self.mLeftRight else UP_DOWN
        for i, neighbor in enumerate(self.mNeighbors):
            if neighbor:
                return [oppositeDirection(i)]
        assert True, "Error in playable_directions!"

    @property
    def playable_directions_for_a_double(self):
        neighborCount = self.number_of_neighbors
        if neighborCount == 4:
            return []
        if neighborCount == 3:
            return [self.mNeighbors.index(None)]
        if neighborCount == 2:
            for i, neighbor in enumerate(self.mNeighbors):
                if neighbor:
                    return rightAngles(i)
        if neighborCount == 1:
            for i in range(len(self.mNeighbors)):
                if self.mNeighbors[i]:
                    return [oppositeDirection(i)]
        if not neighborCount:  # firstDominoPlayed
            return rightAngles(LEFT) if self.mLeftRight else rightAngles(UP)
        assert True, "Error in playable_directions_for_a_double!"

    @property
    def playable_numbers(self):
        # print("FIXME:", self.mDomino, self.playable_directions)
        return sorted(
            set(
                self.mDomino[whichDie(direction)]
                for direction in self.playable_directions
            )
        )

    def newNeighbor(self, inPlayer, inDomino):
        playable_directions = self.playable_directions
        assert playable_directions
        if self.is_double:
            theDirection = choice(playable_directions)
        else:
            theDirection = playable_directions[0]
            if len(playable_directions) > 1:
                if self.mDomino[1] in inDomino:
                    theDirection = playable_directions[1]
        d = PlayedDomino(inPlayer, inDomino, self, theDirection)
        self.mNeighbors[theDirection] = d
        # print('newN Older:', self.mDomino, self.neighbors_as_string)
        # print('newN Newer:',    d.mDomino,    d.neighbors_as_string)
        return d

    def getOffset(self, other, inDirection):
        offset = TEXT_OFFSETS[(self.mLeftRight, other.mLeftRight)][inDirection]
        assert (
            offset
        ), f"text_offset({self.mLeftRight}, {other.mLeftRight}, {inDirection})"
        return list(offset)
        """
        if self.mLeftRight:
            if self.is_double:
                return lrMeDoubleOffset(inDirection)
            elif inDomino.is_double:
                return lrOtherDoubleOffset(inDirection)
            else:
                return lrNoDoublesOffset(inDirection)
        else:
            if self.is_double:
                return udMeDoubleOffset(inDirection)
            elif inDomino.is_double:
                return udOtherDoubleOffset(inDirection)
            else:
                return udNoDoublesOffset(inDirection)
        """

    def get_tk_offset(self, other, inDirection):
        offset = TK_OFFSETS[(self.mLeftRight, other.mLeftRight)][inDirection]
        assert (
            offset
        ), f"tk_offset({self.mLeftRight}, {other.mLeftRight}, {inDirection})"
        return list(offset)

    @property
    def domino_and_loc(self):
        return self.mDomino, "@", self.mLocation

    @property
    def domino_and_loc_and_neighbors(self):
        return self.mDomino, "@", self.mLocation, "n:", self.neighbors_as_string

    def setLocation(self):
        for i, theNeighbor in enumerate(self.mNeighbors):
            if theNeighbor and theNeighbor.mLocation:
                self.mLocation = theNeighbor.getOffset(self, oppositeDirection(i))
                self.mLocation[0] += theNeighbor.mLocation[0]
                self.mLocation[1] += theNeighbor.mLocation[1]
                return

    def set_tk_location(self):
        for i, theNeighbor in enumerate(self.mNeighbors):
            if theNeighbor and theNeighbor.tk_location:
                self.tk_location = theNeighbor.get_tk_offset(self, oppositeDirection(i))
                self.tk_location[0] += theNeighbor.tk_location[0]
                self.tk_location[1] += theNeighbor.tk_location[1]
                return

    def fillCanvas(self, inCanvas):
        # print(self.mDomino, '@', self.mLocation, self.neighbors_as_string)
        if self.mLeftRight:
            s = str(self.mDomino).replace(" ", "")
            for i, c in enumerate(s):
                inCanvas[self.mLocation[1]][self.mLocation[0] + i] = c
        else:
            inCanvas[self.mLocation[1] + 0][self.mLocation[0]] = str(self.mDomino[0])
            inCanvas[self.mLocation[1] + 1][self.mLocation[0]] = "-"
            inCanvas[self.mLocation[1] + 2][self.mLocation[0]] = str(self.mDomino[1])


if __name__ == "__main__":
    # from DominoTest import main
    from DominoWorld import main

    main()
