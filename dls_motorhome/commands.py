from pathlib import Path
from typing import List, cast

from dls_motorhome.onlyaxes import OnlyAxes

from .constants import ControllerType, PostHomeMove
from .group import Group
from .plc import Plc


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
            drive__to_limit(negative=True)
"""


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
    group = cast("Group", Group.the_group)
    return OnlyAxes(group, axes)


###############################################################################
# individual PLC action functions
###############################################################################


def command(cmd):
    Group.add_action(Group.command, cmd=cmd)


def drive_to_limit(negative=True):
    Group.add_snippet("drive_to_limit", **locals())


def drive_off_home(with_limits=True, negative=True, state="FastRetrace"):
    Group.add_snippet("drive_off_home", **locals())


def store_position_diff(**args):
    Group.add_snippet("store_position_diff", **args)


def drive_to_home(
    with_limits=False,
    negative=True,
    no_following_err=False,
    state="PreHomeMove",
    restore_homed_flags=False,
):
    Group.add_snippet("drive_to_home", **locals())


def home(with_limits=True):
    Group.add_snippet("home", **locals())


def debug_pause():
    Group.add_snippet("debug_pause")


def drive_to_initial_pos(with_limits=True):
    Group.add_snippet("drive_to_initial_pos", **locals())


def check_homed():
    Group.add_snippet("check_homed")


def drive_to_home_if_on_limit(negative=True):
    Group.add_snippet("drive_to_home_if_on_limit")


def disable_limits():
    Group.add_snippet("disable_limits")


def restore_limits():
    Group.add_snippet("restore_limits")


def drive_to_hard_limit(**args):
    Group.add_snippet("drive_to_hard_limit", **args)


def jog_if_on_limit(negative=True):
    Group.add_snippet("jog_if_on_limit", **locals())


###############################################################################
# post_home actions to recreate post= from the original motorhome.py
###############################################################################
def post_home(**args):
    group = Group.the_group
    if group.post_home == PostHomeMove.initial_position:
        drive_to_initial_pos(**args)
    elif group.post_home == PostHomeMove.high_limit:
        # go to high soft limit
        pass
    elif group.post_home == PostHomeMove.low_limit:
        # go to low soft limit
        pass
    elif group.post_home == PostHomeMove.hard_hi_limit:
        # go to high hard limit, don't check for limits
        pass
    elif group.post_home == PostHomeMove.hard_lo_limit:
        drive_to_hard_limit(state="PostHomeMove", negative=True)
    elif type(group.post_home) == str and group.post_home.starswith("r"):
        # jog relative by post[1:]
        pass
    elif type(group.post_home) == str and group.post_home.starswith("z"):
        # go to post[1:]
        pass
    elif group.post_home not in (None, 0, "0"):
        # go to post
        pass
    # etc.


###############################################################################
# common action sequences to recreate htypes= from the original motorhome.py
###############################################################################
def home_rlim():
    """
    RLIM the axis must be configured to trigger on release of limit
    """
    # drive in opposite to homing direction until limit hit
    drive_to_limit(negative=True)
    drive_to_home(
        with_limits=False, negative=False, state="FastSearch"
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
    drive_to_home(negative=True)
    drive_to_home(with_limits=True, negative=False, state="FastSearch")
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
    drive_to_home(no_following_err=True, negative=True)
    drive_to_home(with_limits=True, negative=False, state="FastSearch")
    store_position_diff()
    drive_off_home(negative=True)
    home(with_limits=True)
    check_homed()


def home_hsw_dir():
    """
    HSW_DIR home on a directional home switch
    """
    drive_off_home(state="PreHomeMove")
    drive_to_home(
        negative=False, with_limits=True, state="FastSearch", restore_homed_flags=True
    )
    store_position_diff()
    drive_off_home(negative=True, state="FastRetrace")
    home()
    check_homed()
    post_home()


def home_limit():
    """
    LIMIT
    """
    drive_to_home(negative=False, state="FastSearch")
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
    drive_to_home(negative=False)
    jog_if_on_limit()
    drive_to_home(negative=False, state="FastSearch", with_limits=True)
    store_position_diff()
    drive_off_home(negative=True, state="FastRetrace")
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


###############################################################################
# functions for some common motor combinations
###############################################################################


def home_slits_hsw(
    group_num: int,
    posx: int,
    negx: int,
    posy: int,
    negy: int,
    jdist: int = 0,
    post: PostHomeMove = PostHomeMove.none,
):
    motor(axis=posx, jdist=jdist)
    motor(axis=negx, jdist=jdist)
    motor(axis=posy, jdist=jdist)
    motor(axis=negy, jdist=jdist)

    with group(group_num=group_num, axes=[posx, posy, negx, negy], post_home=post):
        comment("HSW", "i")
        drive_to_limit()
        with only_axes([posx, negx]):
            home_hsw()
        with only_axes([posy, negy]):
            home_hsw()
