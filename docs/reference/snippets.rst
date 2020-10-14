.. _SNIPPETS:

Group Snippet Functions
===============================

All of these functions will insert a small snippet of PLC code into the
generated PLC. Each snippet performs a specific action on all of the axes
in a group simultaneously.

They should be called in the context of a Group object. For example this code
will create a homing PLC 12 for a group of axes which does nothing except
drive all of them to their hard limit in the opposite direction to the homing
direction::

    with plc(plc_num=12, controller=ControllerType.brick, filepath=tmp_file):
        motor(axis=1)
        motor(axis=2)
        with group(group_num=2, axes=[1, 2]):
            drive_to_limit(homing_direction=False, with_limits=False)


.. automodule:: dls_motorhome.commands
    :members:

