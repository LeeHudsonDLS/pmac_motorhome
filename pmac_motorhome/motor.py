from typing import Dict

from pmac_motorhome.constants import PostHomeMove


class Motor:
    """
    Declares a motor for use in homing routines in the enclosing Group, Plc

    Should always be instantiated using `pmac_motorhome.commands.motor`
    """

    instances: Dict[int, "Motor"] = {}

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

    def __init__(
        self,
        axis: int,
        jdist: int,
        plc_num: int,
        post_home: PostHomeMove = PostHomeMove.none,
        index: int = -1,
    ) -> None:
        """
        Args:
            axis (int): Axis number of the motor
            jdist (int): Distance in counts to jog after finding the home mark
                this should be enough distance to move clear of the home mark
            plc_num (int): the plc number of the enclosing Plc
            post_home (PostHomeMove): the action to perform on this motor when
                hohing is complete
            index (int): for internal use in conversion of old scripts sets
                the index of this motor to a different value than the order of
                declaration.
        """
        self.axis = axis
        self.jdist = jdist
        if index == -1:
            self.index = len(self.instances)
        else:
            self.index = index

        self.instances[axis] = self
        self.post_home = 0

        # dict is for terse string formatting code in _all_axes() functions
        self.dict = {
            "axis": axis,
            "index": self.index,
            "jdist": jdist,
            "homed_flag": f"7{self.nx}2",
            "pb_homed_flag": f"PowerBrick[{self.gate}].Chan[{self.chan}].CaptCtrl",
            "inverse_flag": f"7{self.nx}3",
            "macro_station": self.macro_station,
        }
        for name, start in self.PVARS.items():
            self.dict[name] = plc_num * 100 + start + self.index

    @classmethod
    def get_motor(
        cls,
        axis: int,
        jdist: int,
        plc_num: int,
        post_home: PostHomeMove = PostHomeMove.none,
        index: int = -1,
    ) -> "Motor":
        """
        A factory function to return a Motor object but ensure that there
        is only ever one instance of each axis number. This is required since
        PLC code allocates p variables on a per axis basis.
        """
        motor = cls.instances.get(axis)
        if motor is None:
            motor = Motor(axis, jdist, plc_num, post_home, index)

        return motor

    # TODO IMPORTANT - this is used in finding the Home capture flags etc. and is
    # specific to Geobrick - For a full implementation see Motor class in
    #  ... pmacutil/pmacUtilApp/src/motorhome.py
    # HINT: watch out for python 2 vs python 3 handling of integer arithmetic
    @property
    def nx(self) -> str:
        nx = int(int((self.axis - 1) / 4) * 10 + int((self.axis - 1) % 4 + 1))
        return "{:02}".format(nx)

    @property
    def gate(self) -> str:
        return str(int((self.axis - 1) / 4))

    @property
    def chan(self) -> str:
        return str(int((self.axis - 1) % 4))

    @property
    def homed(self):
        return self.dict["homed"]

    @property
    def not_homed(self):
        return self.dict["not_homed"]

    @property
    def macro_station(self) -> str:
        msr = int(4 * int(int(self.axis - 1) / 2) + int(self.axis - 1) % 2)
        return "{}".format(msr)
