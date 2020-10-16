"""
Defines some Enumerations for constant values

TODO how do I docstring the values?
"""
from enum import Enum


class ControllerType(Enum):
    """
    Defines the types of controller supported
    """

    brick = "GeoBrick"
    pmac = "PMAC"


class PostHomeMove(Enum):
    """
    Defines the set up actions available upon completion of the homing sequence
    """

    # no action
    none = 0
    # move jdist away from the home mark and set that as home
    move_and_hmz = 1
    relative_move = 2
    initial_position = 3
    high_limit = 4
    low_limit = 5
    hard_hi_limit = 6
    hard_lo_limit = 7
    move_absolute = 8


class HomingState(Enum):
    """
    Defines the stages of homing as reported back to the monitoring IOC
    """

    StateIdle = 0
    StateConfiguring = 1
    StateMoveNeg = 2
    StateMovePos = 3
    StateHoming = 4
    StatePostHomeMove = 5
    StateAligning = 6
    StateDone = 7
    StateFastSearch = 8
    StateFastRetrace = 9
    StatePreHomeMove = 10
