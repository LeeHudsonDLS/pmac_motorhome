from pmac_motorhome.commands import PostHomeMove, group, motor, only_axes, plc
from pmac_motorhome.sequences import home_hsw
from pmac_motorhome.snippets import drive_to_limit


def custom_slits_hsw(posx, negx, posy, negy):
    drive_to_limit(homing_direction=False)  # drive all slits to limit away from home

    with only_axes(posx, posy):  # home and return to limit only positive slits
        home_hsw()
        drive_to_limit(homing_direction=False)

    with only_axes(negx, negy):  # home and return to limit only negative slits
        home_hsw()
        drive_to_limit(homing_direction=False)


with plc(
    plc_num=12, controller="brick", filepath="/tmp/PLC12_CUSTOM_SLITS_HM.pmc",
):
    initial = PostHomeMove.initial_position
    with group(group_num=2, post_home=initial):
        motor(axis=1, jdist=-400)
        motor(axis=2, jdist=-400)
        motor(axis=3, jdist=-400)
        motor(axis=4, jdist=-400)

        custom_slits_hsw(posx=1, negx=2, posy=3, negy=4)
