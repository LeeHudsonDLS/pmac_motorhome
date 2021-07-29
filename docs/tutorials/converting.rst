===============================
Converting to pmac_motorhome.py
===============================

TODO

To convert the plc generating python script (typically named
generate_homing_plcs.py) from using the motorhome.py module to using the
pmac_motorhome.py module, a conversion tool is available.

The command homing_convert can be used to convert either a single v1.0 homing
PLC generator script, or scan a DLS motion area for homing PLC generator scripts
to convert. Using the 'motion' command is encouraged, especially for the case
of generator scripts for individual motion controllers.

The process will create two copies of the motion area given as one of the ARGS,
in the /tmp directory of your machine; an old_motion and a new_motion.
The old_motion directory will contain generated PLCs from the original generator
script, and the new_motion directory from the converted generator script.

A comparison between the generated PLCs is performed, and any discrepancies
are summarised and a meld command is provided to inspect the differences.

At this point, no changes are made to the original motion area.
To complete the conversion step, use the provided command to replace the old
generator script with the new one.