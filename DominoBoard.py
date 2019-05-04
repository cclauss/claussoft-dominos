#!/usr/bin/env python3

# from random import shuffle
# from sys import argv
# from askNumberFromOneTo import askNumberFromOneTo
# import tkinter as tk
# from PlayedDomino import printPlayedDominos
from tkDomino import tkDominoBoard


class DominoBoard(tkDominoBoard):

    def __init__(self, inMaxDie=6):
        print(1, self.__class__)
        # print(2, self.super())
        # iprint(3, super(DominoBoard))
        # self.super(DominoBoard, self).__init__()
        # super().__init__()
        self.mMaxDie = inMaxDie
        self.mBoneyard = []
        self.mPlayedDominos = []

    def __str__(self):
        s = '{} dominos in {} = {}\nPlayable numbers: {}, value = {}\n{}'
        return s.format(len(self.mBoneyard), 'Boneyard', self.mBoneyard,
                        self.playableNumbers(), self.getValue(), self.mPlayedDominos)

    def getValue(self):
        a = sum(d.playedValue() for d in self.mPlayedDominos)
        returnValue = 0
        for d in self.mPlayedDominos:
            returnValue += d.playedValue()
        assert a == returnValue
        return returnValue

    def getPoints(self):
        theValue = self.getValue()
        return 0 if theValue % 5 else theValue / 5

    def pickFromBoneyard(self):
        # not clear what the rule is for other values of self.mMaxDie
        bones_available = len(self.mBoneyard) > (2 if self.mMaxDie == 6 else 0)
        return self.mBoneyard.pop() if bones_available else None

    def playableNumbers(self):
        if not self.mPlayedDominos:
            return range(self.mMaxDie + 1)
        returnValue = []
        for d in self.mPlayedDominos:
            returnValue += d.playableNumbers()
        return sorted(list(set(returnValue)))

    def playableDominos(self, inDomino):
        returnValue = []
        for d in self.mPlayedDominos:
            pn = d.playableNumbers()
            if inDomino[0] in pn or inDomino[1] in pn:
                returnValue.append(d)
        return returnValue

    def isDominoPlayable(self, inDomino):
        if not self.mPlayedDominos:
            return True  # on an empty board, all dominos are playable
        for d in self.mPlayedDominos:
            pn = d.playableNumbers()
            if inDomino[0] in pn or inDomino[1] in pn:
                return True
        return False

    def getFreshCopy(self, inOlderDomino):
        if inOlderDomino in self.mPlayedDominos:
            # print('freshCopy NOT required')
            return inOlderDomino
        print('freshCopy WAS required')
        for d in self.mPlayedDominos:
            if d.mDomino == inOlderDomino.mDomino:
                return d
        assert True

    def setLocations(self):
        if not self.mPlayedDominos:
            return
        for d in self.mPlayedDominos:
            d.mLocation = None
        self.mPlayedDominos[0].mLocation = [0, 0]
        horiz = []
        verts = []
        for d in self.mPlayedDominos:
            if not d.mLocation:  # for all but firstPlayedDomino
                d.setLocation()
            horiz.append(d.mLocation[0])
            verts.append(d.mLocation[1])
        assert min(horiz) < 1
        assert min(verts) < 1
        hOffset = abs(min(horiz))
        vOffset = abs(min(verts))
        if hOffset or vOffset:
            for d in self.mPlayedDominos:
                d.mLocation[0] += hOffset
                d.mLocation[1] += vOffset
        canvasDimensions = [(max(horiz) - min(horiz)) + 5,
                            (max(verts) - min(verts)) + 3]
        return buildCanvas(canvasDimensions)

    def fillCanvas(self, inCanvas):
        for theDomino in self.mPlayedDominos:
            theDomino.fillCanvas(inCanvas)

    def locationList(self):
        theList = []
        for d in self.mPlayedDominos:
            theList.append(d.mLocation)
        return theList

    def printPlayedDominos(self):
        if not self.mPlayedDominos:
            return
        theCanvas = self.setLocations()
        self.fillCanvas(theCanvas)
        printCanvas(theCanvas)
        del theCanvas
        s = 'Playable: {}, Value: {}'
        print(s.format(self.playableNumbers(), self.getValue()))


def buildCanvas(inDimensions):
    theCanvas = []
    for j in range(inDimensions[1] + 5):
        theCanvas.append([])
        for i in range(inDimensions[0] + 5):
            theCanvas[j].append(' ')
    return theCanvas


def printCanvas(inCanvas):
    i = 0
    theMax = 0
    for theLine in inCanvas:
        theLine = ''.join(theLine).rstrip()
        if len(theLine) > theMax:
            theMax = len(theLine)
    border = ('=' * 33)[:theMax]
    print(border)
    for theLine in inCanvas:
        s = ''.join(theLine).rstrip()
        if s:
            print(s)  # ,' <',i
        i += 1
    print(border)

if __name__ == '__main__':
    from DominoWorld import main
    main()
