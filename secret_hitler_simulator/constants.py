# Standard Library Imports
from enum import Enum


class Allegiance(Enum):
    LIBERAL = "LIBERAL"
    FASCIST = "FASCIST"


class Policy(Enum):
    LIBERAL = "LIBERAL"
    FASCIST = "FASCIST"


PARTY_MEMBERSHIP_BY_PLAYERS = {
    5: {Allegiance.LIBERAL: 3, Allegiance.FASCIST: 2},
    6: {Allegiance.LIBERAL: 4, Allegiance.FASCIST: 2},
    7: {Allegiance.LIBERAL: 4, Allegiance.FASCIST: 3},
    8: {Allegiance.LIBERAL: 5, Allegiance.FASCIST: 3},
    9: {Allegiance.LIBERAL: 5, Allegiance.FASCIST: 4},
    10: {Allegiance.LIBERAL: 6, Allegiance.FASCIST: 4},
}
