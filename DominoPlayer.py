#!/usr/bin/env python3

from askNumberFromOneTo import askNumberFromOneTo
from PlayedDomino import PlayedDomino


class DominoRunMove(object):
    def __init__(self, inAlreadyPlayedDomino, inToBePlayedSimpleDomino, inPoints=0):
        self.mAlreadyPlayedDomino = inAlreadyPlayedDomino
        self.mToBePlayedSimpleDomino = inToBePlayedSimpleDomino
        self.mPoints = inPoints

    def __str__(self):
        theMessage = ""
        if self.mPoints:
            theMessage = "{} points, go again...".format(self.mPoints)
        elif self.mToBePlayedSimpleDomino[0] == self.mToBePlayedSimpleDomino[1]:
            theMessage = "is a double, go again..."
        s = "Playing {}".format(self.mToBePlayedSimpleDomino)
        if not self.mAlreadyPlayedDomino:
            return "{} as firstPlayedDomino {}".format(s, theMessage)
        return "{} on {} {}".format(s, self.mAlreadyPlayedDomino.mDomino, theMessage)


class DominoPlayer(object):
    def __init__(self, inName, inBoard):
        self.mName = inName
        self.mBoard = inBoard
        self.mPoints = 0
        self.mDominos = []
        self.mGoAgains = 0
        self.mHandsWon = 0
        self.mGamesWon = 0
        self.mPlayerIsHuman = False  # assume humans are not interested in playing
        # self.mPlayerIsHuman = True

    def __str__(self):
        s = "{} has {} dominos, {} points, {} go agains, {} hands won and {} games won."
        return s.format(
            self.mName,
            len(self.mDominos),
            self.mPoints,
            self.mGoAgains,
            self.mHandsWon,
            self.mGamesWon,
        )

    def handAsString(self):
        return "{}'s hand: {} {}".format(self.mName, len(self.mDominos), self.mDominos)

    def awardPoints(self, inPoints):
        if not inPoints:
            return
        oldPoints = self.mPoints
        self.mPoints += inPoints
        print(
            "Awarding {} points to {} from {} --> {}.".format(
                inPoints, self.mName, oldPoints, self.mPoints
            )
        )

    def pointsStillHolding(self):
        returnValue = 0
        for d in self.mDominos:
            returnValue += d[0] + d[1]
        return returnValue

    def isDominoPlayable(self, inIndex):
        return self.mBoard.is_domino_playable(self.mDominos[inIndex])

    def starIfPlayable(self, inIndex):
        if self.isDominoPlayable(inIndex):
            return "*"
        return ""

    def canPlay(self):
        for i in range(len(self.mDominos)):
            if self.isDominoPlayable(i):
                return True
        return False  # goin' to the boneyard

    def pickFromBoneyard(self):
        print("Going to the boneyard... ", end="")
        theDomino = self.mBoard.pick_from_boneyard()
        if not theDomino:
            print("EMPTY!! Passing to next player.")
            assert True  # ---------*
            return None
        self.mDominos.append(theDomino)
        print("Got:", theDomino)
        return theDomino

    def pickFromBoneyardUntilCanPlay(self):
        while not self.canPlay():
            if not self.pickFromBoneyard():
                return False  # Can not play and boneyard is empty
        return True  # Can play

    def undo(self):  # "A domino laid is a domino played." -- anon
        if not self.mBoard.played_dominos:
            print("Nothing to undo.")
            return
        thePlayer = self.mBoard.played_dominos[-1].mPlayer
        if thePlayer != self:
            print("Can not undo the move of", thePlayer.mName)
            return
        self.mPoints -= self.mBoard.get_points
        theDomino = self.mBoard.played_dominos.pop()
        theDomino.notifyNeighborsOfUndo()
        self.mDominos.append(theDomino.mDomino)

    def getFreshCopy(self, inOlderDomino):
        return self.mBoard.get_fresh_copy(inOlderDomino)

    def printARun(self, inRun):  # a list of DominoRunMoves
        print("playARun() run length:", len(inRun))
        for i, move in enumerate(inRun):
            print(i + 1, move)

    def playARun(self, inRun):  # a list of DominoRunMoves
        self.printARun(inRun)
        movesPlayed = 0
        for theMove in inRun:
            goAgain = self.playAMove(theMove)
            print(self.handAsString())
            self.mBoard.print_played_dominos()
            movesPlayed += 1
            if not goAgain:
                break
        s = "ERROR: movesPlayed {} does not match len(inRun) {}"
        assert movesPlayed == len(inRun), s.format(movesPlayed, len(inRun))
        print("RECAP:", end="")
        self.printARun(inRun)
        return goAgain

    def playAMove(self, inMove):  # a DominoRunMove
        # print(inMove)
        assert inMove
        newerDomino = inMove.mToBePlayedSimpleDomino
        newerDomino = self.mDominos.pop(self.mDominos.index(newerDomino))
        olderDomino = inMove.mAlreadyPlayedDomino
        if olderDomino:
            olderDomino = self.getFreshCopy(olderDomino)  # the toughest bug to find!!
            theDomino = olderDomino.newNeighbor(self, newerDomino)
        else:  # firstPlayedDomino
            theDomino = PlayedDomino(self, newerDomino)
        self.mBoard.played_dominos.append(theDomino)
        thePoints = self.mBoard.get_points
        self.awardPoints(thePoints)
        goAgain = thePoints or theDomino.is_double
        if goAgain:
            self.mGoAgains += 1
        # self.mBoard.update_ui()
        return goAgain

    def playATurn(self):  # returns wasAbleToPlay
        print(self)
        self.mBoard.print_played_dominos()
        if not self.pickFromBoneyardUntilCanPlay():
            print("Pass!!!")
            return False  # unable to play, passing to next player
        goAgain = (
            self.playATurnHumanPlayer()
            if self.mPlayerIsHuman
            else self.playATurnComputerPlayer()
        )
        if goAgain:
            print("Go again.")
            return self.playATurn()
        print(self)
        return True  # was able to play

    # ===== Human player routines

    # class DominoHumanPlayer(DominoPlayer):
    def playATurnHumanPlayer(self):
        newerDomino = self.mDominos[self.askWhichDominoToPlay()]
        olderDomino = self.askWhereToPlay(newerDomino)
        return self.playAMove(DominoRunMove(olderDomino, newerDomino))

    def askWhichDominoToPlay(self, inPrint=True):
        # playable = self.mBoard.playable_numbers()
        theMax = len(self.mDominos)
        if inPrint:
            for i in range(theMax):
                print(
                    "{}: {} {}".format(i + 1, self.mDominos[i], self.starIfPlayable(i))
                )
            print(self.mName, "which domino would you like to play?")
        whichDomino = askNumberFromOneTo(theMax)
        print("Got:", whichDomino)
        if str(whichDomino)[0] == "u":
            self.undo()
            return self.askWhichDominoToPlay()
        whichDomino -= 1  # askNumber is 1 thru 7 but dominos are 0 thru 6
        if not self.isDominoPlayable(whichDomino):
            print("Can not play {}!".format(self.mDominos[whichDomino]))
            return self.askWhichDominoToPlay(False)
        return whichDomino

    def askWhereToPlay(self, inDominoToPlay):
        if not self.mBoard.played_dominos:
            return None  # firstDominoPlayed has no neighbors
        potentialNeighbors = self.mBoard.playable_dominos(inDominoToPlay)
        assert potentialNeighbors
        if len(potentialNeighbors) == 1:
            return potentialNeighbors[0]
        print("Connect {}: to which domino?".format(inDominoToPlay))
        theMax = len(potentialNeighbors)
        for i in range(theMax):
            print("{}: {}".format(i + 1, potentialNeighbors[i].mDomino))
        return potentialNeighbors[askNumberFromOneTo(theMax) - 1]

    # ===== Computer player routines

    # class DominoComputerPlayer(DominoPlayer):
    def playATurnComputerPlayer(self):
        # print(self)
        print(self.handAsString())
        # print('Playable: {}, Value: {}'.format(playable, self.mBoard.get_value()))
        score, run = self.best_run()
        return self.playARun(run)

    def best_run(
        self
    ):  # return the most valuable of an exhaustive series of lists of DominoRunMoves
        if not self.mDominos:
            # going out with goAgain more valuable than not goAgain
            return [12, []]
        bestScoreAndRun = [0, []]  # theRun is a list of DominoRunMoves
        self.mDominos.sort()  # maintain list order across calls to pop() & append()
        for i in range(len(self.mDominos)):
            if self.isDominoPlayable(i):
                d = self.mDominos.pop(i)
                theScoreAndRun = self.bestRunForDomino(d)
                if theScoreAndRun[0] > bestScoreAndRun[0]:
                    bestScoreAndRun = theScoreAndRun
                self.mDominos.append(d)
                self.mDominos.sort()  # pop()/append() will mess up list order
        # print('best_run:', bestScoreAndRun)
        return bestScoreAndRun

    def bestRunForDominoOnEmptyBoard(self, inDomino):
        theKeepers = [[0, 0], [0, 5], [5, 0], [5, 5]]
        if inDomino in theKeepers:
            return [0, []]  # do not waste theKeepers on an empty board
        bestScoreAndRun = [0, []]  # theRun is a list of DominoRunMoves
        theScoreAndRun = self.bestRunForDominoAndNeighbor(inDomino, None)
        if theScoreAndRun[0] > bestScoreAndRun[0]:
            bestScoreAndRun = theScoreAndRun
        return bestScoreAndRun

    def bestRunForDomino(self, inDomino):
        if not self.mBoard.played_dominos:
            return self.bestRunForDominoOnEmptyBoard(inDomino)
        bestScoreAndRun = [0, []]  # theRun is a list of DominoRunMoves
        potentialNeighbors = self.mBoard.playable_dominos(inDomino)
        for theNeighbor in potentialNeighbors:
            theScoreAndRun = self.bestRunForDominoAndNeighbor(inDomino, theNeighbor)
            if theScoreAndRun[0] > bestScoreAndRun[0]:
                bestScoreAndRun = theScoreAndRun
        return bestScoreAndRun

    def calc_run_score(self):  # (inPoints, inNumberOfDominosPlayed, inFaceValue)
        # the 12 values goAgain above a high faceValue
        return (
            self.mBoard.get_points * 1000
            + 12
            + self.mBoard.played_dominos[-1].face_value
        )

    def bestRunForDominoAndNeighbor(self, inDomino, inNeighbor):
        if inNeighbor:
            theDomino = inNeighbor.newNeighbor(self, inDomino)
        else:
            theDomino = PlayedDomino(self, inDomino)
        bestScoreAndRun = [0, []]  # theRun is a list of DominoRunMoves
        self.mBoard.played_dominos.append(theDomino)
        theScore = self.calc_run_score()
        theRun = [DominoRunMove(inNeighbor, inDomino, self.mBoard.get_points)]
        if theScore > bestScoreAndRun[0]:
            bestScoreAndRun = [theScore, theRun]
        if theDomino.is_double or self.mBoard.get_points:
            theScoreAndRun = self.best_run()  # go again
            theScoreAndRun[0] += theScore
            if theScoreAndRun[0] > bestScoreAndRun[0]:
                bestScoreAndRun[0] = theScoreAndRun[0]
                bestScoreAndRun[1] = theRun + theScoreAndRun[1]
        self.mBoard.played_dominos.pop().notifyNeighborsOfUndo()
        return bestScoreAndRun


if __name__ == "__main__":
    from DominoWorld import main

    main()
