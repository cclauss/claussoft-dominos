#!/usr/bin/env python3

from askNumberFromOneTo import ask_number_from_one_to
from PlayedDomino import PlayedDomino


class DominoRunMove(object):
    def __init__(self, already_played_domino, to_be_played_simple_domino, points=0):
        self.already_played_domino = already_played_domino
        self.to_be_played_simple_domino = to_be_played_simple_domino
        self.points = points

    def __str__(self):
        msg = ""
        if self.points:
            msg = f"{self.points} points, go again..."
        elif self.to_be_played_simple_domino[0] == self.to_be_played_simple_domino[1]:
            msg = "is a double, go again..."
        s = f"Playing {self.to_be_played_simple_domino}"
        if not self.already_played_domino:
            return f"{s} as firstPlayedDomino {msg}"
        return f"{s} on {self.already_played_domino.domino} {msg}"


class DominoPlayer(object):
    def __init__(self, name, board):
        self.name = name
        self.board = board
        self.points = 0
        self.dominos = []
        self.go_agains = 0
        self.hands_won = 0
        self.games_won = 0
        self.player_is_human = False  # assume humans are not interested in playing
        # self.player_is_human = True

    def __str__(self):
        s = "{} has {} dominos, {} points, {} go agains, {} hands won and {} games won."
        return s.format(
            self.name,
            len(self.dominos),
            self.points,
            self.go_agains,
            self.hands_won,
            self.games_won,
        )

    def hand_as_string(self):
        return f"{self.name}'s hand: {len(self.dominos)} {self.dominos}"

    def award_points(self, points):
        if not points:
            return
        old_points = self.points
        self.points += points
        print(
            "Awarding {} points to {} from {} --> {}.".format(
                points, self.name, old_points, self.points
            )
        )

    @property
    def points_still_holding(self):
        return sum(sum(domino) for domino in self.dominos)

    def is_domino_playable(self, inIndex):
        return self.board.is_domino_playable(self.dominos[inIndex])

    def star_if_playable(self, inIndex):
        return "*" if self.is_domino_playable(inIndex) else ""

    @property
    def can_play(self):  # if not, then goin' to the boneyard...
        return any(self.is_domino_playable(i) for i in range(len(self.dominos)))

    def pick_from_boneyard(self):
        print("Going to the boneyard... ", end="")
        domino = self.board.pick_from_boneyard()
        if not domino:
            print("EMPTY!! Passing to next player.")
            return None
        self.dominos.append(domino)
        print("Got:", domino)
        return domino

    def pick_from_boneyard_until_can_play(self):
        while not self.can_play:
            if not self.pick_from_boneyard():
                return False  # Can not play and boneyard is empty
        return True  # Can play

    def undo(self):  # "A domino laid is a domino played." -- anon
        if not self.board.played_dominos:
            print("Nothing to undo.")
            return
        player = self.board.played_dominos[-1].player
        if player != self:
            print("Can not undo the move of", player.name)
            return
        self.points -= self.board.get_points
        theDomino = self.board.played_dominos.pop()
        theDomino.notifyNeighborsOfUndo()
        self.dominos.append(theDomino.domino)

    def get_fresh_copy(self, older_domino):
        return self.board.get_fresh_copy(older_domino)

    def print_a_run(self, run):  # a list of DominoRunMoves
        print("playARun() run length:", len(run))
        for i, move in enumerate(run):
            print(i + 1, move)

    def play_a_run(self, run):  # a list of DominoRunMoves
        self.print_a_run(run)
        moves_played = 0
        for move in run:
            go_again = self.play_a_move(move)
            print(self.hand_as_string())
            self.board.print_played_dominos()
            moves_played += 1
            if not go_again:
                break
        s = "ERROR: moves_played {} does not match len(run) {}"
        assert moves_played == len(run), s.format(moves_played, len(run))
        print("RECAP:", end="")
        self.print_a_run(run)
        return go_again

    def play_a_move(self, move):  # a DominoRunMove
        # print(move)
        assert move
        newer_domino = move.to_be_played_simple_domino
        newer_domino = self.dominos.pop(self.dominos.index(newer_domino))
        older_domino = move.already_played_domino
        if older_domino:
            older_domino = self.get_fresh_copy(
                older_domino
            )  # the toughest bug to find!!
            domino = older_domino.newNeighbor(self, newer_domino)
        else:  # firstPlayedDomino
            domino = PlayedDomino(self, newer_domino)
        self.board.played_dominos.append(domino)
        points = self.board.get_points
        self.award_points(points)
        go_again = points or domino.is_double
        if go_again:
            self.go_agains += 1
        # self.board.update_ui()
        return go_again

    def play_a_turn(self):  # returns wasAbleToPlay
        print(self)
        self.board.print_played_dominos()
        if not self.pick_from_boneyard_until_can_play():
            print("Pass!!!")
            return False  # unable to play, passing to next player
        go_again = (
            self.play_a_turn_human_player()
            if self.player_is_human
            else self.play_a_turn_computer_player()
        )
        if go_again:
            print("Go again.")
            return self.play_a_turn()
        print(self)
        return True  # was able to play

    # ===== Human player routines

    # class DominoHumanPlayer(DominoPlayer):
    def play_a_turn_human_player(self):
        newerDomino = self.dominos[self.ask_which_domino_to_play()]
        olderDomino = self.ask_where_to_play(newerDomino)
        return self.play_a_move(DominoRunMove(olderDomino, newerDomino))

    def ask_which_domino_to_play(self, inPrint=True):
        # playable = self.board.playable_numbers()
        theMax = len(self.dominos)
        if inPrint:
            for i in range(theMax):
                print(
                    "{}: {} {}".format(i + 1, self.dominos[i], self.star_if_playable(i))
                )
            print(self.name, "which domino would you like to play?")
        which_domino = ask_number_from_one_to(theMax)
        print("Got:", which_domino)
        if str(which_domino)[0] == "u":
            self.undo()
            return self.ask_which_domino_to_play()
        which_domino -= 1  # askNumber is 1 thru 7 but dominos are 0 thru 6
        if not self.is_domino_playable(which_domino):
            print("Can not play {}!".format(self.dominos[which_domino]))
            return self.ask_which_domino_to_play(False)
        return which_domino

    def ask_where_to_play(self, domino_to_play):
        if not self.board.played_dominos:
            return None  # firstDominoPlayed has no neighbors
        potential_neighbors = self.board.playable_dominos(domino_to_play)
        assert potential_neighbors
        if len(potential_neighbors) == 1:
            return potential_neighbors[0]
        print("Connect {}: to which domino?".format(domino_to_play))
        maximum = len(potential_neighbors)
        for i in range(maximum):
            print("{}: {}".format(i + 1, potential_neighbors[i].domino))
        return potential_neighbors[ask_number_from_one_to(maximum) - 1]

    # ===== Computer player routines

    # class DominoComputerPlayer(DominoPlayer):
    def play_a_turn_computer_player(self):
        # print(self)
        print(self.hand_as_string())
        # print('Playable: {}, Value: {}'.format(playable, self.board.get_value()))
        score, run = self.best_run()
        return self.play_a_run(run)

    def best_run(self):
        """return the most valuable of an exhaustive series of lists of DominoRunMoves"""
        if not self.dominos:
            # going out with goAgain more valuable than not goAgain
            return [12, []]
        best_score_and_run = [0, []]  # theRun is a list of DominoRunMoves
        self.dominos.sort()  # maintain list order across calls to pop() & append()
        for i in range(len(self.dominos)):
            if self.is_domino_playable(i):
                d = self.dominos.pop(i)
                score_and_run = self.best_run_for_domino(d)
                if score_and_run[0] > best_score_and_run[0]:
                    best_score_and_run = score_and_run
                self.dominos.append(d)
                self.dominos.sort()  # pop()/append() will mess up list order
        # print('best_run:', best_score_and_run)
        return best_score_and_run

    def best_run_for_domino_on_empty_board(self, domino):
        keepers = [[0, 0], [0, 5], [5, 0], [5, 5]]
        if domino in keepers:
            return [0, []]  # do not waste keepers on an empty board
        best_score_and_run = [0, []]  # theRun is a list of DominoRunMoves
        score_and_run = self.best_run_for_domino_and_neighbor(domino, None)
        if score_and_run[0] > best_score_and_run[0]:
            best_score_and_run = score_and_run
        return best_score_and_run

    def best_run_for_domino(self, domino):
        if not self.board.played_dominos:
            return self.best_run_for_domino_on_empty_board(domino)
        best_score_and_run = [0, []]  # theRun is a list of DominoRunMoves
        potential_neighbors = self.board.playable_dominos(domino)
        for neighbor in potential_neighbors:
            score_and_run = self.best_run_for_domino_and_neighbor(domino, neighbor)
            if score_and_run[0] > best_score_and_run[0]:
                best_score_and_run = score_and_run
        return best_score_and_run

    def calc_run_score(self):  # (inPoints, inNumberOfDominosPlayed, inFaceValue)
        # the 12 values goAgain above a high faceValue
        return (
            self.board.get_points * 1000 + 12 + self.board.played_dominos[-1].face_value
        )

    def best_run_for_domino_and_neighbor(self, in_domino, neighbor):
        if neighbor:
            domino = neighbor.newNeighbor(self, in_domino)
        else:
            domino = PlayedDomino(self, in_domino)
        best_score_and_run = [0, []]  # run is a list of DominoRunMoves
        self.board.played_dominos.append(domino)
        score = self.calc_run_score()
        run = [DominoRunMove(neighbor, in_domino, self.board.get_points)]
        if score > best_score_and_run[0]:
            best_score_and_run = [score, run]
        if domino.is_double or self.board.get_points:
            score_and__run = self.best_run()  # go again
            score_and__run[0] += score
            if score_and__run[0] > best_score_and_run[0]:
                best_score_and_run[0] = score_and__run[0]
                best_score_and_run[1] = run + score_and__run[1]
        self.board.played_dominos.pop().notifyNeighborsOfUndo()
        return best_score_and_run


if __name__ == "__main__":
    from DominoWorld import main

    main()
