from collections import OrderedDict
from pathlib import Path
from typing import List, cast

from .constants import Controller, PostHomeMove
from .group import Group
from .motor import Motor
from .plcgenerator import PlcGenerator


class Plc:
    def __init__(self, plc_num: int, controller: Controller, filepath: Path) -> None:
        self.filepath = Path(filepath)
        self.plc_num = plc_num
        self.groups: List[Group] = []
        self.motors: OrderedDict[int, Motor] = OrderedDict()
        self.generator = PlcGenerator()
        if not self.filepath.parent.exists():
            raise ValueError("bad file path")
        if (
            self.plc_num < 8  # PLCs 1-8 are reserved
            or self.plc_num > 32  # highest PLC number possible
            or not isinstance(self.plc_num, int)
        ):
            raise ValueError("plc_number should be integer between 9 and 32")

    the_plc = None

    def __enter__(self):
        assert not Plc.the_plc
        Plc.the_plc = self
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        # write out PLC
        plc_text = self.generator.render("plc.pmc.jinja", plc=self)
        with self.filepath.open("w") as stream:
            stream.write(plc_text)
        Plc.the_plc = None
        Motor.instances = []

    @classmethod
    def add_group(
        cls, group_num: int, axes: List[int], post_home: PostHomeMove, **args
    ) -> Group:
        plc = cast("Plc", cls.the_plc)
        assert set(axes).issubset(
            plc.motors
        ), f"invalid axis numbers for group {group_num}"
        motors = [motor for axis_num, motor in plc.motors.items() if axis_num in axes]
        group = Group(group_num, motors, post_home, **args)
        plc.groups.append(group)
        return group

    @classmethod
    def add_motor(cls, axis: int, jdist: int):
        plc = cast("Plc", cls.the_plc)
        assert (
            axis not in plc.motors
        ), f"motor {axis} already defined in plc {plc.plc_num}"
        motor = Motor(axis, jdist, plc.plc_num)
        plc.motors[axis] = motor

    @property
    def count(self) -> int:
        return len(self.groups)

    def _all_axes(self, format: str, separator: str, *arg) -> str:
        all = [format.format(*arg, **ax.dict) for ax in self.motors.values()]
        return separator.join(all)

    ############################################################################
    # the following functions are callled from Jinja templates to generate
    # snippets of PLC code that act on all motors in a plc
    ############################################################################

    def save_hi_limits(self):
        return self._all_axes("P{hi_lim}=i{axis}13", " ")

    def restore_hi_limits(self):
        return self._all_axes("i{axis}13=P{hi_lim}", " ")

    def save_lo_limits(self):
        return self._all_axes("P{lo_lim}=i{axis}14", " ")

    def restore_lo_limits(self):
        return self._all_axes("i{axis}14=P{lo_lim}", " ")

    def save_homed(self):
        return self._all_axes("P{homed}=i{homed_flag}", " ")

    def save_not_homed(self):
        return self._all_axes("P{not_homed}=P{homed}^$C", " ")

    def restore_homed(self):
        return self._all_axes("i{homed_flag}=P{homed}", " ")

    def save_limit_flags(self):
        return self._all_axes("P{lim_flags}=i{axis}24", " ")

    def restore_limit_flags(self):
        return self._all_axes("i{axis}24=P{lim_flags}", " ")

    def save_position(self):
        return self._all_axes("P{pos}=M{axis}62", " ")

    def clear_limits(self):
        r = self._all_axes("i{axis}13=0", " ")
        r += "\n"
        r += self._all_axes("i{axis}14=0", " ")
        return r

    def stop_motors(self):
        return self._all_axes('if (m{axis}42=0)\n    cmd "#{axis}J/"\nendif', "\n")
