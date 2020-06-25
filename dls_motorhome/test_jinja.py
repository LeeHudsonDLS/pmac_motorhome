from collections import OrderedDict
from enum import Enum
from pathlib import Path
from typing import List, Optional, cast

from jinja2 import Environment, FileSystemLoader

this_path = Path(__file__).parent
jinja_path = this_path.parent / "snippets"

templateLoader = FileSystemLoader(searchpath=jinja_path)
environment = Environment(loader=templateLoader)

# offsets into the PLC's PVariables for storing the state of axes
# these names go into long format strings so keep them short for legibility
PVARS = {
    "hi_lim": 4,
    "lo_lim": 20,
    "homed": 36,
    "not_homed": 52,
    "lim_flags": 68,
    "pos": 84,
}


class Motor:
    instances: List["Motor"] = []

    def __init__(self, axis: int, jdist: int, plc_num: int) -> None:
        self.axis = axis
        self.jdist = jdist
        self.index = len(self.instances)
        self.instances.append(self)
        self.post: str = "None"  # TODO need to pass this
        # dict is for terse string formatting code in _all_axes() functions
        self.dict = {
            "axis": axis,
            "index": self.index,
            "jdist": jdist,
            "homed_flag": f"7{self.nx}2",
        }
        for name, start in PVARS.items():
            self.dict[name] = plc_num * 100 + start + self.index

    # TODO IMPORTANT - this is used in finding the Home capture flags etc. and is
    # specific to Geobrick - For a full implementation see Motor class in
    #  ... pmacutil/pmacUtilApp/src/motorhome.py
    # HINT: watch out for python 2 vs python 3 handling of integer arithmetic
    @property
    def nx(self) -> str:
        nx = int(int((self.axis - 1) / 4) * 10 + int((self.axis - 1) % 4 + 1))
        return "{:02}".format(nx)


class PlcGenerator:
    def __init__(self) -> None:
        this_path = Path(__file__).parent
        jinja_path = this_path.parent / "snippets"
        # TODO REMOVE
        jinja_path = Path("/home/giles/dls/dls_motorhome/dls_motorhome/snippets")
        self.templateLoader = FileSystemLoader(searchpath=jinja_path)
        self.environment = Environment(
            loader=self.templateLoader,
            trim_blocks=False,
            lstrip_blocks=True,
            keep_trailing_newline=False,
        )

    def render(self, template_name: str, **args) -> str:
        template = self.environment.get_template(template_name)
        output = template.render(**args)

        return output


class Controller(Enum):
    brick = 1
    pmac = 2


class PostHomeMove(Enum):
    none = 0
    move_and_hmz = 1
    relative_move = 2
    initial_position = 3
    high_limit = 4
    low_limit = 5
    hard_hi_limit = 6
    hard_lo_limit = 7


class HomingState(Enum):
    StateIdle = 0
    StateConfiguring = 1
    StateMoveNeg = 2
    StateMovePos = 3
    StateHoming = 4
    StatePostHomeMove = 5
    StateAligning = 6
    StateDone = 7
    StateFastSearch = 8
    StateFastRetrace = 9
    StatePreHomeMove = 10


class Group:
    # TODO this probably needs to be merged into your Group class that implements
    # the python contexts
    # TODO htype should have a class
    def __init__(self, group_num: int, axes: List[Motor], htype: str = "RLIM",) -> None:
        self.axes = axes
        self.htype = htype
        self.comments: str = self.make_comment()
        self.group_num = group_num
        self.templates: List[str] = []

    the_group: Optional["Group"] = None

    def __enter__(self):
        assert not Group.the_group
        Group.the_group = self
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        Group.the_group = None

    @property
    def count(self) -> int:
        return len(self.templates)

    def make_comment(self) -> str:
        return "\n".join(
            [
                f";  Axis {ax.axis}: htype = {self.htype}, "
                f"jdist = {ax.jdist}, post = {ax.post}"
                for ax in self.axes
            ]
        )

    @classmethod
    def add_snippet(cls, template_name: str):
        # funky casting required for type hints since we init the_group to None
        group = cast("Group", cls.the_group)
        group.templates.append(template_name)

    def _all_axes(self, format: str, separator: str, *arg) -> str:
        # to the string format: pass any extra arguments first, then the dictionary
        # of the axis object so its elements can be addressed by name
        all = [format.format(*arg, **ax.dict) for ax in self.axes]
        return separator.join(all)

    def jog_axes(self) -> str:
        return self._all_axes("#{axis}J^*", " ")

    def jog_axes_jdist(self) -> str:
        return self._all_axes("#{axis}J^*^{jdist}", " ")

    def set_large_jog_distance(self, negative: bool = True) -> str:
        sign = "-" if negative else ""
        return self._all_axes(
            "m{axis}72=100000000*({0}i{axis}23/ABS(i{axis}23))", " ", sign
        )

    def in_pos(self) -> str:
        return self._all_axes("m{axis}40", "&")

    def following_err(self) -> str:
        return self._all_axes("m{axis}42", "|")

    def homed(self) -> str:
        return self._all_axes("m{axis}45", "&")

    def clear_home(self) -> str:
        return self._all_axes("m{axis}45=0", " ")

    def store_position_diff(self):
        return self._all_axes(
            "P{pos}=(P{pos}-M{axis}62)/(I{axis}08*32)+{jdist}-(i{axis}26/16)",
            separator="\n        ",
        )

    def negate_home_flags(self):
        return self._all_axes("i{homed_flag}=P{not_homed}", " ")

    def restore_home_flags(self):
        return self._all_axes("i{homed_flag}=P{homed}", " ")

    def home(self) -> str:
        return self._all_axes("#{axis}hm", " ")


class Plc:
    def __init__(self, plc_num: int, controller: Controller) -> None:
        self.plc_num = plc_num
        self.groups: List[Group] = []
        self.motors: OrderedDict[int, Motor] = OrderedDict()
        self.generator = PlcGenerator()

    the_plc = None

    def __enter__(self):
        assert not Plc.the_plc
        Plc.the_plc = self
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        # write out PLC
        print(self.generator.render("plc.pmc.jinja", plc=self))
        Plc.the_plc = None

    @classmethod
    def add_group(cls, group_num: int, axes: List[int]) -> Group:
        plc = cast("Plc", cls.the_plc)
        assert set(axes).issubset(
            plc.motors
        ), f"invalid axis numbers for group {group_num}"
        motors = [motor for axis_num, motor in plc.motors.items() if axis_num in axes]
        group = Group(group_num, motors)
        plc.groups.append(group)
        return group

    @classmethod
    def add_motor(cls, axis: int, jdist: int, post_home: PostHomeMove):
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






def motor(axis: int, jdist: int = 0, post_home: PostHomeMove = PostHomeMove.none):
    Plc.add_motor(axis, jdist, post_home)


def group(group_num: int, axes: List[int]) -> Group:
    return Plc.add_group(group_num, axes)


# Todo these functions should call a helper so we can make global changes easily
# e.g. need to add non template code with command()
def drive_to_limit(state=HomingState.StateFastRetrace):
    Group.add_snippet("drive_to_limit")


def drive_off_limit():
    Group.add_snippet("drive_off_limit")


def drive_to_inverse_home():
    Group.add_snippet("drive_to_inverse_home")


def store_position_diff():
    Group.add_snippet("store_position_diff")


def home():
    Group.add_snippet("home")


def debug_pause():
    Group.add_snippet("debug_pause")


def home_rlim():
    drive_to_limit()
    drive_off_limit()
    store_position_diff()
    drive_to_inverse_home()
    home()


with Plc(plc_num=11, controller=Controller.brick):
    motor(axis=1, jdist=0, post_home=PostHomeMove.none)
    motor(axis=2, jdist=0, post_home=PostHomeMove.none)
    motor(axis=4, jdist=0, post_home=PostHomeMove.none)
    motor(axis=5, jdist=0, post_home=PostHomeMove.none)

    with group(group_num=2, axes=[1, 2]):
        home_rlim()

    with group(group_num=3, axes=[4, 5]):
        home_rlim()
