# Claussoft Dominos from Claussoft International
Racehorse dominos

Rules:
* Each player is initially dealt a hand of 7 dominos
* Dominos can only be played against matching numbers
* If no domino in a player's hand matches an outside domino then the player must take a domino from the boneyard until one can play or until the boneyard only has two dominos
* If all outside dominos add up to a multiple of 5 then the player gets points and goes again
* If the player plays doubles they get to go again.  Note: Doubles are played sideways and count 2x.
* The player who has no dominos gets all points on the other player's dominos // 5
* First player to 30 points wins the match

$ __./DominoWorld.py__  # To play a text game on the terminal against the computer
```
Player 1's hand: 2 [[3, 0], [5, 0]]
======================
     1     6
[0,1]-[1,6]-[6,5][5,4]
     1     6
======================
Playable: [0, 1, 4, 6], Value: 4
RECAP:playARun() run length: 3
1 Playing [1, 1] on [1, 6] is a double, go again...
2 Playing [0, 1] on [1, 1] 1.0 points, go again...
3 Playing [5, 4] on [6, 5]
Player 1 has 2 dominos, 24.0 points, 16 go agains, 2 hands and 0 games won.
========== NEW TURN ==========
Player 0 has 6 dominos, 18.0 points, 10 go agains, 1 hands and 0 games won.
```

$ __./tkDomino.py__  # To see the start of a [tkinter](https://docs.python.org/3/library/tk.html)-based ui
![tkDomino.py.png](images/tkDomino.py.png)
