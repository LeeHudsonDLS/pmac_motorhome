from enum import Enum


class ControllerType(Enum):
    brick = "Geobrick"
    pmac = "PMAC"


class PostHomeMove(Enum):
    none = 0
    move_and_hmz = 1
    relative_move = 2
    initial_position = 3
    high_limit = 4
    low_limit = 5
    hard_hi_limit = 6
    hard_lo_limit = 7


class HomingState(Enum):
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
