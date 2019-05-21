#!/usr/bin/env python3

# from itertools import combinations_with_replacement
from datetime import datetime as dt
from os import getenv
from random import shuffle
import tkinter as tk

# from time import sleep
from typing import Dict, List

import toml

# from sys import argv
# from ask_number_from_one_to import ask_number_from_one_to
# from PlayedDomino import PlayedDomino
from DominoPlayer import DominoPlayer
from DominoBoard import DominoBoard

# from DominoPlayArea import DominoPlayArea
from drawDomino import draw_domino
from tkDomino import tkDominoBoard


g_passes_in_a_row = 0
# dominos = tuple((x, y) for x in range(7) for y in range(x + 1))


def init_dominos(max_die: int = 6) -> List:
    # return sorted(itertools.combinations_with_replacement(range(7), 2))
    return [[x, y] for x in range(max_die + 1) for y in range(x + 1)]


def pointsRounded(value: int, n: int = 5) -> int:
    return int(round((value + n // 2) // n))


def dump_to_toml_file(data: Dict, filepath: str = "") -> None:
    if not data or not toml:
        return
    filepath = filepath or f"dominos_{dt.today():%Y_%m_%d_%H_%M_%S}.toml"
    with open(filepath, "w") as out_file:
        toml.dump(data, out_file)


class DominoWorld(tkDominoBoard):
    def __init__(self, max_die: int = 6, inNumberOfPlayers: int = 2):
        super().__init__()  # start up tkinter
        # self.max_die = max_die
        self.dominos = init_dominos(max_die)
        assert len(self.dominos) == 28  # a few quick sanity checks
        assert all(self.dominos.count(d) == 1 for d in self.dominos), self.dominos
        assert len(self.dominos) == len(set(str(d) for d in self.dominos)), self.dominos
        self.board = DominoBoard(max_die)
        #  self.boneyard: List = []
        # self.play_area = DominoPlayArea(self)
        # self.played_dominos: List = []
        self.players = [
            DominoPlayer(f"Player {i}", self.board) for i in range(inNumberOfPlayers)
        ]

        self.whose_turn_major = 0
        self.whose_turn_minor = 0
        self.games_ending_in_a_draw = 0

    def __str__(self) -> str:
        return "\n".join(str(player) for player in self.players)

    # @property
    # def play_area(self) -> DominoPlayArea:
    #     return self.board.play_area

    def detect_counterfeits(self):
        """Verify the number of dominos are currently being held by
           players + played on the board + in the boneyard"""
        holders = [player.dominos for player in self.players]
        holders += [self.board.played_dominos, self.board.boneyard]
        lengths = [len(holder) for holder in holders]
        assert sum(lengths) == len(self.dominos), (lengths, len(self.dominos))

    def deal(self, inDominosPerPlayer: int = 7):
        self.board.played_dominos = []
        for _ in range(3):
            shuffle(self.dominos)
        assert len(self.dominos) == 28
        d = 0  # start with the first domino.
        for player in self.players:
            player.dominos = sorted(self.dominos[d : d + inDominosPerPlayer])
            d += inDominosPerPlayer
        self.board.boneyard = self.dominos[d:]
        self.detect_counterfeits()
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
        if self.players[p].play_a_turn():
            g_passes_in_a_row = 0
        else:
            g_passes_in_a_row += 1
        self.detect_counterfeits()
        if g_passes_in_a_row > 1:  # TODO: Only allow passing once?
            for player in self.players:
                player.dominos = []
        self.whose_turn_minor += 1
        self.update_ui()
        if not getenv("TRAVIS"):
            # sleep(2)
            input("Ready? ")  # Allow human to see tkinter window

    def playAHand(self):
        self.whose_turn_minor = self.whose_turn_major
        self.whose_turn_major += 1
        self.deal()
        # print(self)
        while self.playersHaveDominos():
            self.playATurn()
        total_value = 0
        for player in self.players:
            hand_value = player.points_still_holding
            total_value += hand_value
            if hand_value:
                print(player.hand_as_string(), "still holds", hand_value, "...", end="")
        for player in self.players:
            if not player.dominos:  # the player that won
                player.award_points(pointsRounded(total_value))
                player.hands_won += 1
                break
        print()
        domino_dicts = {}
        for domino in self.board.played_dominos:
            domino_dicts.update(domino.as_dict)
        dump_to_toml_file(domino_dicts)
        winner = self.checkForWinner()
        if winner and winner != -1:
            print("=" * 10 + " NEW HAND " + "=" * 10)

    def playAGame(self, human_wants_to_play: bool):
        self.players[0].player_is_human = human_wants_to_play
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
        #        if winner == thePlayer.name:
        #            thePlayer.games_won += 1
        print("The winner is", winner)
        return winner

    @property
    def highest_score(self):
        return max(player.points for player in self.players)

    def checkForWinner(self):
        high_score = self.highest_score
        if high_score < 25:
            return None
        for p in self.players:
            if p.points == high_score:
                return p.name

    def update_ui(self):
        for i, child in enumerate(self.drop_zone_boneyard.winfo_children()):
            child.destroy()
        for i, domino in enumerate(self.board.boneyard):
            draw_domino(self.drop_zone_boneyard, domino).grid(row=i)
        uis = (self.drop_zone_player0, self.drop_zone_player1)
        for player, ui in zip(self.players, uis):
            for i, child in enumerate(ui.winfo_children()):
                child.destroy()
            for i, domino in enumerate(player.dominos):
                draw_domino(ui, domino).grid(row=0, column=i * 3)
        self.board.set_tk_locations()
        for i, child in enumerate(self.drop_zone_play_area.winfo_children()):
            child.destroy()
        for d in self.board.played_dominos:
            column, row = d.tk_location
            orientation = tk.HORIZONTAL if d.left_right else tk.VERTICAL
            # print("pd>", d, orientation, row, column)
            draw_domino(self.drop_zone_play_area, d.domino, orientation).grid(
                row=row, column=column
            )


def main(human_wants_to_play: bool = True):
    print("Enter 1 to play 100 computer vs. computer games.")
    print("Enter 2 to play 1 human vs. computer game.")
    games_to_play = 2  # ask_number_from_one_to(2)
    # human_wants_to_play = games_to_play != 1
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
    print(f"{dw.games_ending_in_a_draw} games ended in a draw")


if __name__ == "__main__":
    import sys

    main(bool(not sys.argv[1:]))  # any param will force a computer-vs.-computer game
