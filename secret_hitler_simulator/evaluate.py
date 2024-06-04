# Standard Library Imports
import random
from typing import Optional

# Module Imports
from secret_hitler_simulator.constants import Allegiance
from secret_hitler_simulator.game import Game
from secret_hitler_simulator.player import Player


def evaluate_liberal_player(
    liberal_player: Player,
    other_liberals: tuple[Player],
    fascists: tuple[Player],
    hitler: Player,
    num_games: int,
    seed: Optional[int] = None,
):
    """Evaluate the win rate of a liberal player

    Args:
        liberal_player (Player): The liberal player being evaluated
        other_liberals (tuple[Player]): The other Liberals being played with
        fascists (tuple[Player]): The other Fascists being played with
        hitler (Player): Hitler, must be in fascist_players
        seed (Optional[int]): The random number seed if not None

    Returns:
        int: Number of games won
    """

    # Intialize value
    num_wins = 0

    # Set random seed
    random.seed(seed)

    # Iterate through games
    for game_num in range(num_games):

        liberals = other_liberals + (liberal_player,)

        presidential_order_list = list(liberals) + list(fascists)
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
        print(f"Game #{game_num + 1}")
        print(f"Winner: {result}")
        print(f"Reason: {reason}")
        print("")

        if result == Allegiance.LIBERAL:
            num_wins += 1

    return num_wins
