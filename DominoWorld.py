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


g_passes_in_a_row = 0
# dominos = tuple((x, y) for x in range(7) for y in range(x + 1))


def init_dominos(max_die=6):
    return [[x, y] for x in range(max_die + 1) for y in range(x + 1)]


def pointsRounded(value, n=5):
    return int(round((value + n // 2) // n))


class DominoWorld(tkDominoBoard):
    def __init__(self, max_die=6, inNumberOfPlayers=2):
        super().__init__()  # start up tkinter
        self.dominos = init_dominos(max_die)
        assert len(self.dominos) == 28
        assert len(self.dominos) == len(set(self.dominos)), self.dominos
        self.board = DominoBoard(max_die)
        self.players = [
            DominoPlayer(f"Player {i}", self.board) for i in range(inNumberOfPlayers)
        ]
        self.whose_turn_major = 0
        self.whose_turn_minor = 0
        self.games_ending_in_a_draw = 0

    def __str__(self):
        return "\n".join(str(player) for player in self.players)

    def deal(self, inDominosPerPlayer=7):
        self.board.mPlayedDominos = []
        for _ in range(3):
            shuffle(self.dominos)
        d = 0  # start with the first domino.
        for player in self.players:
            player.dominos = sorted(self.dominos[d : d + inDominosPerPlayer])
            d += inDominosPerPlayer
        self.board.mBoneyard = self.dominos[d:]
        self.update_ui()

    def reorientDominos(self):
        for d in self.dominos:
            if d[0] > d[1]:
                d.reverse()

    def playersHaveDominos(self):
        for player in self.players:
            if not player.dominos:
                return False
        return True
        # all(player.dominos for player in self.players)

    def playATurn(self):
        global g_passes_in_a_row
        p = self.whose_turn_minor % len(self.players)
        # print('playATurn: {} {}'.format(self.whose_turn_minor, p))
        print("=" * 10 + " NEW TURN " + "=" * 10)
        if self.players[p].playATurn():
            g_passes_in_a_row = 0
        else:
            g_passes_in_a_row += 1
        if g_passes_in_a_row > 1:  # TODO: Only allow passing once?
            for p in self.players:
                p.dominos = []
        self.whose_turn_minor += 1
        self.update_ui()

    def playAHand(self):
        self.whose_turn_minor = self.whose_turn_major
        self.whose_turn_major += 1
        self.deal()
        # print(self)
        while self.playersHaveDominos():
            self.playATurn()
        total_value = 0
        for p in self.players:
            hand_value = p.pointsStillHolding()
            total_value += hand_value
            if hand_value:
                print(p.handAsString(), "still holds", hand_value, "...", end="")
        for p in self.players:
            if not p.dominos:  # the player that won
                p.awardPoints(pointsRounded(total_value))
                p.mHandsWon += 1
                break
        print()
        winner = self.checkForWinner()
        if winner and winner != -1:
            print("=" * 10 + " NEW HAND " + "=" * 10)

    def playAGame(self, human_wants_to_play):
        self.players[0].mPlayerIsHuman = human_wants_to_play
        # self.board.clearBoard()
        winner = None
        while not winner:
            self.playAHand()
            self.reorientDominos()
            winner = self.checkForWinner()
        if winner == -1:
            self.games_ending_in_a_draw += 1
            winner = None
        if human_wants_to_play:
            print(self)
        # if winner:
        #    for thePlayer in self.players:
        #        if winner == thePlayer.mName:
        #            thePlayer.mGamesWon += 1
        print("The winner is", winner)
        return winner

    @property
    def highest_score(self):
        return max(player.mPoints for player in self.players)

    def checkForWinner(self):
        high_score = self.highest_score
        if high_score < 25:
            return None
        for p in self.players:
            if p.mPoints == high_score:
                return p.mName

    def update_ui(self):
        # ui = self.board
        # ui.mDropZoneBoneyard
        # ui.mDropZonePlayArea
        # ui.mDropZonePlayer0
        # ui.mDropZonePlayer1
        # ui.mDropZoneScoreBoard
        for i, child in enumerate(self.mDropZoneBoneyard.winfo_children()):
            child.destroy()
        for i, domino in enumerate(self.board.mBoneyard):
            drawDomino(self.mDropZoneBoneyard, domino).grid(row=i)
        uis = (self.mDropZonePlayer0, self.mDropZonePlayer1)
        for player, ui in zip(self.players, uis):
            for i, child in enumerate(ui.winfo_children()):
                child.destroy()
            for i, domino in enumerate(player.dominos):
                drawDomino(ui, domino).grid(row=0, column=i * 3)
        self.board.set_tk_locations()
        for i, child in enumerate(self.mDropZonePlayArea.winfo_children()):
            child.destroy()
        for d in self.board.mPlayedDominos:
            column, row = d.tk_location
            orientation = tk.HORIZONTAL if d.mLeftRight else tk.VERTICAL
            # print("pd>", d, orientation, row, column)
            drawDomino(self.mDropZonePlayArea, d.mDomino, orientation).grid(
                row=row, column=column
            )


def main():
    print("Enter 1 to play 100 computer vs. computer games.")
    print("Enter 2 to play 1 human vs. computer game.")
    games_to_play = 2  # askNumberFromOneTo(2)
    human_wants_to_play = games_to_play != 1
    if not games_to_play:
        games_to_play = 100
    if getenv("TRAVIS"):  # If we are running under Travis CI...
        human_wants_to_play = False  # computer vs. computer
        games_to_play = 10  # games to play
    dw = DominoWorld()
    while games_to_play:
        games_to_play -= 1
        dw.playAGame(human_wants_to_play)
    print("=" * 10)
    print(dw)

    # dw = DominoWorld()
    # print(dw)
    # print('==========')
    # dw.playAGame(True)
    # while dw.highest_score < 25:
    #    print('Spining the bones...')
    # dw.playAHand()
    # dw.reorientDominos()
    # print('==========')
    # print(dw)


if __name__ == "__main__":
    main()
