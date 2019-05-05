#!/usr/bin/env python3

#           2          4     5
# [0,1][1,2]-[2,3][3,4]-[4,5]-
#           2          4     5
#           2
#           -
#           5
#

# from random import choice, shuffle
# import tkinter as tk
# from sys import argv
# from askNumberFromOneTo import askNumberFromOneTo
# from PrintableDomino import lrNoDoublesOffset, lrMeDoubleOffset, lrOtherDoubleOffset, udNoDoublesOffset, udMeDoubleOffset,
# udOtherDoubleOffset
# from random import choice

# print(argv)


def lrNoDoublesOffset(inDirection):
    # print('lrNoDoublesOffset({})'.format(inDirection), end='')
    return [[-5, 0], [5, 0], [0, 0], [0, 0]][inDirection]


def lrMeDoubleOffset(inDirection):
    # print('lrMeDoubleOffset({})'.format(inDirection), end='')
    return [[-5, 0], [5, 0], [2, -3], [2, 1]][inDirection]


def lrOtherDoubleOffset(inDirection):
    # print('lrOtherDoubleOffset({})'.format(inDirection), end='')
    return [[-1, -1], [5, -1], [0, 0], [0, 0]][inDirection]


def udNoDoublesOffset(inDirection):
    # print('udNoDoublesOffset({})'.format(inDirection), end='')
    return [[0, 0], [0, 0], [0, -3], [0, 3]][inDirection]


def udMeDoubleOffset(inDirection):
    # print('udMeDoubleOffset({})'.format(inDirection), end='')
    return [[-5, +1], [1, 1], [0, -3], [0, 3]][inDirection]


def udOtherDoubleOffset(inDirection):
    # print('udOtherDoubleOffset({})'.format(inDirection), end='')
    return [[0, 0], [0, 0], [-2, -1], [-2, 3]][inDirection]

cLeft, cRight, cUp, cDown = range(4)
LEFT_RIGHT = (cLeft, cRight)
UP_DOWN = (cUp, cDown)


def oppositeDirection(inDirection):
    return {cLeft: cRight, cRight: cLeft, cUp: cDown, cDown: cUp}[inDirection]


def rightAngles(inDirection):
    return UP_DOWN if inDirection in LEFT_RIGHT else LEFT_RIGHT


def whichDie(inDirection):
    return inDirection in (cRight, cDown)


class PlayedDomino(object):

    def __init__(self, inPlayer, inDomino, inNeighbor=None, inDirection=cLeft):
        self.mPlayer = inPlayer
        self.mDomino = inDomino
        self.mLocation = [0, 0]
        self.mLeftRight = inDirection in LEFT_RIGHT
        if self.isDouble():
            self.mLeftRight = not self.mLeftRight
        if self.mLeftRight:
            self.mOrientation = tk.HORIZONTAL
        else:
            self.mOrientation = tk.VERTICAL
        oppDir = oppositeDirection(inDirection)
        if inNeighbor:  # flip inDomino if required
            matchToDie = inNeighbor.mDomino[whichDie(inDirection)]
            assert matchToDie in self.mDomino, 'These dominos do not match!'
            if self.mDomino[whichDie(oppDir)] != matchToDie:
                self.mDomino.reverse()
        self.mNeighbors = [None, None, None, None]
        self.mNeighbors[oppDir] = inNeighbor

    def __str__(self):
        s = 'Domino: {}, isD: {}, pd: {}, fv: {}, pv: {}, Neighbors: {}'
        return s.format(self.mDomino, self.isDouble(),
                        self.playableDirections(), self.faceValue(),
                        self.playedValue(), self.mNeighbors)

    def isDouble(self):
        return self.mDomino[0] == self.mDomino[1]

    def faceValue(self):
        return self.mDomino[0] + self.mDomino[1]

    def numberOfNeighbors(self):
        return len(self.mNeighbors) - self.mNeighbors.count(None)

    def neighborAsString(self, inDirection):
        theNeighbor = self.mNeighbors[inDirection]
        return theNeighbor.mDomino if theNeighbor else theNeighbor

    def neighborsAsString(self):
        return [self.neighborAsString(i) for i in range(len(self.mNeighbors))]

    def playedValue(self):
        neighborCount = self.numberOfNeighbors()
        if neighborCount > 1:  # already boxed in
            return 0
        if self.isDouble() or not neighborCount:  # firstDominoPlayed
            return self.faceValue()
        for i in range(len(self.mNeighbors)):
            if self.mNeighbors[i]:
                return self.mDomino[whichDie(oppositeDirection(i))]
        assert True, 'Error in playedValue()!'

    def notifyNeighborsOfUndo(self):  # break neighbors' links to me
        for theDirection in range(len(self.mNeighbors)):
            if self.mNeighbors[theDirection]:
                oppDir = oppositeDirection(theDirection)
                # print('Notify Before:', self.mNeighbors[theDirection].neighborsAsString())
                self.mNeighbors[theDirection].mNeighbors[oppDir] = None
                # print(' Notify After:', self.mNeighbors[theDirection].neighborsAsString())

    def playableDirections(self):
        if self.isDouble():
            return self.playableDirectionsForADouble()
        neighborCount = self.numberOfNeighbors()
        if neighborCount > 1:
            return []
        if not neighborCount:  # firstDominoPlayed
            return LEFT_RIGHT if self.mLeftRight else UP_DOWN
        for i in range(len(self.mNeighbors)):
            if self.mNeighbors[i]:
                return [oppositeDirection(i)]
        assert True, 'Error in playableDirections()!'

    def playableDirectionsForADouble(self):
        neighborCount = self.numberOfNeighbors()
        if neighborCount == 4:
            return []
        if neighborCount == 3:
            return [self.mNeighbors.index(None)]
        if neighborCount == 2:
            for i in range(len(self.mNeighbors)):
                if self.mNeighbors[i]:
                    return rightAngles(i)
        if neighborCount == 1:
            for i in range(len(self.mNeighbors)):
                if self.mNeighbors[i]:
                    return [oppositeDirection(i)]
        if not neighborCount:  # firstDominoPlayed
            if self.mLeftRight:
                return rightAngles(cLeft)
            else:
                return rightAngles(cUp)
        assert True, 'Error in playableDirectionsForADouble()!'

    def playableNumbers(self):
        returnValue = []
        for dir in self.playableDirections():
            returnValue.append(self.mDomino[whichDie(dir)])
        return sorted(list(set(returnValue)))

    def newNeighbor(self, inPlayer, inDomino):
        playableDirections = self.playableDirections()
        assert playableDirections
        if self.isDouble():
            theDirection = choice(playableDirections)
        else:
            theDirection = playableDirections[0]
            if len(playableDirections) > 1:
                if self.mDomino[1] in inDomino:
                    theDirection = playableDirections[1]
        d = PlayedDomino(inPlayer, inDomino, self, theDirection)
        self.mNeighbors[theDirection] = d
        # print('newN Older:', self.mDomino, self.neighborsAsString())
        # print('newN Newer:',    d.mDomino,    d.neighborsAsString())
        return d

    def getOffset(self, inDomino, inDirection):
        if self.mLeftRight:
            if self.isDouble():
                return lrMeDoubleOffset(inDirection)
            elif inDomino.isDouble():
                return lrOtherDoubleOffset(inDirection)
            else:
                return lrNoDoublesOffset(inDirection)
        else:
            if self.isDouble():
                return udMeDoubleOffset(inDirection)
            elif inDomino.isDouble():
                return udOtherDoubleOffset(inDirection)
            else:
                return udNoDoublesOffset(inDirection)

    def dominoAndLoc(self):
        return self.mDomino, '@', self.mLocation

    def dominoAndLocAndNeighbors(self):
        return self.mDomino, '@', self.mLocation, 'n:', self.neighborsAsString()

    def setLocation(self):
        for i in range(len(self.mNeighbors)):
            theNeighbor = self.mNeighbors[i]
            if theNeighbor and theNeighbor.mLocation:
                oppDir = oppositeDirection(i)
                self.mLocation = theNeighbor.getOffset(self, oppDir)
                self.mLocation[0] += theNeighbor.mLocation[0]
                self.mLocation[1] += theNeighbor.mLocation[1]
                return

    def fillCanvas(self, inCanvas):
        # print(self.mDomino, '@', self.mLocation, self.neighborsAsString())
        if self.mLeftRight:
            s = str(self.mDomino).replace(' ', '')
            for i in range(len(s)):
                inCanvas[self.mLocation[1]][self.mLocation[0] + i] = s[i]
        else:
            inCanvas[self.mLocation[1] +
                     0][self.mLocation[0]] = str(self.mDomino[0])
            inCanvas[self.mLocation[1] + 1][self.mLocation[0]] = '-'
            inCanvas[self.mLocation[1] +
                     2][self.mLocation[0]] = str(self.mDomino[1])

if __name__ == '__main__':
    # from DominoTest import main
    from DominoWorld import main
    main()
