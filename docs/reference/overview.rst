.. _API_Overview:

Overview
========

To create a homing PLC the user must write a definition file which is a simple
python script.

For example the following code will output a PLC 12 that defines a group of
axes including axis 1 and axis 2. It will provide a standard home switch
(or home mark) homing sequence. The PLC will be written to
/tmp/PLC12_SLITS1_HM.pmc

.. _PlcDefinition:

Homing PLC definition file
--------------------------

.. include:: ../tutorials/example.py
  :literal:


All the code that goes into the definition file will use global functions
and contexts (`with`). The functions can be broken into 3 categories
which are documented in the following sections.

- :doc:`commands`: functions to declare PLCs, Motors and Groups
- :doc:`sequences`: a set of commonly used predefined homing sequences
- :doc:`snippets`: a set of blocks of PLC code combined by predfined above
