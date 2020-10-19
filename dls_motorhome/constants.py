"""
Defines some Enumerations for constant values

"""
from enum import Enum


class ControllerType(Enum):
    """
    Defines the types of controller supported
    """

    #: Geobrick controller
    brick = "GeoBrick"
    #: VME PMAC Controller
    pmac = "PMAC"


class PostHomeMove(Enum):
    """
    Defines the set up actions available upon completion of the homing sequence
    """

    #: no action
    none = 0
    #: move jdist counts away from the home mark and set that as home
    move_and_hmz = 1
    #: move jdist counts away from the home mark
    relative_move = 2
    #: return to the original position before the homing sequence
    initial_position = 3
    #: jog to the high limit
    high_limit = 4
    #: jog to the low limit
    low_limit = 5
    #: jog to the high limit, ignorning soft limits
    hard_hi_limit = 6
    #: jog to the low limit, ignorning soft limits
    hard_lo_limit = 7
    #: jog to the absolute position in counts
    move_absolute = 8


class HomingState(Enum):
    """
    Defines the stages of homing as reported back to the monitoring IOC
    TODO docs for this are incorrect and I'm confusing HomingState with HomingStatus
    """

    #: Homing is not running
    StateIdle = 0
    #: Homing is starting up
    StateConfiguring = 1
    #: Homing is moving in opposite direction to homing direction
    StateMoveNeg = 2
    #: Homing is moving in the homing direction
    StateMovePos = 3
    #: HM command has been issued to the pmac
    StateHoming = 4
    #: executing any post home moves
    StatePostHomeMove = 5
    #: executing alignment (unused)
    StateAligning = 6
    #: Homing is complete
    StateDone = 7
    #: Pre Home fast search for home position
    StateFastSearch = 8
    #: Moving back to just before home position
    StateFastRetrace = 9
    #:
    StatePreHomeMove = 10
