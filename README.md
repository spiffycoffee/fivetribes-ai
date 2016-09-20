# fivetribes-ai
An AI for the board game Five Tribes. This project is a Work-in-Progress.

# Introduction
Five Tribes is a wonderful board game designed by Bruno Cathala and published by Days of Wonder. 
It is a bit infamous in the board game community for causing what is know as "analysis paralysis" - 
the inability to decide what to do on your turn because of the sheer number of options to consider. 
Having experience some of that myself, I thought it would be fun to try to build an AI and see if it could do any better.

# Description
This AI currently uses a min-maxing algorithm with alphabeta pruning. 
(In the future I'm interested in testing alternative approaches such as Monte-Carlo tree search.) 
While Five Tribes can support up to a 4-player game, this AI only supports a 2-player game.
This is because most AI approaches were only designed with 2-player games in mind 
and the literature around multiplayer AIs is kind of thin. 

In addition to the player count difference, Five Tribes features additional key differences to traditional AI targeted games 
like Chess or Go that make it more complicated (although also some that make it simpler). These include:
- Extremely high branching factor, on the order of ~1,000 a turn. (Compare this to ~30 in Chess and ~200 in Go)
- Bidding for turn order
- Non-deterministic (aka random) events - namely when replenshing the Merchant Deck and Djinn Deck
- Djinn cards that can change game rules and scoring during the middle of the game

The first bullet was enough to keep my hands full, so for the sake of tractability I am ignoring the other issues. 
There is no bidding for turn order, play occurs in a fixed order. There is no replenishing of either deck. And I am ignoring djinn card
effects completely.

# Usage
`python fivetribes.py`  
This will generate a random starting board and compute the best move for Player 1.  
To understand what is going on, it is recommended that you be familiar with the rules for Five Tribes. 
Rules can be found [here](https://www.daysofwonder.com/five-tribes/en/#rules) for multiple languages. 


# Board Representation
```
Generating starting board with seed 8090                 
Board generated in 0.0019998550415 secs                  
-------------------------------------------------------- 
| 0: h  (6)| 1: h  (6)| 2: f  (7)| 3: s  (6)| 4: f  (3)| 
|   wyg    |   ryr    |   gwr    |   ryb    |   yyy    | 
|        ()|        ()|        ()|        ()|        ()| 
-------------------------------------------------------- 
| 5: f (10)| 6: o (10)| 7: h (12)| 8: s  (7)| 9: o  (4)| 
|   ywb    |   wwb    |   yrg    |   ggg    |   wyb    | 
|        ()|        ()|        ()|        ()|        ()| 
-------------------------------------------------------- 
|10: v  (5)|11: f (10)|12: s (11)|13: s (12)|14: s  (4)| 
|   rbg    |   gww    |   bww    |   gbw    |   wrg    | 
|        ()|        ()|        ()|        ()|        ()| 
-------------------------------------------------------- 
|15: s (10)|16: v  (5)|17: h  (8)|18: h  (9)|19: f  (8)| 
|   rgr    |   gww    |   wbb    |   yrg    |   bwb    | 
|        ()|        ()|        ()|        ()|        ()| 
-------------------------------------------------------- 
|20: o (12)|21: f  (6)|22: s  (3)|23: o  (5)|24: s (11)| 
|   ybr    |   ryb    |   rgw    |   bgy    |   ygy    | 
|        ()|        ()|        ()|        ()|        ()| 
-------------------------------------------------------- 
|25: o  (6)|26: o  (4)|27: v (10)|28: o (10)|29: s (10)| 
|   rwg    |   rrb    |   rby    |   gwb    |   brw    | 
|        ()|        ()|        ()|        ()|        ()| 
-------------------------------------------------------- 

Calculating best move...                                                   
Best move - Net score 3, Move: [(11, ''), (6, 'w'), (7, 'w'), (8, 'g')]    
```
The game is played on a 5x6 grid of tiles, instead of using a grid system I numbered them from 0-29.  

__Within each tile:__
- Top-left: Tile number (0 - 29)
- Top-middle: Tile type (Oassis, Sacred place, Village, Half-market, Full-market)   
- Top-right: Tile point value (a number between 3 and 12)  
- Middle: The meeples currently on the tile (Red, Blue, Green, White, Yellow)  
- Bottom-left: Palm Trees or Palaces (t = Palm Trees, p = Palace)  
- Bottom-right: Camel (+ = Player 1's camels, - = Player 2's camels)

__Reading moves:__  
Move: [(11, ''), (6, 'w'), (7, 'w'), (8, 'g')]    
- From Tile #11, take all meeples (it currently has 'gww').   
- Go to Tile #6, drop White meeple.  
- Go to Tile #7, drop White meeple.  
- Go to Tile #8, drop Green meeple. (Then score)

# TODOs
- Properly score assassins and fakirs
- Allow game to be played through - AI vs AI, and player vs AI
- Allow user to specify game state, rather than always starting with a randomly generated starting board
- Improve run-times - currently looks a whopping 2 moves ahead b/c any further causes massive slow down 
- Various other minor tweaks
