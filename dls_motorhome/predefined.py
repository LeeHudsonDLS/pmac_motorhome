from .commands import only_axes, post_home
from .group import Group
from .snippets import (
    check_homed,
    disable_limits,
    drive_off_home,
    drive_to_home,
    drive_to_limit,
    home,
    jog_if_on_limit,
    restore_limits,
    store_position_diff,
)


###############################################################################
# common action sequences to recreate htypes= from the original motorhome.py
###############################################################################
def home_rlim():
    """
    Home on release of a limit

    This can also be used for homing on a rotary encoder (back of motor)
    with an index mark on the rotation: Drive to limit and then home away
    from limit to the first index mark.

    - (Prehome Move) Jog in -hdir until the limit switch is hit
    - (Fast Search) Jog in hdir until the limit switch is released
    - (Fast Retrace) Jog in -hdir until the limit switch is hit
    - (Home) Home

    Finally do post home move if any.

    This example shows homing off the -ve limit with +ve hdir.
    E.g. ixx23 = 1, msyy,i912 = 10, msyy,i913 = 2.

    .. image:: images/RLIM.png
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
    Home on a home switch or index mark.

    - (Prehome Move) Jog in -hdir until either index/home switch (Figure 1) or
      limit switch (Figure 2)
    - (Fast Search) Jog in hdir until index/home switch
    - (Fast Retrace) Jog in -hdir until off the index/home switch
    - (Home) Home

    Finally do post home move if any.

    .. image:: images/HSW.png
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
    Home on a home switch or index mark on a stage that has no limit switches.

    Detection of following error due to hitting the hard stop is taken as the
    limit indication.

    - (Prehome Move) Jog in -hdir until following error - Ixx97 (in-position
      trigger mode) set to 3 for this phase.
    - (Fast Search) Jog in hdir until index/home switch
    - (Fast Retrace) Jog in -hdir until off the index/home switch
    - (Home) Home

    Finally do post home move if any.

    The axis must be configured to trigger on home index or home flag
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
    # TODO review why this reference to Group is required
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
