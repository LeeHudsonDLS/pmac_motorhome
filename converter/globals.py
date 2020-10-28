from typing import Callable, Optional

from dls_motorhome.constants import ControllerType
from dls_motorhome.sequences import (
    home_home,
    home_hsw,
    home_hsw_dir,
    home_hsw_hlim,
    home_hsw_hstop,
    home_limit,
    home_nothing,
    home_rlim,
)

HOME = 0
LIMIT = 1
HSW = 2
HSW_HLIM = 3
HSW_DIR = 4
RLIM = 5
NOTHING = 6
HSW_HSTOP = 7

NO_HOMING_YET = -1

PMAC = 0
GEOBRICK = 1
BRICK = 1


class HomingSequence:
    def __init__(self, function: Optional[Callable]):
        self.function = function
        if function is None:
            self.name = "No Homing Type Specified"
        else:
            self.name = function.__name__

    def __repr__(self) -> str:
        return self.name


HomingSequences = {
    NO_HOMING_YET: HomingSequence(None),
    HOME: HomingSequence(home_home),
    LIMIT: HomingSequence(home_limit),
    HSW: HomingSequence(home_hsw),
    HSW_HLIM: HomingSequence(home_hsw_hlim),
    HSW_DIR: HomingSequence(home_hsw_dir),
    RLIM: HomingSequence(home_rlim),
    NOTHING: HomingSequence(home_nothing),
    HSW_HSTOP: HomingSequence(home_hsw_hstop),
}


class BrickType:
    def __init__(self, type: ControllerType) -> None:
        self.type = type
        self.name = str(type)

    def __repr__(self) -> str:
        return self.name


BrickTypes = {
    PMAC: BrickType(ControllerType.pmac),
    GEOBRICK: BrickType(ControllerType.brick),
    BRICK: BrickType(ControllerType.brick),
}
