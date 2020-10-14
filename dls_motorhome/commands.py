"""
The commands module  contains all of the methods that can be called directly
from the homing PLC definition file.

The intention of using global methods is so that the PLC definition can be
relatively terse and the author does not need to worry about classes and
objects.

e.g.

from commands import plc, group, motor, only_axes, home_rlim

with plc(plc_num=11, controller=ControllerType.brick, filepath=tmp_file):
    motor(axis=1)
    motor(axis=2)

    with group(group_num=2, axes=[1, 2]):
        home_rlim()
        with only_axes(axes=[1]):
            drive__to_limit(homing_direction=False)
"""

from pathlib import Path
from typing import List

from dls_motorhome.onlyaxes import OnlyAxes

from .constants import ControllerType, PostHomeMove
from .group import Group
from .plc import Plc
from .snippets import (
    check_homed,
    disable_limits,
    drive_off_home,
    drive_relative,
    drive_to_hard_limit,
    drive_to_home,
    drive_to_initial_pos,
    drive_to_limit,
    drive_to_soft_limit,
    home,
    jog_if_on_limit,
    restore_limits,
    store_position_diff,
)

# continue_home_maintain_axes_offset,
# debug_pause,
# drive_to_home_if_on_limit,


###############################################################################
# functions to declare motors, groups, plcs
###############################################################################
def plc(plc_num: int, controller: ControllerType, filepath: Path) -> Plc:
    return Plc(plc_num, controller, filepath)


def group(
    group_num: int, axes: List[int], post_home: PostHomeMove = PostHomeMove.none,
) -> Group:
    return Plc.add_group(group_num, axes, post_home)


def comment(htype: str, post: str = "None") -> None:
    Group.add_comment(htype, post)


def motor(axis: int, jdist: int = 0):
    Plc.add_motor(axis, jdist)


def only_axes(axes: List[int]) -> OnlyAxes:
    group = Group.instance()
    return OnlyAxes(group, axes)


###############################################################################
# post_home actions to recreate post= from the original motorhome.py
###############################################################################
def post_home(**args):
    group = Group.the_group
    if group.post_home == PostHomeMove.none:
        pass
    elif group.post_home == PostHomeMove.initial_position:
        drive_to_initial_pos(**args)
    elif group.post_home == PostHomeMove.high_limit:
        drive_to_soft_limit(homing_direction=True)
    elif group.post_home == PostHomeMove.low_limit:
        drive_to_soft_limit(homing_direction=False)
    elif group.post_home == PostHomeMove.hard_hi_limit:
        drive_to_hard_limit(homing_direction=True)
    elif group.post_home == PostHomeMove.hard_lo_limit:
        drive_to_hard_limit(homing_direction=False)
    elif type(group.post_home) == str and group.post_home.startswith("r"):
        distance = group.post_home.strip("r")
        drive_relative(distance=distance)
    elif type(group.post_home) == str and group.post_home.startswith("z"):
        distance = group.post_home.strip("z")
        drive_relative(distance=distance, set_home=True)
    elif group.post_home not in (None, 0, "0"):
        drive_relative(distance=group.post_home)
    else:
        pass


###############################################################################
# common action sequences to recreate htypes= from the original motorhome.py
###############################################################################
def home_rlim():
    """
    RLIM the axis must be configured to trigger on release of limit
    """
    # drive in opposite to homing direction until limit hit
    drive_to_limit(homing_direction=False)
    drive_to_home(
        with_limits=False, homing_direction=True, state="FastSearch"
    )  # drive away from limit until it releases
    store_position_diff()
    drive_off_home(with_limits=False)  # drive back onto limit switch
    home(with_limits=False)
    check_homed()
    post_home()


def home_hsw():
    """
    HSW the axis must be configured to trigger on home index or home flag
    """
    # drive in opposite to homing direction until home flag or limit hit
    drive_to_home(homing_direction=False)
    drive_to_home(with_limits=True, homing_direction=True, state="FastSearch")
    store_position_diff()
    drive_off_home()
    home()
    check_homed()
    post_home()


def home_hsw_hstop():
    """
    HSW_STOP the axis must be configured to trigger on home index or home flag
    this is used when there are hard stops instead of limit switches
    e.g. piezo walker
    """
    # drive in opposite to homing direction until home flag or following error
    drive_to_home(no_following_err=True, homing_direction=False)
    drive_to_home(with_limits=True, homing_direction=True, state="FastSearch")
    store_position_diff()
    drive_off_home(homing_direction=False)
    home(with_limits=True)
    check_homed()


def home_hsw_dir():
    """
    HSW_DIR home on a directional home switch
    """
    drive_off_home(state="PreHomeMove")
    drive_to_home(
        homing_direction=True,
        with_limits=True,
        state="FastSearch",
        restore_homed_flags=True,
    )
    store_position_diff()
    drive_off_home(homing_direction=False, state="FastRetrace")
    home()
    check_homed()
    post_home()


def home_limit():
    """
    LIMIT
    """
    drive_to_home(homing_direction=True, state="FastSearch")
    store_position_diff()
    drive_off_home(with_limits=False)
    disable_limits()
    home()
    restore_limits()
    check_homed()
    post_home()


def home_hsw_hlim():
    """
    HSW_HLIM
    """
    drive_to_home(homing_direction=True)
    jog_if_on_limit()
    drive_to_home(homing_direction=True, state="FastSearch", with_limits=True)
    store_position_diff()
    drive_off_home(homing_direction=False, state="FastRetrace")
    home()
    check_homed()
    post_home()


def home_home():
    """
    HOME
    """
    home()
    check_homed()
    post_home()


def home_nothing():
    """
    NOTHING
    In original code, this required a homing type other than NOTHING used
    in the same group otherwise compilation would fail.
    Simply goes through to post home move without homing or changing home status.
    """
    Group.the_group.htype = "NOTHING"
    post_home()


###############################################################################
# functions for some common motor combinations
###############################################################################


def home_slits_hsw(posx: int, negx: int, posy: int, negy: int):
    drive_to_limit(homing_direction=False)

    with only_axes([posx, negx]):
        home_hsw()
    with only_axes([posy, negy]):
        home_hsw()
