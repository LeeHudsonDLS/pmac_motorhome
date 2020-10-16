"""
All of these functions will insert a small snippet of PLC code into the
generated PLC. Each snippet performs a specific action on all of the axes
in a group simultaneously.

They should be called in the context of a Group object.

For example this code
will create a homing PLC 12 for a group of axes which does nothing except
drive all of them to their limit in the opposite direction to the homing
direction::

    with plc(plc_num=12, controller=ControllerType.brick, filepath=tmp_file):
        motor(axis=1)
        motor(axis=2)
        with group(group_num=2, axes=[1, 2]):
            # drive opposite to homing direction
            # continue if some axes have hit their limits
            drive_to_limit(homing_direction=False, with_limits=False)
"""

import inspect
from functools import wraps
from typing import Any, Callable, Dict, TypeVar, cast

from .group import Group


# the command action simply inserts the text in 'cmd' into the PLC output
def command(cmd):
    Group.add_action(Group.command, cmd=cmd)


snippet_docstring = """
    This will cause the jinja template {template} to be expanded and inserted
    into the PLC code. The template is as follows:

    .. include:: ../../dls_motorhome/snippets/{template}
        :literal:
"""

wait_for_done_docstring = """

    The included template wait_for_done.pmc.jinja allows this function to take these
    additional parameters which all default to False:

    Args:
        no_following_err (bool): don't check for following error during moves
        with_limits (bool): check for limits during the move. When False we continue
            waiting even if a subset of the axes have stopped on a limit
        wait_for_one_motor (bool): stop wating as soon as one of the motors
            has stopped instead of waiting for all motors
"""

# jinja snippets that include wait_for_done.pmc.jinja also may pass
# these arguments - the dictionary values are the defaults
wait_for_done_args = {
    "no_following_err": False,
    "with_limits": False,
    "wait_for_one_motor": False,
}

F = TypeVar("F", bound=Callable)


# TODO big explanation required!
def snippet_function(*arglists: Dict[str, Any]) -> Callable[[F], F]:
    def wrap(wrapped: F) -> F:
        sig = inspect.signature(wrapped)
        assert (
            "kwargs" in sig.parameters.keys() or len(arglists) == 0
        ), f"Bad snippet function definition - {wrapped.__name__} must take **kwargs"

        merged_args = {}
        # merge in any included jinja tempates arguments with defaults
        for included_args in arglists:
            merged_args.update(included_args)
        # add in the snippet function's arguments, possibly overriding above defaults
        merged_args.update({k: v.default for k, v in sig.parameters.items()})

        @wraps(wrapped)
        def wrapper(**kwargs) -> None:
            bad_keys = kwargs.keys() - merged_args.keys()
            assert (
                len(bad_keys) == 0
            ), f"illegal arguments: {wrapped.__name__} does not take {bad_keys}"

            all_merged = merged_args.copy()
            all_merged.update(kwargs)

            # add a jinja snippet and its processed arguments to the current group
            Group.add_snippet(wrapped.__name__, **all_merged)

        # insert the original function's signature at the top of the docstring
        doc = wrapped.__name__ + str(sig)
        # then insert the original function's docstring
        doc += wrapped.__doc__ or ""
        # insert information about jinja the template this function is expanding
        doc += str.format(snippet_docstring, template=wrapped.__name__ + ".pmc.jinja")
        # insert documentation on any jinja templates included by the above template
        if wait_for_done_args in arglists:
            doc += wait_for_done_docstring
        wrapper.__doc__ = doc

        return cast(F, wrapper)

    return wrap


# TODO state should be an enum
@snippet_function(wait_for_done_args)
def drive_to_limit(state="PreHomeMove", homing_direction=False, **kwargs):
    """
    Jog all of the group's axes until they have each hit a limit

    Args:
        state (str): Which homing state to report to EPICS for monitoring
        homing_direction (bool): When True Jog in the same direction as
            the axis' homing direction, defaults False: opposite to homing direction
    """


@snippet_function(wait_for_done_args)
def drive_off_home(
    state="FastRetrace", homing_direction=False, with_limits=True, **kwargs
):
    """
    Jog all the group's axes until the home flag is released

    Args:
        state (str): Which homing state to report to EPICS for monitoring
        homing_direction (bool): When True Jog in the same direction as
            the axis' homing direction, defaults False: opposite to homing direction
        with_limits (bool): check for limits during the move
    """


@snippet_function()
def store_position_diff():
    """
    Save the current offset from the original position.

    This is only required in order to support driving back to initial position
    after the home operation is complete
    """


@snippet_function(wait_for_done_args)
def drive_to_home(
    state="PreHomeMove", homing_direction=False, restore_homed_flags=False, **kwargs
):
    """
    drive all axes in the group until they hit the home flag or a limit

    Args:
        state (str): Which homing state to report to EPICS for monitoring
        homing_direction (bool): When True Jog in the same direction as
            each axis' homing direction, defaults False: opposite to homing direction
        restore_homed_flags (bool): restore the home flags original state before
            starting. Required if a previous step changed the home flags
    """


@snippet_function(wait_for_done_args)
def home(with_limits=True, **kwargs):
    """
    Initiate the home command on all axes in the group

    Args:
        with_limits (bool): check for limits during the move
    """


@snippet_function()
def debug_pause():
    """
    When running in debug mode, pause until the user indicates to continue
    """


@snippet_function(wait_for_done_args)
def drive_to_initial_pos(with_limits=True, **kwargs):
    """
    return all axes in the group to their original positions before the homing
    sequence began. Requires that store_position_diff was called before home.

    Args:
        with_limits (bool): check for limits during the move
    """


@snippet_function(wait_for_done_args)
def drive_to_soft_limit(homing_direction=False, with_limits=True, **kwargs):
    """
    drive all axes in the group until they hit their soft limits

    Args:
        homing_direction (bool): When True Jog in the same direction as
            each axis' homing direction, defaults False: opposite to homing direction
        with_limits (bool): check for limits during the move
    """


@snippet_function(wait_for_done_args)
def drive_relative(distance="123456", set_home=False, with_limits=True, **kwargs):
    """
    drive all axes in the group a relative distance from current position

    Args:
        distance (str): distance in counts
        set_home (bool): set the home flag afterward if True
        with_limits (bool): check for limits during the move
    """


@snippet_function()
def check_homed():
    """
    verfiy that all axes in the group are homed. Set error condition if not.
    """


@snippet_function(wait_for_done_args)
def drive_to_home_if_on_limit(homing_direction=False, **kwargs):
    ...


@snippet_function()
def disable_limits():
    ...


@snippet_function()
def restore_limits():
    ...


@snippet_function(wait_for_done_args)
def drive_to_hard_limit(state="PostHomeMove", homing_direction=False, **kwargs):
    ...


@snippet_function(wait_for_done_args)
def jog_if_on_limit(homing_direction=False, **kwargs):
    ...


@snippet_function(wait_for_done_args)
def continue_home_maintain_axes_offset(**kwargs):
    ...
