from enum import Enum
from pathlib import Path
from typing import List

from jinja2 import Environment, FileSystemLoader

this_path = Path(__file__).parent
jinja_path = this_path.parent / "snippets"

templateLoader = FileSystemLoader(searchpath=jinja_path)
environment = Environment(loader=templateLoader)


class Motor:
    instances: List["Motor"] = []

    def __init__(self, axis: int, jdist: int) -> None:
        self.axis = axis
        self.jdist = jdist
        self.index = len(self.instances)
        self.instances.append(self)
        self.post: str = "None"  # TODO need to pass this
        # this is for terse string formatting code in Group._all_axes()
        self.dict = {"axis": axis, "index": self.index, "jdist": jdist}

    # TODO IMPORTANT - this is used in finding the Home capture flags etc. and is
    # specific to Geobrick - For a full implementation see Motor class in
    #  ... pmacutil/pmacUtilApp/src/motorhome.py
    # HINT: watch out for python 2 vs python 3 handling of integer arithmetic
    @property
    def nx(self) -> str:
        nx = int(int((self.axis - 1) / 4) * 10 + int((self.axis - 1) % 4 + 1))
        return "{:02}".format(nx)


class SnippetGenerator:
    def __init__(self) -> None:
        this_path = Path(__file__).parent
        jinja_path = this_path.parent / "snippets"
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


class Snippet(Enum):
    # TODO snippets will probably be more than just an enum
    # this will be become the connection between objects created in
    # the script and snippet template files
    # (and maybe snippet is not the right name for what this will become)
    pre_home = "pre_home_move"
    fast_search = "fast_search"
    debug = "debug_pause"
    store_pos = "store_position_diff"
    fast_retrace = "fast_retrace"
    home = "home"


class Group:
    # TODO this probably needs to be merged into your Group class that implements
    # the python contexts
    # TODO htype should have a class
    def __init__(self, axes: List[Motor], group_num: int, htype: str = "RLIM",) -> None:
        self.axes = axes
        self.htype = htype
        self.comments: str = self.make_comment()
        self.group_num = group_num
        self.snippets: List[Snippet] = []

    def make_comment(self) -> str:
        return "\n".join(
            [
                f";  Axis {ax.axis}: htype = {self.htype}, "
                f"jdist = {ax.jdist}, post = {ax.post}"
                for ax in self.axes
            ]
        )

    @property
    def count(self) -> int:
        return len(self.snippets)

    def _all_axes(self, template: str, separator: str, *arg) -> str:
        # to the string format: pass any extra arguments first, then the dictionary
        # of the axis object so its elements can be addressed by name
        all = [template.format(*arg, **ax.dict) for ax in self.axes]
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
        return "\n        ".join(
            [
                f"P{ax.index+1184}=(P{ax.index+1184}-M{ax.axis}62)"
                f"/(I{ax.axis}08*32)+{ax.jdist}-(i{ax.axis}26/16)"
                for ax in self.axes
            ]
        )

    def negate_home_flags(self):
        return " ".join([f"i7{ax.nx}2=P{ax.index+1152}" for ax in self.axes])

    def restore_home_flags(self):
        return " ".join([f"i7{ax.nx}2=P{ax.index+1136}" for ax in self.axes])

    def home(self) -> str:
        return self._all_axes("#{axis}hm", " ")


class Plc:
    def __init__(self, plc_num: int) -> None:
        self.plc_num = plc_num
        self.groups: List[Group] = []
        self.axes: List[Motor] = []

    def add_group(self, group: Group):
        self.groups.append(group)
        self.axes += group.axes

    @property
    def count(self) -> int:
        return len(self.groups)

    def save_hi_limits(self):
        return " ".join([f"P{ax.index+1104}=i{ax.axis}13" for ax in self.axes])

    def restore_hi_limits(self):
        return " ".join([f"i{ax.axis}13=P{ax.index+1104}" for ax in self.axes])

    def save_lo_limits(self):
        return " ".join([f"P{ax.index+1120}=i{ax.axis}14" for ax in self.axes])

    def restore_lo_limits(self):
        return " ".join([f"i{ax.axis}14=P{ax.index+1120}" for ax in self.axes])

    def save_homed(self):
        return " ".join([f"P{ax.index+1136}=i7{ax.nx}2" for ax in self.axes])

    def save_not_homed(self):
        return " ".join([f"P{ax.index+1152}=P{ax.index+1136}^$C" for ax in self.axes])

    def restore_homed(self):
        return " ".join([f"i7{ax.nx}2=P{ax.index+1136}" for ax in self.axes])

    def save_limit_flags(self):
        return " ".join([f"P{ax.index+1168}=i{ax.axis}24" for ax in self.axes])

    def restore_limit_flags(self):
        return " ".join([f"i{ax.axis}24=P{ax.index+1168}" for ax in self.axes])

    def save_position(self):
        return " ".join([f"P{ax.index+1184}=M{ax.axis}62" for ax in self.axes])

    def clear_limits(self):
        r = " ".join([f"i{ax.axis}13=0" for ax in self.axes])
        r += "\n"
        r += " ".join([f"i{ax.axis}14=0" for ax in self.axes])
        return r

    def stop_motors(self):
        return "\n".join(
            [f'if (m{ax.axis}42=0)\n    cmd "#{ax.axis}J/"\nendif' for ax in self.axes]
        )


# TODO all this below will magically happen in the 'with Group' statements
s = SnippetGenerator()
p = Plc(11)

m1 = Motor(axis=1, jdist=0)
m2 = Motor(axis=2, jdist=0)
m4 = Motor(axis=4, jdist=0)
m5 = Motor(axis=5, jdist=0)
g1 = Group([m1, m2], 2)
g1.snippets = [
    Snippet.pre_home,
    Snippet.debug,
    Snippet.fast_search,
    Snippet.store_pos,
    Snippet.debug,
    Snippet.fast_retrace,
    Snippet.debug,
    Snippet.home,
]
g2 = Group([m4, m5], 3)
g2.snippets = [
    Snippet.pre_home,
    Snippet.debug,
    Snippet.fast_search,
    Snippet.store_pos,
    Snippet.debug,
    Snippet.fast_retrace,
    Snippet.debug,
    Snippet.home,
]

p.add_group(g1)
p.add_group(g2)

print(s.render("plc.pmc.jinja", plc=p))
