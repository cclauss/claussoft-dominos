#!/usr/bin/env python3

from os import getenv
from random import shuffle
import tkinter as tk
# from sys import argv
# from askNumberFromOneTo import askNumberFromOneTo
# from PlayedDomino import PlayedDomino
from DominoPlayer import DominoPlayer
from DominoBoard import DominoBoard
from drawDomino import drawDomino
from tkDomino import tkDominoBoard


gPassesInARow = 0
# dominos = tuple((x, y) for x in range(7) for y in range(x + 1))


def initDominos(inMaxDie=6):
    return [[x, y] for x in range(inMaxDie + 1) for y in range(x + 1)]


"""
def ZZinitDominos(inMaxDie=6):
    theDominos = []
    for i in range(inMaxDie + 1):
        for j in range(i, inMaxDie + 1):
            theDominos.append([i, j])
    return theDominos
"""


def pointsRounded(inValue, n=5):
    return int(round((inValue + n // 2) // n))


"""
def ZZpointsRounded(inValue):
    return inValue / 5 + int(inValue % 5 > 2)

# for i in range(20):
#    print(i, pointsRounded(i), ZZpointsRounded(i))
"""
"""
# tkinter offsets when playing one domino next to the other
# (self_horiz, other_horiz): (LEFT, RIGHT, UP, DOWN)
# None: if self and other are both horizontal then UP and DOWN are invalid
#       if self and other are both vertical then LEFT and RIGHT are invalid
TK_OFFSETS = {(True, True): ((-3, 0), (3, 0), None, None),
                (True, False): ((-1, -1), (3, -1), (1, -3), (1, 1)),
                (False, True): ((-3, 1), (1, 1), (-1, -1), (-1, 3)),
                (False, False): (None, None, (0, -3), (0, 3))}


def tk_offset(self_horiz, other_horiz, direction):
    offset = TK_OFFSETS[(self_horiz, other_horiz)][direction]
    assert offset, f"tk_offset({self_horiz}, {other_horiz}, {direction})"
    return offset
"""

class DominoWorld(tkDominoBoard):
    def __init__(self, inMaxDie=6, inNumberOfPlayers=2):
        print(1, self.__class__.__name__)
        # print(2, self.super())
        # iprint(3, super(DominoBoard))
        # self.super(DominoBoard, self).__init__()
        super().__init__()
        print(2, super().__class__.__name__)
        self.mDominos = initDominos(inMaxDie)
        self.mBoard = DominoBoard(inMaxDie)
        self.mPlayers = [DominoPlayer(f'Player {i}', self.mBoard)
                         for i in range(inNumberOfPlayers)]
        self.mWhoseTurnMajor = 0
        self.mWhoseTurnMinor = 0
        self.mGamesEndingInADraw = 0

    def __str__(self):
        p = ''
        for thePlayer in self.mPlayers:
            p += str(thePlayer) + '\n'
        return p  # + str(self.mBoard)

    def deal(self, inDominosPerPlayer=7):
        self.mBoard.mPlayedDominos = []
        shuffle(self.mDominos)
        shuffle(self.mDominos)
        shuffle(self.mDominos)
        # shuffle(shuffle(shuffle(self.mDominos)))
        d = 0  # start with the first domino.
        for thePlayer in self.mPlayers:
            thePlayer.mDominos = sorted(
                self.mDominos[d:d + inDominosPerPlayer])
            d += inDominosPerPlayer
        self.mBoard.mBoneyard = self.mDominos[d:]
        self.update_ui()

    def reorientDominos(self):
        for d in self.mDominos:
            if d[0] > d[1]:
                d.reverse()

    def playersHaveDominos(self):
        for thePlayer in self.mPlayers:
            if not thePlayer.mDominos:
                return False
        return True
        # all(player.mDominos for player in self.mPlayers)

    def playATurn(self):
        global gPassesInARow
        p = self.mWhoseTurnMinor % len(self.mPlayers)
        # print('playATurn: {} {}'.format(self.mWhoseTurnMinor, p))
        print('=' * 10 + ' NEW TURN ' + '=' * 10)
        if self.mPlayers[p].playATurn():
            gPassesInARow = 0
        else:
            gPassesInARow += 1
        if gPassesInARow > 1:
            for p in self.mPlayers:
                p.mDominos = []
        self.mWhoseTurnMinor += 1
        self.update_ui()

    def playAHand(self):
        self.mWhoseTurnMinor = self.mWhoseTurnMajor
        self.mWhoseTurnMajor += 1
        self.deal()
        # print(self)
        while self.playersHaveDominos():
            self.playATurn()
        totalValue = 0
        for p in self.mPlayers:
            handValue = p.pointsStillHolding()
            totalValue += handValue
            if handValue:
                print(p.handAsString(), 'still holds',
                      handValue, '...', end='')
        for p in self.mPlayers:
            if not p.mDominos:  # the player that won
                p.awardPoints(pointsRounded(totalValue))
                p.mHandsWon += 1
                break
        print()
        theWinner = self.checkForWinner()
        if theWinner and theWinner != -1:
            print('=' * 10 + ' NEW HAND ' + '=' * 10)

    def playAGame(self, inHumanWantsToPlay):
        self.mPlayers[0].mPlayerIsHuman = inHumanWantsToPlay
        # self.mBoard.clearBoard()
        theWinner = None
        while not theWinner:
            self.playAHand()
            self.reorientDominos()
            theWinner = self.checkForWinner()
        if theWinner == -1:
            self.mGamesEndingInADraw += 1
            theWinner = None
        if inHumanWantsToPlay:
            print(self)
        # if theWinner:
        #    for thePlayer in self.mPlayers:
        #        if theWinner == thePlayer.mName:
        #            thePlayer.mGamesWon += 1
        print('The winner is', theWinner)
        return theWinner

    def highestScore(self):
        highScore = 0
        for p in self.mPlayers:
            if p.mPoints > highScore:
                highScore = p.mPoints
        return highScore

    def checkForWinner(self):
        highScore = self.highestScore()
        if highScore < 25:
            return None
        for p in self.mPlayers:
            if p.mPoints == highScore:
                return p.mName

    def update_ui(self):
        # ui = self.mBoard
        # ui.mDropZoneBoneyard
        # ui.mDropZonePlayArea
        # ui.mDropZonePlayer0
        # ui.mDropZonePlayer1
        # ui.mDropZoneScoreBoard
        for i, child in enumerate(self.mDropZoneBoneyard.winfo_children()):
            child.destroy()
        for i, domino in enumerate(self.mBoard.mBoneyard):
            drawDomino(self.mDropZoneBoneyard, domino).grid(row=i)
        uis = (self.mDropZonePlayer0, self.mDropZonePlayer1)
        for player, ui in zip(self.mPlayers, uis):
            for i, child in enumerate(ui.winfo_children()):
                child.destroy()
            for i, domino in enumerate(player.mDominos):
                drawDomino(ui, domino).grid(row=0, column=i*3)
        self.mBoard.set_tk_locations()
        for i, child in enumerate(self.mDropZonePlayArea.winfo_children()):
            child.destroy()
        for d in self.mBoard.mPlayedDominos:
            column, row = d.tk_location
            orientation = tk.HORIZONTAL if d.mLeftRight else tk.VERTICAL
            print("pd>", d, orientation, row, column)
            drawDomino(self.mDropZonePlayArea,
                       d.mDomino, orientation).grid(row=row, column=column)

def main():
    print('Enter 1 to play 100 computer vs. computer games.')
    print('Enter 2 to play 1 human vs. computer game.')
    games_to_play = 2  # askNumberFromOneTo(2)
    humanWantsToPlay = games_to_play != 1
    if not games_to_play:
        games_to_play = 100
    if getenv("TRAVIS"):       # If we are running under Travis CI...
        humanWantsToPlay = False  # computer vs. computer
        games_to_play = 10        # games to play
    dw = DominoWorld()
    while games_to_play:
        games_to_play -= 1
        dw.playAGame(humanWantsToPlay)
    print('=' * 10)
    print(dw)

    # dw = DominoWorld()
    # print(dw)
    # print('==========')
    # dw.playAGame(True)
    # while dw.highestScore() < 25:
    #    print('Spining the bones...')
    # dw.playAHand()
    # dw.reorientDominos()
    # print('==========')
    # print(dw)

if __name__ == '__main__':
    main()
