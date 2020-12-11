
==========================
Simple Homing PLC
==========================
The simplest homing PLC will use one of the predifined homing sequences that
are built in to pmac_motorhome.

A PLC definition is a python file that defines the following:

- One or more :py:meth:`~pmac_motorhome.commands.plc` commands which define a
  single PLC using PLC number, mototion `ControllerType` and a
  filename in which the output of the PLC code generation is saved.
- Within each PLC, one or more :py:meth:`~pmac_motorhome.commands.group` commands
  that define groups of motors to be
  homed as a unit. These require a group number which must be unique within the
  PLC. Group Number 1 is reserved for 'home all groups'.
- Within each group are one or more :py:meth:`~pmac_motorhome.commands.motor`
  commands that declare the motors in the
  current group. These require an axis number.
- Also within each group is a sequence of commands that will generate a sequence of
  PLC commands in the output file.

:py:meth:`~pmac_motorhome.commands.plc` and :py:meth:`~pmac_motorhome.commands.group` use
python contexts to manage their scope. This simply means that you add
`with` before calling them and then indent the related code.

The basic example below defines a single PLC containing a single group and generates
PLC code that will home axes 1 and 2 simultaneously and use the home switch or encoder
home mark to find their home positions.

.. include:: example.py
    :literal:

To create the PLC file for download to the brick you simply need to execute example.py
in the virtual environment in which pmac_motorhome is installed e.g. ::

    pipenv run docs/tutorials/example.py
    less /tmp/PLC12_SLITS1_HM.pmc