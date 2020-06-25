from typing import List

from .contants import PostHomeMove, Controller
from .group import Group
from .plc import Plc


###############################################################################
# functions to declare motors, groups, plcs
###############################################################################
def plc(plc_num: int, controller: Controller, filepath: str) -> Plc:
    return Plc(plc_num, controller, filepath)


def motor(axis: int, jdist: int = 0, post_home: PostHomeMove = PostHomeMove.none):
    Plc.add_motor(axis, jdist, post_home)


def group(group_num: int, axes: List[int]) -> Group:
    return Plc.add_group(group_num, axes)


###############################################################################
# individual PLC action functions
###############################################################################
def drive_neg_to_limit():
    Group.add_snippet("drive_neg_to_limit")


def drive_pos_off_home():
    Group.add_snippet("drive_pos_off_home")


def drive_neg_to_inverse_home():
    Group.add_snippet("drive_neg_to_inverse_home")


def store_position_diff():
    Group.add_snippet("store_position_diff")


def home():
    Group.add_snippet("home")


def debug_pause():
    Group.add_snippet("debug_pause")


###############################################################################
# predefined action sequences to recreate htypes the original motorhome.py
###############################################################################
def home_rlim():
    drive_neg_to_limit()
    drive_pos_off_home()
    store_position_diff()
    drive_neg_to_inverse_home()
    home()
