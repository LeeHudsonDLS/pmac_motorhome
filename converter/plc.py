from typing import Dict, List

from converter.group import Group

from .globals import (
    NO_HOMING_YET,
    PMAC,
    BrickType,
    BrickTypes,
    HomingSequence,
    HomingSequences,
)
from .motor import Motor


class PLC:
    instances: List["PLC"] = []

    def __init__(
        self,
        plc,
        timeout=600000,
        htype=NO_HOMING_YET,
        jdist=0,
        post=None,
        ctype=PMAC,
        allow_debug=True,
    ):
        self.plc = plc
        self.timeout = timeout
        self.htype = htype
        self.jdist = jdist
        self.post = post
        self.ctype = ctype
        self.allow_debug = allow_debug

        self.error = 0
        self.error_msg = ""

        # instantiate some members for translating parameters into the
        # new motorhome nomenclature
        self.sequence: HomingSequence = HomingSequences[htype]
        self.bricktype: BrickType = BrickTypes[ctype]

        # members for recording what is addded to this PLC
        self.groups: Dict[int, Group] = {}
        self.filename = ""

        self.instances.append(self)

    @classmethod
    def clear_instances(cls):
        cls.instances = []

    @classmethod
    def get_instances(cls):
        """
        Returns a list of instances of PLCs created since the last clear_instance().
        Ignores PLCs with no groups. This avoids an issue with redundant instances that
        came up in the first example.

        Yields:
            PLC: an iterator over all populated PLC instances
        """
        for instance in cls.instances:
            if len(instance.groups) > 0:
                yield instance

    def configure_group(self, group, checks=None, pre=None, post=None):
        # TODO this needs adding
        pass

    def add_motor(
        self,
        axis,
        group=1,
        htype=None,
        jdist=None,
        jdist_overrides=None,
        post=None,
        enc_axes=[],
        ms=None,
    ):
        motor = Motor(axis, enc_axes, self.ctype, ms)
        if group not in self.groups:
            new_group = Group(group, checks=[], pre="", post="")
            self.groups[group] = new_group

        if jdist is not None:
            motor.jdist = jdist

        self.groups[group].motors.append(motor)

        if htype is not None:
            self.groups[group].set_htype(htype)
        elif self.groups[group].htype is None and self.htype is not None:
            # I'm assuming that not specifying homing type in add_motor implies
            # getting it from group and if not group then PLC
            self.groups[group].set_htype(htype)

    def write(self, filename):
        self.filename = filename

    def writeFile(self, f):
        pass
