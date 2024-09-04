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

from enum import Enum
from typing import Any

from discord import Interaction

__all__ = (
    'BucketType',
)


class BucketType(Enum):
    """Specifies a type of bucket for, e.g. a cooldown.

    This works in a similar way as :attr:`discord.ext.commands.BucketType`, but designed
    for interactions.

    To pass a BucketType to a application commands cooldown you must do the following:

    .. code-block:: python3
        @app_commands.command(...)
        @app_commands.checks.cooldown(rate, per, key=BucketType.default)  # Change the bucket type as desired
        async def my_command(...):
            ...
    """

    default = 0
    """The default bucket operates on a global basis."""
    user = 1
    """The user bucket operates on a per-user basis."""
    guild = 2
    """The guild bucket operates on a per-guild basis."""
    channel = 3
    """The channel bucket operates on a per-channel basis."""
    member = 4
    """The member bucket operates on a per-member basis."""
    category = 5
    """The category bucket operates on a per-category basis."""
    role = 6
    """The role bucket operates on a per-role basis."""

    def get_key(self, interaction: Interaction[Any]) -> Any:
        if self is BucketType.user:
            return interaction.user.id
        if self is BucketType.guild:
            return interaction.guild_id or interaction.user.id
        if self is BucketType.channel:
            return interaction.channel_id
        if self is BucketType.member:
            return interaction.guild_id, interaction.user.id
        if self is BucketType.category:
            return (interaction.channel and (interaction.channel.category or interaction.channel)).id
        if self is BucketType.role:
            return interaction.channel_id if interaction.guild_id is None else interaction.user.top_role.id  # type: ignore

    def __call__(self, interaction: Interaction[Any]) -> Any:
        return self.get_key(interaction)
