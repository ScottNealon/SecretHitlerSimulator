# Standard Library Imports
import random
from typing import TYPE_CHECKING, Optional

# Module Imports
from secret_hitler_simulator.constants import Allegiance, Policy
from secret_hitler_simulator.player import Player

# Type Checking
if TYPE_CHECKING:
    from secret_hitler_simulator.game import RoundRecord


class NaiveLiberal(Player):

    ### FORMING GOVERNMENT DECISIONS ###

    @classmethod
    def select_chancellor(cls, state: "tuple[RoundRecord]") -> int:
        """Randomly selects Chancellor from valid options"""
        number_of_players = state[-1].number_of_players
        valid_players = tuple(
            player
            for player in range(number_of_players)
            if player not in state[-1].ineligible_for_chancellorship
        )
        return random.choice(valid_players)

    @classmethod
    def intent_to_vote_on_government(
        cls, state: "tuple[RoundRecord]"
    ) -> Optional[bool]:
        """Always says how they will vote"""
        return cls.vote_on_government(state)

    @classmethod
    def vote_on_government(
        cls,
        state: "tuple[RoundRecord]",
    ) -> bool:
        """Always votes yes"""
        return True

    ### LEGISLATIVE SESSION ###

    @classmethod
    def select_policy_to_discard_as_president(
        cls, state: "tuple[RoundRecord]"
    ) -> Policy:
        """Always discards Fascist policies"""
        return Policy.FASCIST

    @classmethod
    def select_policy_to_discard_as_chancellor(
        cls, state: "tuple[RoundRecord]"
    ) -> Policy:
        """Always discards Fascist policies"""
        return Policy.FASCIST

    @classmethod
    def veto_legislation(cls, state: "tuple[RoundRecord]") -> int:
        """Always veto Fascist policies"""
        return state[-1].selected_policy is Policy.FASCIST

    ### LEGISLATIVE SESSION CLAIMS ###

    @classmethod
    def claimed_policy_to_discard_as_president(
        cls,
        state: "tuple[RoundRecord]",
    ) -> tuple[int, Policy]:
        """Always tell the truth"""
        return (
            state[-1].num_fascist_policies_for_president,
            state[-1].policy_discarded_by_president,
        )

    @classmethod
    def claimed_policy_to_discard_as_chancellor(
        cls, state: "tuple[RoundRecord]"
    ) -> int:
        """Always tell the truth"""
        return state[-1].policy_discarded_by_chancellor

    ### EXECUTIVE ACTIONS ###

    @classmethod
    def select_player_to_investigate(cls, state: "tuple[RoundRecord]") -> int:
        """Randomly investigate someone"""
        number_of_players = state[-1].number_of_players
        valid_players = [
            player
            for player in range(number_of_players)
            if player not in state[-1].executed_players
            and player is not state[-1].your_player_id
        ]
        return random.choice(valid_players)

    @classmethod
    def claimed_player_investigation_result(
        cls,
        state: "tuple[RoundRecord]",
    ) -> Allegiance:
        """Always tell the truth"""
        return state[-1].investigated_player_identity

    @classmethod
    def select_special_election_president(cls, state: "tuple[RoundRecord]") -> int:
        """Randomly select someone"""
        number_of_players = state[-1].number_of_players
        valid_players = [
            player
            for player in range(number_of_players)
            if player not in state[-1].executed_players
            and player is not state[-1].your_player_id
        ]
        return random.choice(valid_players)

    @classmethod
    def select_player_to_execute(cls, state: "tuple[RoundRecord]") -> int:
        """Randomly select someone"""
        number_of_players = state[-1].number_of_players
        valid_players = [
            player
            for player in range(number_of_players)
            if player not in state[-1].executed_players
        ]
        return random.choice(valid_players)
