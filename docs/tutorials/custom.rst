
==========================
Custom Homing PLC
==========================

A custom homing PLC can be created by calling snippets defined in
:py:meth:`~pmac_motorhome.snippets` in the order required in the context
of a PLC.

An example is the already defined
:py:meth:`~pmac_motorhome.sequences.home_slits_hsw` function.

It takes four motors for its arguments, and drives them all to their limit
away from the homing direction of the motor.
Separately, the pair of positive axes are homed using the home switch/mark
and the then moved out of the way; followed by the pair of negative axes.

If the home_slits_hsw was not defined already, it could be defined in the
generate_homing_plcs.py in the following way:

.. include:: example_custom_slits.py
    :literal:
