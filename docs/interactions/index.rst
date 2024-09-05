.. currentmodule:: discord.ext.tools.app_commands

API Reference
=============

This section outlines all the available tools for interaction based commands (application commands, UI kit, etc.)

Models
------

MaxConcurrency
~~~~~~~~~~~~~~

.. attributetable:: MaxConcurrency

.. autoclass:: MaxConcurrency()

Enumerations
------------

BucketType
~~~~~~~~~~

.. attributetable:: BucketType

.. autoclass:: BucketType


Exceptions
----------

.. exception_hierarchy::

    - :dpy:`app_commands.CheckFailure`
        - :exc:`MissingSKU`
        - :exc:`MaxConcurrencyReached`

.. autoexception:: MissingSKU()

.. autoexception:: MaxConcurrencyReached()


Checks
------

.. autofunction:: max_usages

.. autofunction:: has_skus

.. autofunction:: max_concurrency
