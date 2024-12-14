.. currentmodule:: discord_tools

.. _Keep a Changelog: https://keepachangelog.com/en/1.1.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html

.. _changelog:

Changelog
=========

All the changes of this project will be registered here.

This format is based on `Keep A Changelog`_ and this project adheres to
`Semantic Versioning`_.


Unreleased
----------

This changes are available on the ``master`` branch, without any guarantee on functionality and stability.

.. warning::

    This version **contains breaking changes**.

Added
~~~~~

- Added :class:`~discord_tools.app_commands.CogContextMenuHolder`, which allows creating context menus in cogs.
- Added :class:`RegexConverter` converter to allow using :class:`re.Match` objects as annotations in prefixed commands.
    - Added :exc:`StringDoesNotMatch`.
- Added :class:`ImplicitBoolFlagConverter`.
    - New :func:`flag` method to create implicit boolean flags.
    - New :class:`Flag` subclass of :class:`~discord.ext.commands.Flag` which adds the implicit boolean functionality.
- Added a simple IPC.
    - Added :class:`~discord_tools.ipc.Request`.
    - Added :class:`~discord_tools.ipc.Route`.
    - Added :class:`~discord_tools.ipc.Server`.
    - Added :class:`~discord_tools.ipc.ClientSession`.
    - Added :func:`~discord_tools.ipc.route`.
- Added various new methods to :class:`~discord_tools.app_commands.i18n.Translator`.
- Added new :class:`~discord_tools.app_commands.Greedy` transformer.

Changed
~~~~~~~

- :class:`~discord_tools.app_commands.i18n.Translator` is now a subclass of :class:`~discord.app_commands.Translator`.

Removed
~~~~~~~

- Removed ``discord_tools.app_commands.i18n.Client``.
