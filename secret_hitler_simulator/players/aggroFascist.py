# Standard Library Imports
import random
from typing import TYPE_CHECKING, Optional

# Module Imports
from secret_hitler_simulator.constants import Allegiance, Policy
from secret_hitler_simulator.player import Player

# Type Checking
if TYPE_CHECKING:
    from secret_hitler_simulator.game import RoundRecord


class AggroFascist(Player):

    ### FORMING GOVERNMENT DECISIONS ###

    @classmethod
    def select_chancellor(cls, state: "tuple[RoundRecord]") -> int:
        """Randomly selects fascist Chancellor if able, prefering hitler if after 3 fascist politices"""
        if state[-1].number_of_fascist_policies_passed > 3:
            if state[-1].hitler not in state[-1].ineligible_for_chancellorship:
                return state[-1].hitler
        number_of_players = state[-1].number_of_players
        valid_fascist_players = tuple(
            player
            for player in state[-1].fascists
            if player not in state[-1].ineligible_for_chancellorship
        )
        if len(valid_fascist_players) > 0:
            return random.choice(valid_fascist_players)
        else:
            # If unable to select Fascist, randomly select someone
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
        """Only votes if at least one is a Fascist"""
        return (
            state[-1].president in state[-1].fascists
            or state[-1].chancellor in state[-1].fascists
        )

    ### LEGISLATIVE SESSION ###

    @classmethod
    def select_policy_to_discard_as_president(
        cls, state: "tuple[RoundRecord]"
    ) -> Policy:
        """Always discards Liberal policies"""
        return Policy.LIBERAL

    @classmethod
    def select_policy_to_discard_as_chancellor(
        cls, state: "tuple[RoundRecord]"
    ) -> Policy:
        """Always discards Liberal policies"""
        return Policy.LIBERAL

    @classmethod
    def veto_legislation(cls, state: "tuple[RoundRecord]") -> int:
        """Always veto Liberal policies"""
        return state[-1].selected_policy is Policy.LIBERAL

    ### LEGISLATIVE SESSION CLAIMS ###

    @classmethod
    def claimed_policy_to_discard_as_president(
        cls,
        state: "tuple[RoundRecord]",
    ) -> tuple[int, Policy]:
        # If no veto
        if state[-1].selected_policy is not None:
            # If Chancellor is Liberal
            if state[-1].chancellor not in state[-1].fascists:
                # Always say you gave them a choice, regardless of if you did
                # TODO: Be smarter about number of fascist cards drawn
                return (2, Policy.FASCIST)
            # If Chancellor is Fascist
            else:
                match state[-1].selected_policy:
                    # If passed Liberal, pretend it was a choice
                    case Policy.LIBERAL:
                        # TODO: Be smarter about number of fascist cards drawn
                        return (2, Policy.FASCIST)
                    # If passed Fascist, pretned there was no option
                    case Policy.FASCIST:
                        return (3, Policy.FASCIST)
        # If veto
        else:
            # I don't want to think about this, just say it was impossible
            return (3, Policy.FASCIST)

    @classmethod
    def claimed_policy_to_discard_as_chancellor(
        cls, state: "tuple[RoundRecord]"
    ) -> int:
        # If no veto
        if state[-1].selected_policy is not None:
            # If President is Liberal
            if state[-1].president not in state[-1].fascists:
                match state[-1].selected_policy:
                    # If passed Liberal, tell the truth
                    case Policy.LIBERAL:
                        return state[-1].policy_discarded_by_chancellor
                    # If passed Fascist, trigger 50/50
                    case Policy.FASCIST:
                        return Policy.FASCIST
            # If President is Fascist
            else:
                # If passed Liberal, hopefully the President also pretends it was a choice.
                # If passed Fascist, pretned there was no option
                return Policy.FASCIST
        # If veto
        else:
            # I don't want to think about this, just say it was impossible
            return Policy.FASCIST

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
        """Always lie"""
        return (
            Policy.LIBERAL
            if state[-1].investigated_player_identity is Policy.FASCIST
            else Policy.FASCIST
        )

    @classmethod
    def select_special_election_president(cls, state: "tuple[RoundRecord]") -> int:
        """Randomly selects fascist President if able, avoiding hitler"""
        number_of_players = state[-1].number_of_players
        valid_fascist_players = tuple(
            player
            for player in state[-1].fascists
            if player is not state[-1].hitler and player is not state[-1].your_player_id
        )
        if len(valid_fascist_players) > 0:
            return random.choice(valid_fascist_players)
        else:
            # If unable to select Fascist, randomly select someone
            valid_players = tuple(
                player
                for player in range(number_of_players)
                if player not in state[-1].ineligible_for_chancellorship
                and player is not state[-1].hitler
                and player is not state[-1].your_player_id
            )
            return random.choice(valid_players)

    @classmethod
    def select_player_to_execute(cls, state: "tuple[RoundRecord]") -> int:
        """Randomly execute a Liberal"""
        number_of_players = state[-1].number_of_players
        valid_players = [
            player
            for player in range(number_of_players)
            if player not in state[-1].executed_players
            and player not in state[-1].fascists
        ]
        return random.choice(valid_players)
