Adding Functionality
====================

Audience
--------

This section is for developers who want to add homing procedures that
require changes to the code. Note that many custom homing sequences may
be achieved by simply recombining the existing snippets and this would
not require code changes to this library.

For an overview of how the following work together see `How_it_Works`

Adding a New Homing Sequence Function
-------------------------------------
TODO - flesh this out

- Add a new function in :py:mod:`dls_motorhome.sequences`
- Make calls to functions in `commands`, `snippets`
  and possibly other :py:mod:`dls_motorhome.sequences`

A nice example is home_slits_hsw (TODO cannot get literalinclude to work!)

.. literalinclude:: `commands.py`
  :pyobject: home_slits_hsw

Adding a New Snippet Template
-----------------------------
TODO - flesh this out

- write the Jina template
- add a snippet command to snippets.py using _snippet_function decorator

TODO - also cant get _snippet function documentation to included here

.. automodule:: dls_motorhome.snippets

    .. automethod:: _snippet_function

Adding a New Callback Function
------------------------------
TODO - flesh this out

- add the function to Plc or Group
- use the all_axes function to generate axis commands
- or output arbitrary text

