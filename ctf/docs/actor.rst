.. |br| raw:: html

   <br />


Actor Interface
===============

Any living entity in the world (a.k.a. `Actor`) can be controlled via an API that's divided by functionality.  These interfaces are implemented by child components of the actor.

.. autosummary::

    aisbx.actor.interface.motion
    aisbx.actor.interface.navigation
    aisbx.actor.interface.perception

These interfaces are also unified together into a high-level interface that makes it easier to combine these different functionalities together.


Motion
------
.. automodule:: aisbx.actor.interface.motion
    :members:

Navigation
----------
.. automodule:: aisbx.actor.interface.navigation
    :members:

Perception
----------
.. automodule:: aisbx.actor.interface.perception
    :members:

