"""
Group Snippet function will insert a snippet of PLC code
using a jinja template with function name as priefix (func_name.pmc.jinja)
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
        with_limits (bool): check for limits during the move
        wait_for_one_motor (bool): proceed to the next block as soon as one of
            the motors have stopped instead of waiting for all motors
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
        # plus kwargs if we have added included jinja templates arguments
        if arglists:
            doc = doc[:-1] + ", **kwargs)"
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
def drive_to_limit(state="PreHomeMove", homing_direction=False):
    """
    Jog all of the group's axes until they have each hit a limit

    Args:
        state (str): Which homing state to report to EPICS for monitoring
        homing_direction (bool): When True Jog in the same direction as
            the axis' homing direction, defaults False: opposite to homing direction
    """


@snippet_function(wait_for_done_args)
def drive_off_home(state="FastRetrace", homing_direction=False, with_limits=True):
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
    ...


@snippet_function(wait_for_done_args)
def drive_to_home(
    state="PreHomeMove", homing_direction=False, restore_homed_flags=False
):
    ...


@snippet_function(wait_for_done_args)
def home(with_limits=True):
    ...


@snippet_function()
def debug_pause():
    ...


@snippet_function(wait_for_done_args)
def drive_to_initial_pos(with_limits=True):
    ...


@snippet_function(wait_for_done_args)
def drive_to_soft_limit(homing_direction=False, with_limits=True):
    ...


@snippet_function(wait_for_done_args)
def drive_relative(distance="123456", set_home=False, with_limits=True):
    ...


@snippet_function()
def check_homed():
    ...


@snippet_function(wait_for_done_args)
def drive_to_home_if_on_limit(homing_direction=False):
    ...


@snippet_function()
def disable_limits():
    ...


@snippet_function()
def restore_limits():
    ...


@snippet_function(wait_for_done_args)
def drive_to_hard_limit(state="PostHomeMove", homing_direction=False):
    ...


@snippet_function(wait_for_done_args)
def jog_if_on_limit(homing_direction=False):
    ...


@snippet_function(wait_for_done_args)
def continue_home_maintain_axes_offset():
    ...
