[The Game](https://boardgamegeek.com/boardgame/173090/the-game) is a card game built around discarding cards from a deck into multiple piles while following certain rules. The goal is to cooperatively discard all cards and not have any left over at the end. If a player has no possible move, all players lose.

I played this game with my friends yesterday and was interested in the probabilities and possible strategies. How important are each of the mechanics? How important is communication? How good of a solution is one that is locally best?

What I have found is that, assuming simplistic but good local play and no long-term strategy, the win rate is about 1.1%. One interesting find is that playing more cards than the minimum, even if those cards have a small difference between them, does not noticeably improve the winrate.

Another interesting observation is that, on average, all players have 12.7 possible plays each turn. This number shows itself over hundreds of thousands of simulations.

The rules are faithfully ported and the AI uses simplistic but good local play. As of yet, it does not calculate combinations, but I intend to add that in the future.

A future plan of mine would be to make the game more engaging, add PVP elements, and port it to pygame with multiplayer.

Tools used:
  - mypy
  - ruff

TODO:
  - Refactor object ID system
  - Move functions into local scopes
  - Add more statistics
