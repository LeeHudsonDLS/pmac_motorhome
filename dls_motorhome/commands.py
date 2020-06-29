from pathlib import Path
from typing import List

from .constants import Controller, PostHomeMove
from .group import Group
from .plc import Plc


###############################################################################
# functions to declare motors, groups, plcs
###############################################################################
def plc(plc_num: int, controller: Controller, filepath: Path) -> Plc:
    return Plc(plc_num, controller, filepath)


def group(
    group_num: int, axes: List[int], post_home: PostHomeMove = PostHomeMove.none
) -> Group:
    return Plc.add_group(group_num, axes, post_home)


def comment(htype: str, post: str = "None") -> None:
    Group.add_comment(htype, post)


def motor(axis: int, jdist: int = 0):
    Plc.add_motor(axis, jdist)


###############################################################################
# individual PLC action functions
###############################################################################
def set_axes(axes):
    Group.add_action(Group.set_axis_filter, axes=axes)


def command(cmd):
    Group.add_action(Group.command, cmd=cmd)


def drive_neg_to_limit(**args):
    Group.add_snippet("drive_neg_to_limit", **args)


def drive_pos_off_home(**args):
    Group.add_snippet("drive_pos_off_home", **args)


def drive_neg_to_inverse_home(**args):
    Group.add_snippet("drive_neg_to_inverse_home", **args)


def store_position_diff(**args):
    Group.add_snippet("store_position_diff", **args)


def drive_neg_to_home(**args):
    Group.add_snippet("drive_neg_to_home", **args)


def drive_pos_to_home(**args):
    Group.add_snippet("drive_pos_to_home", **args)


def home(**args):
    Group.add_snippet("home", **args)


def debug_pause():
    Group.add_snippet("debug_pause")


def drive_to_initial_pos(**args):
    Group.add_snippet("drive_to_initial_pos", **args)


def check_homed(**args):
    Group.add_snippet("check_homed", **args)


###############################################################################
# post_home actions to recreate post= from the original motorhome.py
###############################################################################
def post_home(**args):
    group = Group.the_group
    if group.post_home == PostHomeMove.initial_position:
        drive_to_initial_pos(**args)
    elif group.post_home == PostHomeMove.low_limit:
        pass  # TODO add the rest of the post home move types
    # etc.


###############################################################################
# common action sequences to recreate htypes= from the original motorhome.py
###############################################################################
def home_rlim():
    drive_neg_to_limit()
    drive_pos_off_home()
    store_position_diff()
    drive_neg_to_inverse_home()
    home()
    check_homed()
    post_home()


def home_hsw():
    drive_neg_to_home()
    drive_pos_off_home(with_limits=True)
    store_position_diff()
    drive_neg_to_inverse_home(with_limits=True)
    home(with_limits=True)
    check_homed()
    post_home(with_limits=True)


def home_hsw_hstop():
    drive_neg_to_home(no_following_err=True)
    drive_pos_to_home(with_limits=True)
    store_position_diff()
    drive_neg_to_inverse_home(with_limits=True)
    home(with_limits=True)
    check_homed()


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
        drive_neg_to_limit()
        set_axes([posx, negx])
        home_hsw()
        set_axes([posy, negy])
        home_hsw()
