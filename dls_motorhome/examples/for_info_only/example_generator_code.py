# this is the example code from Tom's original ideas discussions

class Group():
    def _init_(self, *axes):
        self.axes = axes
    def _enter_(self):
        return self
    def _exit_(self, *args):
        return
    def do_stuff(self):
        print(f"Doing stuff with axes {self.axes}")
    def limited_to(self, *axes):
        for a in axes: assert a in self.axes
        return Group(*axes)

with Group(1, 2, 3) as g:
    g.do_stuff()
    with g.limited_to(1, 3) as g:
        g.do_stuff()
    g.do_stuff()

def home_on_release_of_limit(group):
    group.drive_to_limit()
    group.drive_off_limit()
    group.store_homed_position()
    group.drive_to_limit()
    group.home()
    group.go_back_to_start()

############################
# PLC14_S5_HM.py

from motorhome import PLC, home_on_release_of_limit

with plc.group(1, 3) as group: # and store stuff like current position, flags, etc
    home_on_release_of_limit(group)

with plc.group(2, 4) as group:
    group.drive_to_limit()
    group.command("i243=4545 i443=453435")
    group.drive_off_limit()
    group.store_homed_position()
    group.drive_to_limit()
    group.home()
    group.go_back_to_start()

def home_slits(posx, posy, negx, negy):
    with group(posx, posy, negx, negy):
        drive_to_limit()
        with only_axes(posx, posy):
            home_pair()
        with only_axes(negx, negy):
            home_pair()
        drive_back_to_start()

def home_pair():
    drive_to_reference()
    store_homed_position()
    retrace_from_reference()
    home()
    drive_to_limit()

with PLC(_file_, ctype=BRICK):
    home_slits(posx=1, posy=2, negx=3, negy=4)

def PLC:
    the_plc = None
    def _enter_(self):
        assert not PLC.the_plc
        PLC.the_plc = self
        return self
    def _exit_(self):
        if deferred_commands:
            process_deferred_comands()
        write_file_out()
        PLC.the_plc = None
    def add_motor(htyp=LIMIT):
        deferred_commands.append((axis, htyp))

def group():
    return Group(PLC.the_plc)

if name == "S1":
    plc = PLC(num, htype=LIMIT, ctype=PMAC, post=post) # all axes home off limit switches
    # group 2 is Y:PLUS, Y:MINUS
    plc.add_motor(1, group=2)
    plc.add_motor(3, group=2)
    # group 3 is X:PLUS, X:MINUS
    plc.add_motor(2, group=3)
    plc.add_motor(4, group=3)

