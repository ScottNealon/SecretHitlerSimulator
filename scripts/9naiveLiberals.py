# Standard Library Imports
import random

# Module imports
from secret_hitler_simulator.game import Game
from secret_hitler_simulator.players.naiveLiberal import NaiveLiberal

# Create a game of 9 Liberals, even as Fascists and hitler
liberals = [
    NaiveLiberal(),
    NaiveLiberal(),
    NaiveLiberal(),
    NaiveLiberal(),
    NaiveLiberal(),
]
hitler = NaiveLiberal()
fascists = [hitler, NaiveLiberal(), NaiveLiberal(), NaiveLiberal()]
presidential_order_list = liberals + fascists
random.shuffle(presidential_order_list)
presidential_order = tuple(presidential_order_list)
game = Game(
    liberals=frozenset(liberals),
    fascists=frozenset(fascists),
    hitler=hitler,
    policy_deck=Game.generate_random_policy_deck(),
    presidential_order=presidential_order,
)

# Play game
result, reason = game.play_game()
print(result)
print(reason)

game_report = game.write_game_report()
for line in game_report:
    print(line)
