# Standard Library Imports
import random

# Module imports
from secret_hitler_simulator.game import Game
from secret_hitler_simulator.players.aggroFascist import AggroFascist
from secret_hitler_simulator.players.naiveLiberal import NaiveLiberal

# Create a game of 5 Liberals and 4 Aggro Fascists
liberals = [
    NaiveLiberal(),
    NaiveLiberal(),
    NaiveLiberal(),
    NaiveLiberal(),
    NaiveLiberal(),
]
hitler = AggroFascist()
fascists = [hitler, AggroFascist(), AggroFascist(), AggroFascist()]
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
print(f"Winner: {result}")
print(f"Reason: {reason}")
print("")

game_report = game.write_game_report()
if "Exception" not in reason:
    for line in game_report:
        print(line)
