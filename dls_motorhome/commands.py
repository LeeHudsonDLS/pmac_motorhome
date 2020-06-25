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


def motor(axis: int, jdist: int = 0):
    Plc.add_motor(axis, jdist)


def group(
    group_num: int, axes: List[int], post_home: PostHomeMove = PostHomeMove.none
) -> Group:
    return Plc.add_group(group_num, axes, post_home)


###############################################################################
# individual PLC action functions
###############################################################################
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
