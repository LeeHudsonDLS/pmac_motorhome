from dls_motorhome.commands import ControllerType, group, motor, plc
from dls_motorhome.sequences import home_hsw

with plc(
    plc_num=12,
    controller=ControllerType.brick,
    filepath="/tmp/PLC12_SLITS1_HM.pmc",
):
    motor(axis=1, jdist=1500)
    motor(axis=2, jdist=1000)

    with group(group_num=3, axes=[1, 2]):
        home_hsw()
