#!/bin/env dls-python

# Import the motorhome PLC generation library
from motorhome import *

# find the plc number, component name and filename
num, name, filename = parse_args()

# set some defaults
plc = PLC(num, ctype=BRICK)

### Step 10 ###
# configure the axes according to name
if name == "UPSTREAM":
    plc.add_motor(2, group=2, htype=RLIM)
    plc.add_motor(3, group=3, htype=RLIM)
    plc.add_motor(4, group=4, htype=RLIM)
    plc.add_motor(5, group=5, htype=RLIM)
elif name == "PXY2":
    plc.add_motor(6, group=2, htype=RLIM)
    plc.add_motor(7, group=3, htype=RLIM)
### Step 11 ###
elif name == "DOWNSTREAM":
    plc.add_motor(1, group=2, htype=RLIM)
    plc.add_motor(2, group=3, htype=RLIM)
    plc.add_motor(3, group=4, htype=RLIM)
    plc.add_motor(4, group=5, htype=RLIM)
    plc.add_motor(5, group=6, htype=RLIM)
elif name == "PXY1":
    plc.add_motor(6, group=2, htype=RLIM)
    plc.add_motor(7, group=3, htype=RLIM)
### Step 14 ###
elif name == "FSWT":
    plc.add_motor(1, group=2, htype=HSW)
    plc.add_motor(2, group=3, htype=HSW)

### Step 12 ###
# Microscope stages
# All axes home on index mark
elif name == "MSCP":
    plc.add_motor(1, group=2, htype=HSW, jdist=-1000, post="i")  # X
    plc.add_motor(2, group=3, htype=HSW, jdist=-10000, post="i")  # Y
    plc.add_motor(3, group=4, htype=HSW, jdist=-1000, post="i")  # Z

# Pi microfocus sample stages
# All axes home on a step index mark, so we must drive to lo lim before homing -> use RLIM
elif name == "MF":
    plc.add_motor(6, group=2, htype=RLIM, post="i")  # X
    plc.add_motor(8, group=3, htype=RLIM, post="i")  # Y
    plc.add_motor(7, group=4, htype=RLIM, post="i")  # Z

elif name == "ROT":  # Coarse rotation stage
    plc.add_motor(4, group=2, htype=HSW, jdist=-1000, post="i")

# Precision rotation stage (T8)
# Homes on index mark, in the negative direction
elif name == "PROT":
    plc.add_motor(5, group=2, htype=HSW, jdist=100)

else:
    sys.stderr.write("***Error: Can't make homing PLC %d for %s\n" % (num, name))
    sys.exit(1)

# write out the plc
plc.write(filename)
