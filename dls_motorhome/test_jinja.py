from enum import Enum
from pathlib import Path
from typing import List

from jinja2 import Environment, FileSystemLoader

this_path = Path(__file__).parent
jinja_path = this_path.parent / "snippets"

templateLoader = FileSystemLoader(searchpath=jinja_path)
environment = Environment(loader=templateLoader)


# TODO IMPORTANT - this is used in finding the Home capture flags etc. and is
# specific to Geobrick - you will want to use a Motor abstraction instead
# of just a list of motor numbers. For inspiration see Motor class in
#  ... pmacutil/pmacUtilApp/src/motorhome.py
# HINT: watch out for python 2 vs python 3 handling of integer arithmetic
def axis_nx(ax: int) -> str:
    nx = int(int((ax - 1) / 4) * 10 + int((ax - 1) % 4 + 1))
    return "{:02}".format(nx)


class SnippetGenerator:
    def __init__(self) -> None:
        this_path = Path(__file__).parent
        jinja_path = this_path.parent / "snippets"
        self.templateLoader = FileSystemLoader(searchpath=jinja_path)
        self.environment = Environment(
            loader=self.templateLoader,
            trim_blocks=True,
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


class Group:
    # TODO this probably needs to be merged into your Group class that implements
    # the python contexts
    def __init__(self, axes: List[int], group_num: int = 9) -> None:
        self.axes = axes
        self.comments: str = f"; TODO commments placeholder for group {group_num}"
        self.group_num = group_num
        self.snippets: List[Snippet] = []

    @property
    def count(self) -> int:
        return len(self.snippets)

    def _all_axes(self, template: str, separator: str) -> str:
        all = [template.format(axis) for axis in self.axes]
        return separator.join(all)

    def jog_axes(self) -> str:
        return self._all_axes("#{0}J^*", " ")

    def set_large_jog_distance(self) -> str:
        return self._all_axes("m{0}72=100000000*(-i{0}23/ABS(i{0}23))", " ")

    def in_pos(self) -> str:
        return self._all_axes("m{0}40", "&")

    def following_err(self) -> str:
        return self._all_axes("m{0}42", "|")

    def homed(self) -> str:
        return self._all_axes("m{0}45", "&")

    def clear_home(self) -> str:
        return self._all_axes("m{0}45=0", " ")


class Plc:
    def __init__(self, plc_num: int) -> None:
        self.plc_num = plc_num
        self.groups: List[Group] = []
        self.axes: List[int] = []

    def add_group(self, group: Group):
        self.groups.append(group)
        self.axes += group.axes

    @property
    def count(self) -> int:
        return len(self.groups)

    def save_hi_limits(self):
        return " ".join([f"P{n+1104}=i{ax}13" for n, ax in enumerate(self.axes)])

    def restore_hi_limits(self):
        return " ".join([f"i{ax}13=P{n+1104}" for n, ax in enumerate(self.axes)])

    def save_lo_limits(self):
        return " ".join([f"P{n+1120}=i{ax}14" for n, ax in enumerate(self.axes)])

    def restore_lo_limits(self):
        return " ".join([f"i{ax}14=P{n+1120}" for n, ax in enumerate(self.axes)])

    def save_homed(self):
        return " ".join(
            [f"P{n+1136}=i7{axis_nx(ax)}2" for n, ax in enumerate(self.axes)]
        )

    def restore_homed(self):
        return " ".join(
            [f"i7{axis_nx(ax)}2=P{n+1136}" for n, ax in enumerate(self.axes)]
        )

    def save_not_homed(self):
        return " ".join([f"P{n+1152}=P{n+1136}^$C" for n, ax in enumerate(self.axes)])

    def save_limit_flags(self):
        return " ".join([f"P{n+1168}=i{ax}24" for n, ax in enumerate(self.axes)])

    def restore_limit_flags(self):
        return " ".join([f"i{ax}24=P{n+1168}" for n, ax in enumerate(self.axes)])

    def save_position(self):
        return " ".join([f"P{n+1184}=M{ax}62" for n, ax in enumerate(self.axes)])

    def clear_limits(self):
        r = " ".join([f"i{ax}13=0" for ax in self.axes])
        r += "\n"
        r += " ".join([f"i{ax}14=0" for ax in self.axes])
        return r

    def stop_motors(self):
        return "\n".join(
            [f'if (m{ax}42=0)\n    cmd "#{ax}J/"\nendif' for ax in self.axes]
        )


# TODO all this will magically happen in the 'with Group' statements
s = SnippetGenerator()
p = Plc(11)

g1 = Group([1, 2], 2)
g1.snippets = [Snippet.pre_home, Snippet.debug]
g2 = Group([4, 5], 3)
g2.snippets = [Snippet.pre_home, Snippet.debug]

p.add_group(g1)
p.add_group(g2)

print(s.render("plc.pmc.jinja", plc=p))
