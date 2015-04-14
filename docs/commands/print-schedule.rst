print-schedule
==============

Synopsis
--------

``srcomp print-schedule [-h] -o <output> [-s <shepherds>] [-p <period> [...]] <compstate>``

Description
-----------

Print a schedule for shepherds.

The shepherds file should contain a key called ``shepherds`` which is a list of
objects containing a ``teams`` and ``colour`` field, with an optional ``name``
field.
