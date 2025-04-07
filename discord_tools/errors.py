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

import re
from typing import Any, TYPE_CHECKING

from discord import Guild, Member
from discord.ui import Item
from discord.utils import _human_join as human_join
from discord.ext.commands import CheckFailure, Command, Context, ConversionError
from discord.app_commands import CheckFailure as AppCheckFailure, Cooldown

if TYPE_CHECKING:
    from .converters import RegexConverter

__all__ = (
    "MaxUsagesReached",
    "NotInValidGuild",
    "MissingAnyPermissions",
    "MissingAttachments",
    "NoVoiceState",
    "StringDoesNotMatch",
    "ItemOnCooldown",
)


class MaxUsagesReached(CheckFailure):
    """An exception raised when a command has reached its maximum usages.

    Attributes
    ----------
    command: :class:`discord.ext.commands.Command`
        The context that raised the error.
    """

    def __init__(self, command: Command[Any, ..., Any], limit: int, *args: Any) -> None:
        self.command: Command[Any, ..., Any] = command
        super().__init__(
            f"{command.qualified_name} has reached the maximum usages ({limit})", *args
        )


class NotInValidGuild(CheckFailure):
    """An exception raised when a command has been invoked in a non-allowed guild.

    Attributes
    ----------
    command: :class:`discord.ext.commands.Command`
        The command that raised the error.
    guild: :class:`discord.Guild`
        The guild in which this command was invoked in.
    """

    def __init__(
        self, command: Command[Any, ..., Any], guild: Guild, *args: Any
    ) -> None:
        self.command: Command[Any, ..., Any] = command
        self.guild: Guild = guild
        super().__init__(
            f"{guild.id} was not a valid guild for {command.qualified_name} to be invoked",
            *args,
        )


class MissingAnyPermissions(CheckFailure):
    """An exception raised when the command invoker lacks any permissions to run a
    command.

    Attributes
    ----------
    missing_permissions: List[:class:`str`]
        The permissions that the invoker is missing.
    """

    def __init__(self, missing_permissions: list[str], *args: Any) -> None:
        self.missing_permissions: list[str] = missing_permissions

        missing = [
            perm.replace("_", " ").replace("guild", "server").title()
            for perm in missing_permissions
        ]

        message = f'You are missing {human_join(missing, final=", and")} permission(s) to run this command.'
        super().__init__(message, *args)


class MissingAttachments(CheckFailure):
    """An exception raised when the invoker message does not have enough attachments to run
    a command.

    Attributes
    ----------
    attachment_count: :class:`int`
        The amount of attachments the message has.
    attachment_minimum: :class:`int`
        The minimum amount of attachments the message must have.
    """

    def __init__(self, count: int, minimum: int, *args: Any) -> None:
        self.attachment_count: int = count
        self.attachment_minimum: int = minimum
        super().__init__(
            f"{count} attachments were provided and {minimum} were required.",
            *args,
        )


class NoVoiceState(CheckFailure):
    """An exception raised when the command invoker has no voice state (is not connected in a voice channel).

    Attributes
    ----------
    author: :class:`discord.Member`
        The author that did not have a voice state.
    context: :class:`discord.ext.commands.Context`
        The context that failed.
    """

    def __init__(self, author: Member, context: Context[Any], *args: Any) -> None:
        self.author: Member = author
        self.context: Context[Any] = context
        super().__init__(f"{author} has no voice state.", *args)


class StringDoesNotMatch(ConversionError):
    """An exception raised when the :class:`RegexConverter` fails to find an occurrence in a string.

    .. versionadded:: 1.0

    Attributes
    ----------
    pattern: :class:`re.Pattern`
        The pattern that was searched for.
    argument: :class:`str`
        The argument that failed.
    """

    def __init__(self, converter: RegexConverter, argument: str, *args: Any) -> None:
        self.pattern: re.Pattern = converter.pattern
        self.argument: str = argument
        super().__init__(
            converter,
            ValueError(f"{argument!r} did not match {self.pattern!r}.", *args),
        )


class ItemOnCooldown(AppCheckFailure):
    """Exception raised when an item is interacted with but was on cooldown.

    This inherits from :exc:`discord.app_commands.CheckFailure`.
    """

    def __init__(self, item: Item, cooldown: Cooldown) -> None:
        super().__init__(
            f"Item {item} is on cooldown. Retry in {cooldown.get_retry_after()}s"
        )
