import logging
from collections import OrderedDict
from pathlib import Path
from typing import List, Optional

from .constants import ControllerType, PostHomeMove
from .group import Group
from .motor import Motor
from .plcgenerator import PlcGenerator

log = logging.getLogger(__name__)


class Plc:
    """
    This class is used in a PLC definition to declare that a PLC is to
    be generated.

    Should always be instantiated using `pmac_motorhome.commands.plc`
    """

    # this class variable holds the instance in the current context
    the_plc: Optional["Plc"] = None

    def __init__(
        self,
        plc_num: int,
        controller: ControllerType,
        filepath: Path,
        timeout: int,
        post,
    ) -> None:
        """
        Args:
            plc_num (int): The PLC number to use in generated code
            controller (ControllerType):  target controller type for the code
            filepath (pathlib.Path): ouput file to receive the generated code

        Raises:
            ValueError: Invalid output file name
            ValueError: Invalid PLC number supplied
        """
        self.filepath = filepath
        self.plc_num = plc_num
        self.controller: ControllerType = controller
        self.timeout: int = timeout
        self.post = post

        self.groups: List[Group] = []
        self.motors: "OrderedDict[int, Motor]" = OrderedDict()
        self.generator = PlcGenerator()
        if not self.filepath.parent.exists():
            log.error(f"Cant find parent of {self.filepath} from dir {Path.cwd()}")
            raise ValueError(f"bad file path {self.filepath.parent}")
        if (
            self.plc_num < 8  # PLCs 1-8 are reserved
            or self.plc_num > 32  # highest PLC number possible
            or not isinstance(self.plc_num, int)
        ):
            raise ValueError("plc_number should be integer between 9 and 32")

    def __enter__(self):
        """
        Enter context: store the in-scope Plc object
        """
        assert not Plc.the_plc, "cannot create a new Plc within a Plc context"
        Plc.the_plc = self
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        Plc.the_plc = None
        """
         Leaving the context. Use the in scope Plc object to generate the
         PLC output code.
        """
        # need to do this for the case where 2 PLCs are defined in one file
        # (including in the unit tests)
        Motor.instances = {}

        # write out PLC
        plc_text = self.generator.render("plc.pmc.jinja", plc=self)
        with self.filepath.open("w") as stream:
            stream.write(plc_text)

    @classmethod
    def instance(cls) -> "Plc":
        """
        Get the current in-scope PLC.
        """
        assert cls.the_plc, "There is no group context currently defined"
        return cls.the_plc

    @classmethod
    def add_group(
        cls,
        group_num: int,
        post_home: PostHomeMove,
        post_distance: int,
        comment: str = None,
        pre: str = None,
        post: str = None,
    ) -> Group:
        """
        Add a new group of axes to the current Plc

        Args:
            group_num (int): A Unique group number (1 is reserved for 'All Groups')
            post_home (PostHomeMove): A post home action to perform on success
            post_distance (int): A distance for those post home actions which require it

        Returns:
            Group: The newly created Group
        """
        plc = Plc.instance()
        group = Group(
            group_num,
            plc.plc_num,
            plc.controller,
            post_home,
            post_distance,
            comment,
            pre,
            post,
        )
        print("  plc.py", group.post_home, plc.post)
        if group.post_home is None:
            group.post_home = plc.post
        # group.post_home = PostHomeMove.initial_position
        plc.groups.append(group)
        return group

    @classmethod
    def add_motor(cls, axis: int, motor: Motor):
        """
        Add a motor to the PLC. The Plc object collects all the motors in all
        of its groups for use in the Plc callback functions.

        Args:
            axis (int): axis number
            motor (Motor): motor details
        """
        plc = Plc.instance()
        if axis not in plc.motors:
            plc.motors[axis] = motor

    def _all_axes(self, format: str, separator: str, *arg) -> str:
        """
        A helper function to generate code for all axes in a group when one
        of the callback functions below is called from a Jinja template.

        Args:
            format (str): A format string to apply to each motor in the Plc
            separator (str): The separator between each formatted string

        Returns:
            str: [description]
        """
        # to the string format: pass any extra arguments first, then the dictionary
        # of the axis object so its elements can be addressed by name

        # PLC P variables etc must be sorted to match original motorhome.py
        motors = sorted(self.motors.values(), key=lambda x: x.index)
        all = [format.format(*arg, **ax.dict) for ax in motors]
        return separator.join(all)

    ############################################################################
    # the following functions are callled from Jinja templates to generate
    # snippets of PLC code that act on all motors in a plc
    #
    # We call these Plc Axis Snippet functions
    ############################################################################

    def save_hi_limits(self):
        """
        Generate a command string for saving all axes high limits
        """
        return self._all_axes("P{hi_lim}=i{axis}13", " ")

    def restore_hi_limits(self):
        """
        Generate a command string for restoring all axes high limits
        """
        return self._all_axes("i{axis}13=P{hi_lim}", " ")

    def save_lo_limits(self):
        """
        Generate a command string for saving all axes low limits
        """
        return self._all_axes("P{lo_lim}=i{axis}14", " ")

    def restore_lo_limits(self):
        """
        Generate a command string for restoring all axes low limits
        """
        return self._all_axes("i{axis}14=P{lo_lim}", " ")

    def save_homed(self):
        """
        Generate a command string for saving all axes homed state
        """
        if self.controller is ControllerType.pmac:
            return self._all_axes("MSR{macro_station},i912,P{homed}", " ")
        else:
            return self._all_axes("P{homed}=i{homed_flag}", " ")

    def save_not_homed(self):
        """
        Generate a command string for saving the inverse of all axes homed state
        """
        return self._all_axes("P{not_homed}=P{homed}^$C", " ")

    def restore_homed(self):
        """
        Generate a command string for restoring all axes homed state
        """
        if self.controller is ControllerType.pmac:
            return self._all_axes("MSW{macro_station},i912,P{homed}", " ")
        else:
            return self._all_axes("i{homed_flag}=P{homed}", " ")

    def save_limit_flags(self):
        """
        Generate a command string for saving all axes limit flags
        """
        return self._all_axes("P{lim_flags}=i{axis}24", " ")

    def restore_limit_flags(self):
        """
        Generate a command string for restoring all axes limit flags
        """
        return self._all_axes("i{axis}24=P{lim_flags}", " ")

    def save_position(self):
        """
        Generate a command string for saving all axes positions
        """
        return self._all_axes("P{pos}=M{axis}62", " ")

    def clear_limits(self):
        """
        Generate a command string for clearing all axes limits
        """
        r = self._all_axes("i{axis}13=0", " ")
        r += "\n"
        r += self._all_axes("i{axis}14=0", " ")
        return r

    def stop_motors(self):
        """
        Generate a command string for stopping all axes
        """
        return self._all_axes('if (m{axis}42=0)\n    cmd "#{axis}J/"\nendif', "\n")

    def are_homed_flags_zero(self):
        """
        Generate a command string for checking if all axes homed=0
        """
        return self._all_axes("P{homed}=0", " or ")
