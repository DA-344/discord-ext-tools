"""
The MIT License (MIT)

Copyright (c) 2024-present Developer Anonymous

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations

from typing import Any

from discord import Permissions, Member
from discord.utils import MISSING
from discord.abc import Snowflake
from discord.ext.commands import BucketType, Context, check

from .models import MaxUsages
from .errors import NotInValidGuild, MissingAnyPermissions, MissingAttachments, NoVoiceState

__all__ = (
    'max_usages',
    'guilds',
    'has_any_permissions',
    'has_attachments',
    'has_voice_state',
)


def max_usages(
    limit: int,
    bucket: BucketType,
    *,
    hide_after_limit: bool = False,
    disable_after_limit: bool = False,
):
    """A decorator that adds a limit of usages to a command.

    This decorator is for prefixed commands only, for an application commands
    version see :func:`~.app_commands.max_usages`.

    Parameters
    ----------
    limit: :class:`int`
        The amount of allowed usages before the command is no longer usable.
    bucket: :class:`discord.ext.commands.BucketType`
        The bucket in which the usages are restricted by.
    hide_after_limit: :class:`bool`
        Whether to set the :attr:`discord.ext.commands.Command.hidden` attribute to ``True`` after the limit is
        exhausted. Defaults to ``False``. Only allowed if ``bucket`` is :attr:`discord.ext.commands.BucketType.default`.
    disable_after_limit: :class:`bool`
        Whether to set the :attr:`discord.ext.commands.Command.enabled` attribute to ``False`` after the limit is
        exhausted. Defaults to ``False``. Only allowed if ``bucket`` is :attr:`discord.ext.commands.BucketType.default`.
    """
    return check(
        MaxUsages(
            limit,
            bucket,
            hide_after_limit=hide_after_limit,
            disable_after_limit=disable_after_limit
        )
    )


def guilds(*guild_ids: Snowflake | int):
    """A decorator that adds a guild checks to a command.

    This makes the command only available in the provided guilds.

    This decorator is for prefixed commands only, for an application commands
    version see :func:`discord.app_commands.guilds`.

    Parameters
    ----------
    *guild_ids: Union[:class:`discord.abc.Snowflake`, :class:`int`]
        The guilds to limit the command to.
    """
    guild_ids = [guild.id if isinstance(guild, Snowflake) else guild for guild in guild_ids]

    async def predicate(context: Context[Any]) -> bool:
        if not context.guild:
            return True
        if context.guild.id not in guild_ids:
            raise NotInValidGuild(context.command, context.guild)
        return True
    return check(predicate)


def has_any_permissions(**perms: bool):
    """A decorator that adds a permissions check.

    Unlike :func:`discord.ext.commands.has_permissions`, :func:`discord.ext.commands.has_guild_permissions` this checks
    if the command invoker has **any** of the provided permissions.

    Parameters
    ----------
    **perms: :class:`bool`
        The permissions to check for.
    """

    invalid = set(perms) - set(Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f'Invalid permission(s) provided in has_any_permissions: {", ".join(invalid)}')

    def predicate(context: Context[Any]) -> bool:
        permissions = context.permissions

        if any(
            getattr(permissions, perm) == value
            for perm, value in perms.items()
        ):
            return True
        raise MissingAnyPermissions(list(perms.keys()))
    return check(predicate)


def has_attachments(*, count: int = MISSING):
    """A decorator that checks if the invoker message has any attachments.

    Parameters
    ----------
    count: :class:`int`
        The amount of attachments the message should have for this check to pass successfully. Limit is 10.
    """
    if count is not MISSING and count > 10:
        raise ValueError('Can only limit attachments to 10')

    def predicate(context: Context[Any]) -> bool:
        if count is MISSING:
            if not context.message.attachments:
                raise MissingAttachments(0, 1)
        else:
            if len(context.message.attachments) < count:
                raise MissingAttachments(len(context.message.attachments), count)
        return True
    return check(predicate)


def has_voice_state():
    """A decorator that checks if the command invoker has a voice state (is in a voice channel).
    """

    def predicate(context: Context[Any]) -> bool:
        if not isinstance(context.author, Member):
            return True  # Ignore for non-guild commands.
        if context.author.voice is None:
            raise NoVoiceState(context.author, context)
        return True
    return check(predicate)
