# Module imports
from secret_hitler_simulator.evaluate import evaluate_liberal_player
from secret_hitler_simulator.players.aggroFascist import AggroFascist
from secret_hitler_simulator.players.naiveLiberal import NaiveLiberal

liberal_player = NaiveLiberal()
other_liberals = (
    NaiveLiberal(),
    NaiveLiberal(),
    NaiveLiberal(),
    NaiveLiberal(),
)
hitler = AggroFascist()
fascists = (
    hitler,
    AggroFascist(),
    AggroFascist(),
    AggroFascist(),
)
num_games = 1000
seed = 0

evaluate_liberal_player(
    liberal_player, other_liberals, fascists, hitler, num_games, seed
)
