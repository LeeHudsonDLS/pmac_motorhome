from .globals import HOME
from .motor import Motor
from .pmac import PMAC


class PLC:
    def __init__(
        self,
        plc,
        timeout=600000,
        htype=HOME,
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
        self.groups = {}

    def configure_group(self, group, checks=None, pre=None, post=None):
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
        if group in self.groups:
            self.groups[group].append(motor)
        else:
            self.groups[group] = [motor]

    def write(self, f):
        for i, group in self.groups.items():
            print(f"    group {i}")
            for motor in group:
                print(f"        axis {motor.axis}")

    def writeFile(self, f):
        pass
