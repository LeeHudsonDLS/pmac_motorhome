from typing import Callable, List, Optional, cast

from dls_motorhome.constants import PostHomeMove

from .motor import Motor
from .template import Template


class Group:
    # this class variable holds the instance in the current context
    the_group: Optional["Group"] = None

    def __init__(
        self,
        group_num: int,
        axes: List[Motor],
        post_home: PostHomeMove,
        plc_num: int,
        comment: str = None,
    ) -> None:
        self.axes = axes
        self.all_axes = axes
        self.post_home = post_home
        self.comment = comment
        self.plc_num = plc_num
        self.group_num = group_num
        self.templates: List[Template] = []

    def __enter__(self):
        assert not Group.the_group, "cannot creat a new Group within a Group context"
        Group.the_group = self
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        Group.the_group = None

    @property
    def count(self) -> int:
        return len(self.templates)

    @classmethod
    # add a comment in the style of the original motorhome module but NOTE that
    # you can use any descriptive text for htype and post
    def add_comment(cls, htype: str, post: str = "None") -> None:
        # funky casting required for type hints since we init the_group to None
        group = cast("Group", cls.the_group)
        group.comment = "\n".join(
            [
                f";  Axis {ax.axis}: htype = {htype}, "
                f"jdist = {ax.jdist}, post = {post}"
                for ax in group.axes
            ]
        )

    @classmethod
    def add_snippet(cls, template_name: str, **args):
        group = cast("Group", cls.the_group)
        group.templates.append(
            Template(jinja_file=template_name, args=args, function=None)
        )

    @classmethod
    def add_action(cls, func: Optional[Callable], **args):
        group = cast("Group", cls.the_group)
        group.templates.append(Template(jinja_file=None, function=func, args=args))

    def set_axis_filter(self, axes: List[int]) -> str:
        if axes == []:
            # reset the axis filter
            self.axes = self.all_axes
        else:
            self.axes = [motor for motor in self.all_axes if motor.axis in axes]
            assert len(self.axes) == len(axes), "set_axis_filter: invalid axis number"
            # callback functions must return a string since we call them with
            # {{- group.callback(template.function, template.args) -}} from jinja
        return ""

    def command(self, cmd: str):
        return cmd

    def _all_axes(self, format: str, separator: str, *arg) -> str:
        # to the string format: pass any extra arguments first, then the dictionary
        # of the axis object so its elements can be addressed by name
        all = [format.format(*arg, **ax.dict) for ax in self.axes]
        return separator.join(all)

    ############################################################################
    # the following functions are callled from Jinja templates to generate
    # snippets of PLC code that act on all motors in a group
    #
    # We call these Group Axis Snippet functions
    ############################################################################

    def callback(self, function, args):
        return function(self, **args)

    def jog_axes(self) -> str:
        return self._all_axes("#{axis}J^*", " ")

    def jog_to_trigger_jdist(self) -> str:
        return self._all_axes("#{axis}J^*^{jdist}", " ")

    def set_large_jog_distance(self, negative: bool = True) -> str:
        sign = "-" if negative else ""
        return self._all_axes(
            "m{axis}72=100000000*({0}i{axis}23/ABS(i{axis}23))", " ", sign
        )

    def jog(self, negative: bool = True) -> str:
        sign = "-" if negative else ""
        return self._all_axes("#{axis}J{0}", " ", sign)

    def in_pos(self) -> str:
        return self._all_axes("m{axis}40", "&")

    def limits(self) -> str:
        return self._all_axes("m{axis}30", "|")

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

    def stored_pos_to_jogdistance(self):
        return self._all_axes("m{axis}72=P{pos}", " ")

    def jog_distance(self):
        return self._all_axes("#{axis}J=*", " ")

    def negate_home_flags(self):
        return self._all_axes("i{homed_flag}=P{not_homed}", " ")

    def restore_home_flags(self):
        return self._all_axes("i{homed_flag}=P{homed}", " ")

    def jog_to_home_jdist(self):
        return self._all_axes("#{axis}J^*^{jdist}", " ")

    def home(self) -> str:
        return self._all_axes("#{axis}hm", " ")

    def restore_limit_flags(self):
        return self._all_axes("i{axis}24=P{lim_flags}", " ")

    def overwrite_inverse_flags(self):
        return self._all_axes("P{not_homed}=i{inverse_flag}", " ")
