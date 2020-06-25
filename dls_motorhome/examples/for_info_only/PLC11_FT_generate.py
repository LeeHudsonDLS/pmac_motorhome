#!/bin/env dls-python

#this is the original motorhome.py approach to generating PLC11_FT_HM.pmc
# it is from BL07I-MO-STEP-04

# Import the motorhome PLC generation library
from motorhome import *

# find the plc number, component name and filename
num, name, filename = parse_args()

# set some defaults
geoplc = PLC(num, ctype=GEOBRICK)

# configure the axes according to name
if name == "FT":
    # Home on limit switch release
    for axis in [1,2]:
        geoplc.add_motor(axis, group=2, htype=RLIM) # group 2 is Y1 and Y2
    for axis in [4,5]:
        geoplc.add_motor(axis, group=3, htype=RLIM) # group 3 is Y3 and Y4
else:
    sys.stderr.write("***Error: Can't make homing PLC %d for %s\n" % (num, name))
    sys.exit(1)

# write out the plc
geoplc.write(filename)
