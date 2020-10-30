"""
The commands module contains functions that can be called directly
from the `PlcDefinition`.

These functions are used to define PLCs, axes and axis groupings.
"""

from pathlib import Path
from typing import Union

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


def plc(
    plc_num: int, controller: Union[ControllerType, str], filepath: Union[Path, str]
) -> Plc:
    """
    Define a new PLC. Use this to create a new Plc context using the 'with'
    keyword.

    Must be called in the global context.

    Args:
        plc_num (int): Number of the generated homing PLC
        controller (ControllerType): Determines the class of controller Pmac or
            Geobrick
        filepath (pathlib.Path): The output file where the PLC will be written

    Returns:
        Plc: the Plc object for use in the context
    """

    return Plc(plc_num, ControllerType(controller), Path(filepath))


def group(
    group_num: int,
    post_home: Union[PostHomeMove, str] = PostHomeMove.none,
    post_distance: int = 0,
    comment: str = None,
) -> Group:
    """
    Define a new group of axes within a PLC that should be homed simultaneously.
    Use this to create a new context using the 'with' keyword from within a Plc
    context.

    Must be called in a Plc context.

    Args:
        group_num (int): an identifying number note that group 1 is reserved for
            homing all groups
        axes (List[int]): a list of axis numbers to include in the group
        post_home (PostHomeMove): action to perform on all axes after the
            home sequence completes

    Returns:
        Group: The Group object for use in the context
    """
    return Plc.add_group(group_num, PostHomeMove(post_home), post_distance, comment)


def comment(htype: str, post: str = "None") -> None:
    Group.add_comment(htype, post)


def motor(axis: int, jdist: int = 0, index: int = 0) -> None:
    """
    Declare a motor for use in the current group.

    Must be called in a group context.

    Args:
        axis (int): axis number
        jdist (int): number of counts to jog after reaching a home mark. Required
            to far enough to move off of the home mark.
        index (int): for internal use in conversion of old scripts sets
            the index of this motor to a different value than the order of
            declaration.
    """
    motor = Group.add_motor(axis, jdist, index)
    Plc.add_motor(axis, motor)


def only_axes(*axes: int) -> OnlyAxes:
    """
    Creates a context in which actions are performed on a subset of the groups axes

    Must be called in a group context.

    For an example of the use of this, see :doc:`../tutorials/custom`

    Args:
        axes int: List of axis numbers

    Returns:
        OnlyAxes: an OnlyAxes object for use in the context
    """
    return OnlyAxes(*axes)


###############################################################################
# post_home actions to recreate post= from the original motorhome.py
###############################################################################
def post_home(**args) -> None:
    """
    Perform one of the predefined post homing actions on all axes in the
    current group.

    Must be called in a Group context.

    This function is called as the last step in all of the :doc:`sequences`
    functions
    """
    group = Group.instance()

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
