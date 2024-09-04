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

from typing import Union, Any

from discord import Interaction
from discord.abc import Snowflake
from discord.app_commands.checks import check

from .errors import MissingSKU
from .enums import BucketType
from .models import MaxConcurrency
from ..models import MaxUsages

__all__ = (
    'max_usages',
    'has_skus',
)


def max_usages(limit: int, bucket: BucketType):
    """A decorator that adds a limit of usages to a command.

    Parameters
    ----------
    limit: :class:`int`
        The amount of allowed usages before the command is no longer usable.
    bucket: :class:`discord.ext.commands.BucketType`
        The bucket in which the usages are restricted by.
    """
    return check(MaxUsages(limit, bucket))


def has_skus(*sku_ids: Union[int, str, Snowflake]):
    """A decorator that checks if the interaction has all the provided skus.

    Parameters
    ----------
    sku_ids
        The SKU IDs to check for.
    """
    skus = [sku.id if isinstance(sku, Snowflake) else int(sku) for sku in sku_ids]

    def predicate(interaction: Interaction[Any]) -> bool:
        entitlements_sku_ids = [e.sku_id for e in interaction.entitlements]

        if any(
            esi not in skus
            for esi in entitlements_sku_ids
        ):
            raise MissingSKU(list(sku_ids))
        return True
    return check(predicate)


def max_concurrency(number: int, per: BucketType = BucketType.default, *, wait: bool = False):
    """A decorator that adds a maximum concurrency to a :class:`discord.app_commands.Command` or its subclasses.

    This enabled you to only allow a certain number of command invocations at the same time,
    for example if a command takes too long or if only one user can use it at a time. This
    differs from a cooldown in that there is no set waiting period or token bucket -- only
    a set number of people can run the command.

    This is the application command variant, for prefixed commands see :func:`discord.ext.commands.max_concurrency`.

    Parameters
    ----------
    number: :class:`int`
        The maximum number of concurrent invocations.
    per: :class:`.BucketType`
        The bucket that this concurrency is based on, e.g. :attr:`BucketType.guild` would allow
        it to be used up to ``number`` times per guild.
    wait: :class:`bool`
        Whether the command should wait for the queue to be over. If this is set to ``False``
        then instead of waiting until the command can run again, the command raises
        :exc:`.MaxConcurrencyReached` to its error handler. If this is set to ``True``
        then the command waits until it can be executed.
    """

    obj = MaxConcurrency(number, per=per, wait=wait)

    async def predicate(interaction: Interaction[Any]) -> bool:
        await obj.acquire(interaction)
        await obj.release(interaction)
        # If it does not error in obj.acquire then it has not reached the
        # max concurrency yet. So return a True.
        return True
    return check(predicate)
