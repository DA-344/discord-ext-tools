.. currentmodule:: discord_tools.app_commands

Interactions API Reference
==========================

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
    :members:


Exceptions
----------

.. exception_hierarchy::

    - :exc:`~discord.app_commands.CheckFailure`
        - :exc:`MissingSKU`
        - :exc:`MaxConcurrencyReached`

.. autoexception:: MissingSKU()

.. autoexception:: MaxConcurrencyReached()


Checks
------

.. autofunction:: max_usages

.. autofunction:: has_skus

.. autofunction:: max_concurrency
