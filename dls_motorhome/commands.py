"""
The commands module contains functions that can be called directly
from the homing PLC definition file.

These functions are used to define PLCs, axes and axis groupings.

The other two modules that define functions to be called from the homing
PLC definition are:

    - predefined: a set of commonly used predefined homing sequences
    - snippets: a set of blocks of PLC code combined by predfined above

The intention of using global functions in these 3 modules is so that the PLC
definition can be relatively terse and the author does not need to worry about
classes and objects.

For example the following code will output a PLC 11 that defines a group of
axes including axis 1 and axis 2. It will provide a standard home switch
(or home mark) homing sequence::

    from commands import plc, group, motor, only_axes
    from predfined import home_hsw

    with plc(plc_num=11, controller=ControllerType.brick, filepath=tmp_file):
        motor(axis=1)
        motor(axis=2)

        with group(group_num=2, axes=[1, 2]):
            home_hsw()
"""

from pathlib import Path
from typing import List, Union

from dls_motorhome.onlyaxes import OnlyAxes

from .constants import ControllerType, PostHomeMove
from .group import Group
from .plc import Plc
from .snippets import (
    drive_relative,
    drive_to_hard_limit,
    drive_to_initial_pos,
    drive_to_soft_limit,
)

# continue_home_maintain_axes_offset,
# debug_pause,
# drive_to_home_if_on_limit,


###############################################################################
# functions to declare motors, groups, plcs
###############################################################################
def plc(
    plc_num: int, controller: Union[ControllerType, str], filepath: Union[Path, str]
) -> Plc:
    """
    Define a new PLC. Use this to create a new Plc context using the 'with' keyword
    like this::

        with plc(plc_num=13, controller=ControllerType.brick, filepath=tmp_file):
            motor(axis=1)
            with group(group_num=2, axes=[1]):
                command("; this PLC only contains this comment")

    Args:
        plc_num (int): Number of the generated homing PLC
        controller (ControllerType): Determines the class of controller Pmac or
            Geobrick
        filepath (pathlib.Path): The output file where the PLC will be written

    Returns:
        Plc: [description]
    """

    return Plc(plc_num, ControllerType(controller), Path(filepath))


def group(
    group_num: int,
    post_home: Union[PostHomeMove, str] = PostHomeMove.none,
    post_distance: int = 0,
) -> Group:
    """
    Define a new group of axes within a PLC that should be homed simultaneously.
    Use this to create a new context using the 'with' keyword from within a Plc
    context like this::

        with plc(plc_num=13, controller=ControllerType.brick, filepath=tmp_file):
            motor(axis=1)
            motor(axis=2)
            with group(group_num=2, axes=[1,2]):
                command("; this PLC only contains this comment")

    Args:
        group_num (int): an identifying number note that group 1 is reserved for
            homing all groups
        axes (List[int]): a list of axis numbers to include in the group
        post_home (PostHomeMove): action to perform on all axes after the
            home sequence completes

    Returns:
        Group:
    """
    return Plc.add_group(group_num, PostHomeMove(post_home), post_distance)


def comment(htype: str, post: str = "None") -> None:
    Group.add_comment(htype, post)


def motor(axis: int, jdist: int = 0):
    """
    Declare a motor for use in subsequently defined groups

    Args:
        axis (int): axis number
        jdist (int): number of counts to jog after reaching a home mark
    """
    motor = Group.add_motor(axis, jdist)
    Plc.add_motor(axis, motor)


def only_axes(axes: List[int]) -> OnlyAxes:
    """
    Creates a context in which actions are performed on a subset of the groups axes

    e.g the following  function ensures that the horizontal and vertical blades
    of a set of slits do not clash by moving them all to their limits and then
    homing each pair individually (to be called in a group context with
    4 axes defined)::

        def home_slits_hsw(posx: int, negx: int, posy: int, negy: int):
            drive_to_limit(homing_direction=False)

            with only_axes([posx, negx]):
                home_hsw()
            with only_axes([posy, negy]):
                home_hsw()

    Args:
        axes (List[int]): List of axis numbers

    Returns:
        OnlyAxes:
    """
    return OnlyAxes(axes)


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
    elif group.post_home == PostHomeMove.relative_move:
        drive_relative(distance=group.post_distance)
    elif group.post_home == PostHomeMove.move_and_hmz:
        drive_relative(distance=group.post_distance, set_home=True)
    elif group.post_home == PostHomeMove.move_absolute:
        # TODO this is wrong - we need a jog absolute snippet
        drive_relative(distance=group.post_distance)
    else:
        pass
