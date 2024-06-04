# Standard Library imports
import random
from copy import deepcopy
from dataclasses import dataclass, fields
from traceback import format_exception
from typing import Optional

# Module Imports
from secret_hitler_simulator.constants import (
    PARTY_MEMBERSHIP_BY_PLAYERS,
    Allegiance,
    Policy,
)
from secret_hitler_simulator.errors import PlayerException
from secret_hitler_simulator.player import Player


class Game:
    """Game of Secret Hitler"""

    def __init__(
        self,
        liberals: frozenset[Player],
        fascists: frozenset[Player],
        hitler: Player,
        policy_deck: tuple["Policy"],
        presidential_order: tuple["Player"],
    ):
        """Initialize a Game of Secret Hitler

        Args:
            liberals (frozenset[Player]): The players who are liberal
            fascists (frozenset[Player]): The players who are fascists (including Hitler)
            hitler (Player): The player who is Hitler
            policy_deck (tuple[Policy]): The deck of policies to draw from
            presidential_order (tuple[Player]): The order players will be President
        """
        # Ensure valid attributes
        number_players = len(presidential_order)
        for player in presidential_order:
            if (
                player not in liberals
                and player not in fascists
                and player is not hitler
            ):
                raise ValueError(f"Player {player} does not have an assigned role.")
        if not liberals.issubset(presidential_order):
            raise ValueError("Not every liberal player is in presidential order.")
        if not fascists.issubset(presidential_order):
            raise ValueError("Not every fascist player is in presidential order.")
        if hitler not in presidential_order:
            raise ValueError(f"Hitler ({hitler}) is not in presidential order")
        if (
            len(liberals)
            != PARTY_MEMBERSHIP_BY_PLAYERS[number_players][Allegiance.LIBERAL]
        ):
            raise ValueError(
                f"Invalid number of liberals for a {number_players} player game."
            )
        if (
            len(fascists)
            != PARTY_MEMBERSHIP_BY_PLAYERS[number_players][Allegiance.FASCIST]
        ):
            raise ValueError(
                f"Invalid number of fascists for a {number_players} player game."
            )

        # Save attributes
        self.liberals = liberals
        self.fascists = fascists
        self.hitler = hitler
        self.policy_deck = policy_deck
        self.presidential_order = presidential_order

        # Initialize settings
        self.round_history: tuple[RoundRecord] = tuple()
        self.players = presidential_order
        self.executed_players = tuple()
        self.special_election_next_president: Optional[Player] = None
        self.previous_government: frozenset[Player] = frozenset()
        self.anarchy_counter = 0
        self.liberal_policies_passed = 0
        self.fascist_policies_passed = 0
        self.shot_hitler = False
        self.elected_hitler = False

        # Save random number generator so players can't cheat
        self.random_number_generator = random.getstate()

    @classmethod
    def generate_random_policy_deck(self) -> tuple[Policy]:
        """Generate a randomly shuffled policy deck

        Returns:
            tuple[Policy]: Randomly shuffled policy deck
        """
        policy_deck_list = 11 * [Policy.FASCIST] + 6 * [Policy.LIBERAL]
        random.shuffle(policy_deck_list)
        return tuple(policy_deck_list)

    def play_game(self) -> tuple[Allegiance, str]:
        """Play a game of Secret Hitler

        Returns:
            Optional[Allegiance]: The winning team
            str: The reason for victory
        """
        try:
            while self.determine_if_winner()[0] is None:
                self.play_round()
            return self.determine_if_winner()
        except PlayerException as e:
            player_generating_exception = e.args[0]["player"]
            if player_generating_exception in self.liberals:
                return Allegiance.FASCIST, "\n".join(format_exception(e))
            elif player_generating_exception in self.fascists:
                return Allegiance.LIBERAL, "\n".join(format_exception(e))
            else:
                ValueError(
                    f"Unable to determine allegiance of player ({player_generating_exception}) who generated exception "
                    "during game."
                )

    def play_round(self) -> Optional[Allegiance]:
        """Play a round of Secret Hitler

        Returns:
            Optional[Allegiance]: The winning team, or None if game continues
        """
        # Update policy deck
        # * In theory this is done at the end of rounds, but doing it here means we don't need to shuffle after the game
        #   is over.
        self.update_policy_deck()

        # Initialize round history
        self.update_round_history()

        # Determine next president
        president, president_id = self.determine_next_president()

        # Solicit intent to vote in government from all players
        self.solicit_intent_to_vote(president)

        # Determine the next chancellor
        chancellor, chancellor_id = self.select_chancellor(president)

        # Hold election
        successful_election = self.hold_election()

        # Election results
        if successful_election:
            # Check for Hitler
            if self.fascist_policies_passed >= 3 and chancellor is self.hitler:
                self.elected_hitler = True
                return
            # Pass a policy
            passed_policy = self.hold_legislation_session(president, chancellor)
            # Executive action
            if passed_policy is Policy.FASCIST:
                self.executive_action(president)
        else:
            # Anarchy
            self.anarchy_counter += 1
            if self.anarchy_counter == 3:
                self.execute_anarchy()

    def update_round_history(self):
        self.round_history = self.round_history + (
            RoundRecord(
                _previous_record=(
                    None if len(self.round_history) == 0 else self.round_history[-1]
                ),
                number_of_players=len(self.players),
                fascists=frozenset(
                    self.players.index(player) for player in self.fascists
                ),
                hitler=self.players.index(self.hitler),
            ),
        )

    def determine_next_president(self) -> tuple[Player, int]:
        """Determine the next president

        Returns:
            Player: The next president
            int: The player id of the next president
        """
        # Determine the next president
        if self.special_election_next_president is not None:
            president = self.special_election_next_president
            self.special_election_next_president = None
        else:
            president = self.presidential_order[0]
            self.presidential_order = self.presidential_order[1:] + (president,)
        president_id = self.players.index(president)
        self.round_history[-1].president = president_id
        return president, president_id

    def solicit_intent_to_vote(
        self, president: Player
    ) -> dict[int, dict[int, Optional[bool]]]:
        """Ask every player their opinion of every possible government

        Args:
            president (Player): The current president up for election

        Returns:
            dict[int, dict[int, Optional[bool]]]: The expressed voting intention of every player for every chancellor
        """
        declared_election_intent: dict[int, dict[int, Optional[bool]]] = {}
        for proposed_chancellor in self.players:
            proposed_chancellor_id = self.players.index(proposed_chancellor)
            if (
                proposed_chancellor in self.executed_players
                or proposed_chancellor is president
                or (
                    proposed_chancellor in self.previous_government
                    and len(self.presidential_order) > 5
                )
            ):
                continue
            for player in self.players:
                if player in self.executed_players:
                    continue
                player_id = self.players.index(player)
                game_state = self.get_player_percieved_game_state(player)
                declared_election_intent.setdefault(proposed_chancellor_id, {})[
                    player_id
                ] = player.intent_to_vote_on_government(
                    game_state,
                )
        self.round_history[-1].declared_election_intent = declared_election_intent

    def select_chancellor(self, president: Player) -> tuple[Player, int]:
        president_perspective = self.get_player_percieved_game_state(president)
        try:
            chancellor_id = president.select_chancellor(president_perspective)
        except Exception as e:
            raise PlayerException(
                {
                    "message": f"Exception from {president} while selecting Chancellor",
                    "player": president,
                }
            ) from e
        self.round_history[-1].chancellor = chancellor_id
        chancellor = self.players[chancellor_id]
        return chancellor, chancellor_id

    def hold_election(self) -> bool:
        election_results: dict[Player, bool] = {}
        for player in self.players:
            if player in self.executed_players:
                continue
            player_id = self.players.index(player)
            player_perception = self.get_player_percieved_game_state(player)
            election_results[player_id] = player.vote_on_government(
                player_perception,
            )
        successful_election = sum(election_results.values()) > len(self.players) / 2
        self.round_history[-1].election_results = election_results
        self.round_history[-1].successful_election = successful_election
        return successful_election

    def hold_legislation_session(
        self,
        president: Player,
        chancellor: Player,
    ):
        """Hold legislative session

        Args:
            president (Player): The elected president
            chancellor (Player): The elected chancellor
        """
        # Draw policies
        legislative_session_policies = self.draw_legislative_session_policies()
        num_fascist_policies_for_president = legislative_session_policies.count(
            Policy.FASCIST
        )
        self.round_history[-1].num_fascist_policies_for_president = (
            num_fascist_policies_for_president
        )
        # The president selects a policy to discard
        match num_fascist_policies_for_president:
            case 0:
                policy_discarded_by_president = Policy.LIBERAL
            case 1 | 2:
                president_perceptive = self.get_player_percieved_game_state(president)
                try:
                    policy_discarded_by_president = (
                        president.select_policy_to_discard_as_president(
                            president_perceptive
                        )
                    )
                    if policy_discarded_by_president not in [
                        Policy.LIBERAL,
                        Policy.FASCIST,
                    ]:
                        raise ValueError(
                            f"Unknown policy type returned by player {president}: {policy_discarded_by_president}"
                        )
                except Exception as e:
                    raise PlayerException(
                        {
                            "message": f"Exception from {president} while selecting policies as President",
                            "player": president,
                        }
                    ) from e
            case 3:
                policy_discarded_by_president = Policy.FASCIST
            case _:
                raise ValueError(
                    f"Invalid number of fascist policies ({num_fascist_policies_for_president}) handed to President."
                )
        num_fascist_policies_for_chancellor = (
            num_fascist_policies_for_president
            if policy_discarded_by_president is Policy.LIBERAL
            else num_fascist_policies_for_president - 1
        )
        self.round_history[-1].policy_discarded_by_president = (
            policy_discarded_by_president
        )
        self.round_history[-1].num_fascist_policies_for_chancellor = (
            num_fascist_policies_for_chancellor
        )
        # The chancellor selects a policy
        match num_fascist_policies_for_chancellor:
            case 0:
                policy_discarded_by_chancellor = Policy.LIBERAL
                selected_policy = Policy.LIBERAL
            case 1:
                chancellor_perceptive = self.get_player_percieved_game_state(chancellor)
                try:
                    policy_discarded_by_chancellor = (
                        chancellor.select_policy_to_discard_as_chancellor(
                            chancellor_perceptive
                        )
                    )
                    if policy_discarded_by_chancellor not in [
                        Policy.LIBERAL,
                        Policy.FASCIST,
                    ]:
                        raise PlayerException(
                            {
                                "message": f"Invalid policy passed by chancellor ({chancellor}): {policy_discarded_by_chancellor}",
                                "player": chancellor,
                            }
                        )
                except Exception as e:
                    raise PlayerException(
                        {
                            "message": f"Exception from {chancellor} while selecting policies as Chancellor.",
                            "player": chancellor,
                        }
                    ) from e
                selected_policy = (
                    Policy.LIBERAL
                    if policy_discarded_by_chancellor is Policy.FASCIST
                    else Policy.FASCIST
                )
            case 2:
                policy_discarded_by_chancellor = Policy.FASCIST
                selected_policy = Policy.FASCIST
        self.round_history[-1].policy_discarded_by_chancellor = (
            policy_discarded_by_chancellor
        )
        # Veto
        if self.fascist_policies_passed >= 5:
            chancellor_perceptive = self.get_player_percieved_game_state(chancellor)
            try:
                chancellor_veto = chancellor.veto_legislation(chancellor_perceptive)
                if not isinstance(chancellor_veto, bool):
                    raise PlayerException(
                        {
                            "message": f"Invalid veto value by chancellor ({chancellor}): {policy_discarded_by_chancellor}",
                            "player": chancellor,
                        }
                    )
            except Exception as e:
                raise PlayerException(
                    {
                        "message": f"Exception from {chancellor} while vetoing legislation.",
                        "player": chancellor,
                    }
                ) from e
            self.round_history[-1].chancellor_veto = chancellor_veto
            if chancellor_veto:
                president_perceptive = self.get_player_percieved_game_state(president)
                try:
                    president_veto = president.veto_legislation(president_perceptive)
                    if not isinstance(president_veto, bool):
                        raise PlayerException(
                            {
                                "message": f"Invalid veto value by president ({president}): {policy_discarded_by_president}",
                                "player": president,
                            }
                        )
                except Exception as e:
                    raise PlayerException(
                        {
                            "message": f"Exception from {president} while vetoing legislation.",
                            "player": president,
                        }
                    ) from e
                self.round_history[-1].president_veto = president_veto
                veto = president_veto
            else:
                veto = False
        else:
            veto = False

        # Enact the policy
        if not veto:
            match selected_policy:
                case Policy.LIBERAL:
                    self.liberal_policies_passed += 1
                case Policy.FASCIST:
                    self.fascist_policies_passed += 1
                case _:
                    raise ValueError(f"Unknown policy type {selected_policy}")
            self.round_history[-1].selected_policy = selected_policy
        # Claim policies
        # Neither president or chancellor get to know what the other claims before they claim
        president_perceptive = self.get_player_percieved_game_state(president)
        chancellor_perceptive = self.get_player_percieved_game_state(chancellor)
        try:
            (
                president_claimed_number_of_fascist_cards_drawn,
                president_claimed_discarded_policy,
            ) = president.claimed_policy_to_discard_as_president(president_perceptive)
            if president_claimed_number_of_fascist_cards_drawn not in [0, 1, 2, 3]:
                raise PlayerException(
                    {
                        "message": f"Player {president} claimed an invalid number of fascist cards: "
                        f"{president_claimed_number_of_fascist_cards_drawn}",
                        "player": president,
                    }
                )
            if president_claimed_discarded_policy not in [
                Policy.LIBERAL,
                Policy.FASCIST,
            ]:
                raise PlayerException(
                    {
                        "message": f"Player {president} claimed an invalid policy as President: "
                        f"{president_claimed_discarded_policy}",
                        "player": president,
                    }
                )
        except Exception as e:
            raise PlayerException(
                {
                    "message": f"Exception from {president} while claiming policies as President.",
                    "player": president,
                }
            ) from e
        try:
            chancellor_claimed_discarded_policy = (
                chancellor.claimed_policy_to_discard_as_chancellor(
                    chancellor_perceptive
                )
            )
            if chancellor_claimed_discarded_policy not in [
                Policy.LIBERAL,
                Policy.FASCIST,
            ]:
                raise PlayerException(
                    {
                        "message": f"Player {chancellor} claimed an invalid policy as Chancellor: "
                        f"{chancellor_claimed_discarded_policy}",
                        "player": chancellor,
                    }
                )
        except Exception as e:
            raise PlayerException(
                {
                    "message": f"Exception from {chancellor} while claiming policies as Chancellor.",
                    "player": chancellor,
                }
            ) from e
        self.round_history[-1].president_claimed_number_of_fascist_cards_drawn = (
            president_claimed_number_of_fascist_cards_drawn
        )
        self.round_history[-1].president_claimed_discarded_policy = (
            president_claimed_discarded_policy
        )
        self.round_history[-1].chancellor_claimed_discarded_policy = (
            chancellor_claimed_discarded_policy
        )
        return selected_policy

    def executive_action(self, president: Player):
        """Perform executive actions"""
        match self.fascist_policies_passed:
            # Investigate
            case 1 | 2:
                self.investigate_player(president)
            # Special election
            case 3:
                self.declare_special_election(president)
            # Bullet
            case 4 | 5:
                self.execute_player(president)
            # Game Over
            case 6:
                pass
            case _:
                raise ValueError(
                    f"Unknown number of Fascist policies passed: {self.fascist_policies_passed}"
                )

    def investigate_player(self, president: Player):
        """The president investigates a player"""
        president_perceptive = self.get_player_percieved_game_state(president)
        try:
            investigated_player_id = president.select_player_to_investigate(
                president_perceptive
            )
            if (
                not isinstance(investigated_player_id, int)
                or investigated_player_id < 0
                or investigated_player_id > len(self.players) - 1
            ):
                raise ValueError(
                    f"Invalid player_id {investigated_player_id} returned by President for investigating."
                )
        except Exception as e:
            raise PlayerException(
                {
                    "message": f"Exception from {president} while investigating as President.",
                    "player": president,
                }
            ) from e
        investigated_player = self.players[investigated_player_id]
        if investigated_player in self.liberals:
            investigated_player_identity = Allegiance.LIBERAL
        elif investigated_player in self.fascists:
            investigated_player_identity = Allegiance.FASCIST
        else:
            raise ValueError(
                f"Unable to determine allegiance of player ({investigated_player})"
            )
        self.round_history[-1].investigated_player = investigated_player_id
        self.round_history[-1].investigated_player_identity = (
            investigated_player_identity
        )
        claimed_investigated_player_allegiance = (
            president.claimed_player_investigation_result(
                president_perceptive,
            )
        )
        self.round_history[-1].claimed_investigated_player_allegiance = (
            claimed_investigated_player_allegiance
        )

    def declare_special_election(self, president: Player):
        """The president declares a special election"""
        # Feature option: Query every player for every President-Chancellor election option.
        # This would be computationally expensive but more realistic.
        president_perceptive = self.get_player_percieved_game_state(president)
        try:
            special_election_president_id = president.select_special_election_president(
                president_perceptive
            )
            if (
                not isinstance(special_election_president_id, int)
                or special_election_president_id < 0
                or special_election_president_id > len(self.players) - 1
            ):
                raise ValueError(
                    f"Invalid player_id {special_election_president_id} returned by President for selecting special "
                    "president."
                )
        except Exception as e:
            raise PlayerException(
                {
                    "message": f"Exception from {president} while calling special election as President.",
                    "player": president,
                }
            ) from e
        special_election_president = self.players[special_election_president_id]
        if special_election_president is president:
            raise PlayerException(
                {
                    "message": f"Player {president} selected themselves as President for special election.",
                    "player": president,
                }
            )
        elif special_election_president in self.executed_players:
            raise PlayerException(
                {
                    "message": f"Player {president} selected a corpse as President for special election.",
                    "player": president,
                }
            )
        self.special_election_next_president = special_election_president
        self.round_history[-1].special_election_next_president = (
            special_election_president_id
        )

    def execute_player(self, president: Player):
        """The president shoots a player"""
        president_perceptive = self.get_player_percieved_game_state(president)
        try:
            executed_player_id = president.select_player_to_execute(
                president_perceptive
            )
            if (
                not isinstance(executed_player_id, int)
                or executed_player_id < 0
                or executed_player_id > len(self.players) - 1
            ):
                raise ValueError(
                    f"Invalid player_id {executed_player_id} returned by President for execution."
                )
        except Exception as e:
            raise PlayerException(
                {
                    "message": f"Exception from {president} while executing as President.",
                    "player": president,
                }
            ) from e
        executed_player = self.players[executed_player_id]
        if executed_player in self.executed_players:
            raise PlayerException(
                {
                    "message": f"Player {president} selected a corpse for execution.",
                    "player": president,
                }
            )
        self.executed_players = self.executed_players + (executed_player,)
        self.presidential_order = tuple(
            player
            for player in self.presidential_order
            if player is not executed_player
        )
        self.round_history[-1].executed_player = executed_player_id

    def execute_anarchy(self):
        """Draws a random policy card following 3 failed elections"""
        next_policy = self.draw_anarchy_policy()
        match next_policy:
            case Policy.LIBERAL:
                self.liberal_policies_passed += 1
                self.round_history[-1].anarchy_result = Policy.LIBERAL
            case Policy.FASCIST:
                self.fascist_policies_passed += 1
                self.round_history[-1].anarchy_result = Policy.FASCIST

    def draw_legislative_session_policies(self) -> tuple[Policy]:
        """Draws the top three cards of the policy deck for the legislative session

        Returns:
            tuple[Policy]: Top three cards of the policy deck
        """
        legislative_session_policies = tuple(self.policy_deck[:3])
        self.policy_deck = self.policy_deck[3:]
        return legislative_session_policies

    def draw_anarchy_policy(self) -> Policy:
        """Draws the top card of the policy deck for anarchy"""
        anarchy_card = self.policy_deck[0]
        self.policy_deck = self.policy_deck[1:]
        return anarchy_card

    def update_policy_deck(self):
        """Shuffles the deck if less than 3 policies remaining"""
        if len(self.policy_deck) < 3:
            policy_deck_list = (11 - self.fascist_policies_passed) * [
                Policy.FASCIST
            ] + (6 - self.liberal_policies_passed) * [Policy.LIBERAL]
            random.setstate(self.random_number_generator)
            random.shuffle(policy_deck_list)
            self.policy_deck = tuple(policy_deck_list)
            self.random_number_generator = random.getstate()

    def determine_if_winner(self) -> tuple[Optional[Allegiance], Optional[str]]:
        """Determine if there is a winner to the game

        Returns:
            Optional[Allegiance]: The winning team, or None if game continues
        """
        if self.liberal_policies_passed == 5:
            return Allegiance.LIBERAL, "Passed 5 Liberal Policies"
        elif self.shot_hitler:
            return Allegiance.LIBERAL, "Shot Hitler"
        elif self.fascist_policies_passed == 6:
            return Allegiance.FASCIST, "Passed 6 Fascist Policies"
        elif self.elected_hitler:
            return Allegiance.FASCIST, "Elected Hitler"
        else:
            return None, None

    def get_player_percieved_game_state(self, player: Player) -> tuple["RoundRecord"]:
        """Return a player's truth perspective of the current game state

        Args:
            player (Player): The player to get the perspective of.

        Returns:
            tuple[RoundRecord]: A fully copied representation of the truth game state for a given player
        """
        game_state = tuple()
        for round in self.round_history:
            # Deepcopy record
            round_state = deepcopy(round)
            # Update values
            for field in fields(round_state):
                value = getattr(round_state, field.name)
                value = deepcopy(value)
            # Set your round id
            player_id = self.players.index(player)
            round_state.your_player_id = player_id
            # Add to tuple
            game_state = game_state + (round_state,)
        return game_state

    def write_game_report(self):
        report: tuple[str] = tuple()
        for round_num, round_state in enumerate(self.round_history):
            report += (f"Round #{round_num + 1}",)
            field_name_length = max(len(field.name) for field in fields(round_state))
            format_string = f"    {{field_name:{field_name_length}s}}: {{value}}"
            for field in fields(round_state):
                value = getattr(round_state, field.name)
                if value is not None:
                    report += (
                        format_string.format(field_name=field.name, value=value),
                    )
        return report


@dataclass
class RoundRecord:

    ### CONSTANTS ###

    number_of_players: int
    fascists: tuple[int]
    hitler: int

    ### PRIVATE ATTRIBUTES ###

    _previous_record: Optional["RoundRecord"] = None

    ### ACTION RESULTS ###

    president: Optional[int] = None
    declared_election_intent: Optional[dict[int, dict[int, Optional[bool]]]] = None
    chancellor: Optional[int] = None
    election_results: Optional[dict[int, bool]] = None
    successful_election: Optional[bool] = None
    num_fascist_policies_for_president: Optional[int] = None
    policy_discarded_by_president: Optional[Policy] = None
    num_fascist_policies_for_chancellor: Optional[int] = None
    policy_discarded_by_chancellor: Optional[Policy] = None
    chancellor_veto: Optional[bool] = None
    president_veto: Optional[bool] = None
    president_claimed_number_of_fascist_cards_drawn: Optional[int] = None
    president_claimed_discarded_policy: Optional[Policy] = None
    chancellor_claimed_discarded_policy: Optional[Policy] = None
    anarchy_occured: Optional[bool] = None
    selected_policy: Optional[Policy] = None
    investigated_player: Optional[int] = None
    investigated_player_identity: Optional[Allegiance] = None
    claimed_investigated_player_allegiance: Optional[Allegiance] = None
    special_election_next_president: Optional[Allegiance] = None
    executed_player: Optional[int] = None
    anarchy_result: Optional[Policy] = None

    ### VALUES FOR PLAYERS ###

    your_player_id: Optional[int] = None

    ### HELPER FUNCTIONS ###

    @property
    def number_of_liberal_policies_passed(self) -> int:
        # This works both before and after selected policy is defined, but do no cache
        passed_liberal_policy = (
            self.selected_policy == Policy.LIBERAL
            or self.anarchy_result == Policy.LIBERAL
        )
        if self._previous_record is not None:
            return self._previous_record.number_of_liberal_policies_passed + int(
                passed_liberal_policy
            )
        else:
            return int(passed_liberal_policy)

    @property
    def number_of_fascist_policies_passed(self) -> int:
        # This works both before and after selected policy is defined, but do no cache
        passed_fascist_policy = (
            self.selected_policy == Policy.FASCIST
            or self.anarchy_result == Policy.FASCIST
        )
        if self._previous_record is not None:
            return self._previous_record.number_of_fascist_policies_passed + int(
                passed_fascist_policy
            )
        else:
            return int(passed_fascist_policy)

    @property
    def anarchy_counter(self) -> int:
        # Check where in the round we are
        if self.election_results is None:
            # Before elections
            if self._previous_record is not None:
                return self._previous_record.anarchy_counter
            else:
                return 0
        else:
            # After elections
            if self.successful_election:
                return 0
            else:
                if self._previous_record is not None:
                    return self._previous_record.anarchy_counter + 1
                else:
                    return 1

    @property
    def executed_players(self) -> tuple[int]:
        """Return a tuple of the ids of players who were executed"""
        # Check where in the round we are
        if self.executed_player is None:
            # Before any executions
            if self._previous_record is not None:
                return self._previous_record.executed_players
            else:
                return tuple()
        else:
            # After any executions
            if self._previous_record is not None:
                return self._previous_record.executed_players + (self.executed_player,)
            else:
                return (self.executed_player,)

    @property
    def ineligible_for_chancellorship(self) -> tuple[int]:
        """Return a tuple of the ids of players ineligable for the chancellorship"""
        if self._previous_record is None:
            return tuple()
        elif self.number_of_players - len(self.executed_players) <= 5:
            return self._previous_record.executed_players
        else:
            if self._previous_record.successful_election:
                return self._previous_record.executed_players + (
                    self._previous_record.chancellor,
                )
            else:
                return self._previous_record.ineligible_for_chancellorship
