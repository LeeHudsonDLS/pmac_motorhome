from pathlib import Path
from typing import List, cast

from dls_motorhome.onlyaxes import OnlyAxes

from .constants import Controller, PostHomeMove
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

with plc(plc_num=11, controller=Controller.brick, filepath=tmp_file):
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


def drive_to_trigger(with_limits=True):
    Group.add_snippet("drive_to_trigger", **locals())


def drive_to_inverse_home(with_limits=True, negative=True):
    Group.add_snippet("drive_to_inverse_home", **locals())


def store_position_diff(**args):
    Group.add_snippet("store_position_diff", **args)


def drive_to_home(
    with_limits=False, negative=True, no_following_err=False, state="PreHomeMove"
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
    """
    RLIM the axis must be configured to trigger home flag on release of limit
    """
    drive_to_limit()
    drive_to_trigger(with_limits=False)  # drive away from limit until it releases
    store_position_diff()
    drive_to_inverse_home(with_limits=False)  # drive back onto limit switch
    home(with_limits=False)
    check_homed()
    post_home()


def home_hsw():
    drive_to_home()
    drive_to_trigger()
    store_position_diff()
    drive_to_inverse_home()
    home()
    check_homed()
    post_home()


def home_hsw_hstop():
    drive_to_home(no_following_err=True, negative=True)
    drive_to_home(with_limits=True, negative=False, state="FastSearch")
    store_position_diff()
    drive_to_inverse_home(negative=True)
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
        drive_to_limit()
        with only_axes([posx, negx]):
            home_hsw()
        with only_axes([posy, negy]):
            home_hsw()
