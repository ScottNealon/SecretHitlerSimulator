# Standard Library Import
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

# Module Imports
from secret_hitler_simulator.constants import Allegiance, Policy

# Type Checking
if TYPE_CHECKING:
    from secret_hitler_simulator.game import RoundRecord


class Player(ABC):

    ### FORMING GOVERNMENT DECISIONS ###

    @classmethod
    @abstractmethod
    def select_chancellor(cls, state: "tuple[RoundRecord]") -> int:
        """Returns selected Chancellor for proposed government as Chancellor

        Args:
            state (tuple[RoundRecord]): Current state of the game from the player's perspective

        Returns:
            int: The player id of the selected chancellor for the proposed government
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def intent_to_vote_on_government(
        cls, state: "tuple[RoundRecord]"
    ) -> Optional[bool]:
        """Return the publically declared intent to vote for the proposed government

        Args:
            state (tuple[RoundRecord]): Current state of the game from the player's perspective

        Returns:
            Optional[bool]: Ja (true), Nein (false), or no declaration of intent (None) for proposed government
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def vote_on_government(
        cls,
        state: "tuple[RoundRecord]",
    ) -> bool:
        """Return the players vote for the proposed government

        Args:
            state (tuple[RoundRecord]): Current state of thhe game

        Returns:
            bool: Ja (true) or Nein (false) for proposed government"""
        raise NotImplementedError()

    ### LEGISLATIVE SESSION ###

    @classmethod
    @abstractmethod
    def select_policy_to_discard_as_president(
        cls, state: "tuple[RoundRecord]"
    ) -> Policy:
        """Return the policy discarded as President when given a choice

        Args:
            state (tuple[RoundRecord]): Current state of the game from the player's perspective

        Returns:
            Policy: The policy discarded as President"""
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def select_policy_to_discard_as_chancellor(
        cls, state: "tuple[RoundRecord]"
    ) -> Policy:
        """Return what policy discarded as Chancellor when given a choice

        Args:
            state (tuple[RoundRecord]): Current state of the game from the player's perspective

        Returns:
            Policy: Selected policy
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def veto_legislation(cls, state: "tuple[RoundRecord]") -> int:
        """Return whether to veto legislation if Chancellor or President following 5th Fascist policy

        Args:
            state (tuple[RoundRecord]): Current state of the game from the player's perspective

        Returns:
            int: The player id of the player selected to be shot
        """
        raise NotImplementedError()

    ### LEGISLATIVE SESSION CLAIMS ###

    @classmethod
    @abstractmethod
    def claimed_policy_to_discard_as_president(
        cls,
        state: "tuple[RoundRecord]",
    ) -> tuple[int, Policy]:
        """Return the set of policies publicly claimed as the President. THIS IS WHERE YOU LIE!

        Args:
            state (tuple[RoundRecord]): Current state of the game from the player's perspective

        Returns:
            int: The publicly claimed number of fascist policies drawn
            Policy: The publically claimed policy discarded
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def claimed_policy_to_discard_as_chancellor(
        cls, state: "tuple[RoundRecord]"
    ) -> int:
        """Return the set of policies publicly claimed as the Chancellor. THIS IS WHERE YOU LIE!

        Args:
            state (tuple[RoundRecord]): Current state of the game from the player's perspective

        Returns:
            int: The publicly claimed number of fascist policies handed to the Chancellor
        """
        raise NotImplementedError()

    ### EXECUTIVE ACTIONS ###

    @classmethod
    @abstractmethod
    def select_player_to_investigate(cls, state: "tuple[RoundRecord]") -> int:
        """Return the id of the player selected to investigate if President following 1st or 2nd Fascist policy

        Args:
            state (tuple[RoundRecord]): Current state of the game from the player's perspective

        Returns:
            int: The id of the player selected for investigation
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def claimed_player_investigation_result(
        cls,
        state: "tuple[RoundRecord]",
    ) -> Allegiance:
        """Return the publicly claimed investigation results if President following 1st or 2nd Fascist policy

        Args:
            state (tuple[RoundRecord]): Current state of the game from the player's perspective

        Returns:
            Allegiance: The publicly claimed investigation results
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def select_special_election_president(cls, state: "tuple[RoundRecord]") -> int:
        """Return the id of the player selected as the President of the special election if President following 3rd Fascist policy

        Args:
            state (tuple[RoundRecord]): Current state of the game from the player's perspective

        Returns:
            int: The id of the player selected as the President of the special election
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def select_player_to_execute(cls, state: "tuple[RoundRecord]") -> int:
        """Return the player selected to shoot if President following 4th or 5th Fascist policy

        Args:
            state (tuple[RoundRecord]): Current state of the game from the player's perspective

        Returns:
            int: The player id of the player selected to be shot
        """
        raise NotImplementedError()
