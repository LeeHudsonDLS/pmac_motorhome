
==========================
Create a Simple Homing PLC
==========================
The simplest homing PLC will use one of the predifined homing sequences that
are built in to pmac_motorhome.

A PLC definition is a python file that defines the following:

- One or more `Plc` objects which have a PLC number, motor `ControllerType` and a
  filename in which the output of the PLC code generation is saved.
- Within each PLC, one or more `Group` objects that define groups of motors to be
  homed as a unit.
- Within each group are one or more `Motor` objects that determine axis numbers
  of the group's motors.
- Also within each group is a sequence of commands that generate a sequence of
  PLC commands in the output file.

The basic example below defines a single PLC containing a single group and generates
PLC code that will home the

.. include:: example.py
    :literal: