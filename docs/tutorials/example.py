from dls_motorhome.commands import group, motor, plc
from dls_motorhome.sequences import home_hsw

with plc(
    plc_num=12, controller="brick", filepath="/tmp/PLC12_SLITS1_HM.pmc",
):
    with group(group_num=3):
        motor(axis=1)
        motor(axis=2)

        home_hsw()
