from typing import Any, Callable, Dict, List, Optional

from dls_motorhome.constants import ControllerType, PostHomeMove

from .motor import Motor
from .template import Template


class Group:
    """
    Defines a group of axes to be homed as a unit

    Should always be instantiated using `dls_motorhome.commands.group`
    """

    # this class variable holds the instance in the current context
    the_group: Optional["Group"] = None

    def __init__(
        self,
        group_num: int,
        plc_num: int,
        controller: ControllerType,
        post_home: PostHomeMove,
        post_distance: int,
        comment: str = None,
    ) -> None:
        """
        Args:
            group_num (int): A unique number to represent this group within its
                Plc. group 1 is reservered for 'all groups'
            axes (List[Motor]): A list of axis numbers that this group will control
            plc_num (int): The plc number of the enclosing Plc
            controller (ControllerType): Enum representing the type of motor controller
            post_home (PostHomeMove): An action to perform on the group after homing
                completes successfully
            post_distance (int): a distance to use in post_home if required
            comment (str): [description]. A comment to place in the output Plc code
                at the beginning of this group's definition
        """
        self.motors: List[Motor] = []
        self.all_motors: List[Motor] = []
        self.post_home = post_home
        self.post_distance = post_distance
        self.comment = comment
        self.plc_num = plc_num
        self.group_num = group_num
        self.templates: List[Template] = []
        self.htype: str = "unknown"
        self.controller = controller

    def __enter__(self):
        """
        Entering a context. Store the Group object for use in the scope of
        this context.
        """
        assert not Group.the_group, "cannot create a new Group within a Group context"
        Group.the_group = self
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """
        Exiting the context. Clear the Group object.
        """
        Group.the_group = None

    @classmethod
    def add_motor(cls, axis: int, jdist: int) -> Motor:
        """
        Add a new motor to the current group

        Args:
            axis (int): Axis number
            jdist (int): distance to jog to move off of home mark

        Returns:
            Motor: The newly created Motor
        """
        group = Group.instance()
        assert (
            axis not in group.motors
        ), f"motor {axis} already defined in group {group.plc_num}"
        motor = Motor.get_motor(axis, jdist, group.plc_num)
        group.motors.append(motor)
        group.all_motors.append(motor)
        return motor

    @classmethod
    def instance(cls) -> "Group":
        """
        Get the current in-scope Group
        """
        assert cls.the_group, "There is no group context currently defined"
        return cls.the_group

    @classmethod
    def add_comment(cls, htype: str, post: str = "None") -> None:
        """
        Add a group comment to the top of the Plc code in the style of the original
        motorhome.py module but note that you can use any descriptive text
        for htype and post

        Args:
            htype (str): Homing sequence type e.g. RLIM HSW etc.
            post (str): post home move action
        """
        group = Group.instance()
        group.comment = "\n".join(
            [
                f";  Axis {ax.axis}: htype = {htype}, "
                f"jdist = {ax.jdist}, post = {post}"
                for ax in group.motors
            ]
        )

    @classmethod
    def add_snippet(cls, template_name: str, **args):
        """
        Add a jinja snippet to the list of snippets to be rendered

        Args:
            template_name (str): prefix of the jinja template's filename
                '.pmc.jinja' is added to this name and the template file
                should be in dls_motorhome/snippets
        """
        group = Group.instance()
        group.templates.append(
            Template(jinja_file=template_name, args=args, function=None)
        )

    @classmethod
    def add_action(cls, func: Callable, **args):
        """
        Add a callback to the list of 'snippets' to be rendered The callback
        function should return an string to be inserted into the rendered
        template

        Args:
            func (Callable): the function to call
            args (dict): arguments to pass to func
        """
        group = Group.instance()
        group.templates.append(Template(jinja_file=None, function=func, args=args))

    def set_axis_filter(self, axes: List[int]) -> str:
        """
        A callback function to set group actions to only act on a subset of the
        group's axes.

        Will be called back during the rendering of plc.pmc.jinja, and is inserted
        using Group.add_action()

        Args:
            axes (List[int]): List of axis numbers to be controlled in this context

        Returns:
            str: Blank string. Required because this function is used as a callback
                from a jinja template and thus must return some string to insert into
                the template
        """
        if axes == []:
            # reset the axis filter
            self.motors = self.all_motors
        else:
            self.motors = [motor for motor in self.all_motors if motor.axis in axes]
            assert len(self.motors) == len(axes), "set_axis_filter: invalid axis number"
            # callback functions must return a string since we call them with
            # {{- group.callback(template.function, template.args) -}} from jinja
        return ""

    def command(self, cmd: str) -> str:
        """
        A callback function to insert arbitrarty text into the ouput Plc code.

        Will be called back during the rendering of plc.pmc.jinja, and is inserted
        using Group.add_action()

        Args:
            cmd (str): Any string

        Returns:
            str: the passed string (for jinja rendering)
        """
        return cmd

    def _all_axes(self, format: str, separator: str, *arg) -> str:
        """
        A helper function that generates a command line by applying each of Motor
        in the group as a parameter to the format string and the concatenating all of
        the results with a separator.

        Args:
            format (str): The format string to apply, passing each Motor in the group
                as its arguments
            separator (str): Separator that goes between the formatted string for each
                axis
            arg ([Any]): additional arguments to pass to the format string

        Returns:
            str: The resulting command string
        """

        # to the string format: pass any extra arguments first, then the dictionary
        # of the axis object so its elements can be addressed by name
        all = [format.format(*arg, **ax.dict) for ax in self.motors]
        return separator.join(all)

    def callback(self, function: Callable, args: Dict[str, Any]) -> str:
        """
        Callback from plc.pmc.jinja to a function that was added into the group
        using :func:`~Group.add_action`

        Args:
            function (Callable): the function to call
            args (Dict[str, Any]): arguments to pass to function

        Returns:
            str: The string to insert into the PLC output file
        """
        return function(self, **args)

    def jog_axes(self) -> str:
        """
        Generate a command string for all group axes: jog a set distance
        """
        return self._all_axes("#{axis}J^*", " ")

    def set_large_jog_distance(self, homing_direction: bool = True) -> str:
        """
        Generate a command string for all group axes: set large jog distance
        """
        sign = "" if homing_direction else "-"
        return self._all_axes(
            "m{axis}72=100000000*({0}i{axis}23/ABS(i{axis}23))", " ", sign
        )

    def jog(self, homing_direction: bool = True) -> str:
        """
        Generate a command string for all group axes: jog indefinitely
        """
        sign = "+" if homing_direction else "-"
        return self._all_axes("#{axis}J{0}", " ", sign)

    def in_pos(self, operator="&") -> str:
        """
        Generate a command string for all group axes: check in postiion
        """
        return self._all_axes("m{axis}40", operator)

    def limits(self) -> str:
        """
        Generate a command string for all group axes: check limits
        """
        return self._all_axes("m{axis}30", "|")

    def following_err(self) -> str:
        """
        Generate a command string for all group axes: check following error
        """
        return self._all_axes("m{axis}42", "|")

    def homed(self) -> str:
        """
        Generate a command string for all group axes: check homed
        """
        return self._all_axes("m{axis}45", "&")

    def clear_home(self) -> str:
        """
        Generate a command string for all group axes: clear home flag
        """
        return self._all_axes("m{axis}45=0", " ")

    def store_position_diff(self):
        """
        Generate a command string for all group axes: save position
        """
        return self._all_axes(
            "P{pos}=(P{pos}-M{axis}62)/(I{axis}08*32)+{jdist}-(i{axis}26/16)",
            separator="\n        ",
        )

    def stored_pos_to_jogdistance(self):
        """
        Generate a command string for all group axes: calculate jog distance
        to return to pre homed position
        """
        return self._all_axes("m{axis}72=P{pos}", " ")

    def stored_limit_to_jogdistance(self, homing_direction=True):
        """
        Generate a command string for all group axes: save distance to limit
        """
        if homing_direction:
            return self._all_axes("m{axis}72=P{hi_lim}", " ")
        else:
            return self._all_axes("m{axis}72=P{lo_lim}", " ")

    def jog_distance(self, distance="*"):
        """
        Generate a command string for all group axes: jog to prejog position.
        Useful if a program has been aborted in the middle of a move, because it
        will move the motor to the programmed move end position
        """
        return self._all_axes("#{axis}J=%s" % (distance), " ")

    def negate_home_flags(self):
        """
        Generate a command string for all group axes: invert homing flags
        """
        if self.controller == ControllerType.pmac:
            return self._all_axes("MSW{macro_station},i912,P{not_homed}", " ")
        else:
            return self._all_axes("i{homed_flag}=P{not_homed}", " ")

    def restore_home_flags(self):
        """
        Generate a command string for all group axes: restore original homing flags
        """
        if self.controller == ControllerType.pmac:
            return self._all_axes("MSW{macro_station},i912,P{homed}", " ")
        else:
            return self._all_axes("i{homed_flag}=P{homed}", " ")

    def jog_to_home_jdist(self):
        """
        Generate a command string for all group axes: jog to home and then move jdist
        """
        return self._all_axes("#{axis}J^*^{jdist}", " ")

    def home(self) -> str:
        """
        Generate a command string for all group axes: home command
        """
        return self._all_axes("#{axis}hm", " ")

    def set_home(self) -> str:
        """
        Generate a command string for all group axes: set current position as home
        """
        return self._all_axes("#{axis}hmz", " ")

    def restore_limit_flags(self):
        """
        Generate a command string for all group axes: restore original limit flags
        """
        return self._all_axes("i{axis}24=P{lim_flags}", " ")

    def overwrite_inverse_flags(self):
        """
        Generate a command string for all group axes: reuse the not homed store to
        store ?? (TODO what is this doing ?)
        """
        return self._all_axes("P{not_homed}=i{inverse_flag}", " ")
