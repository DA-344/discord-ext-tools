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

from typing import Any, List, Union, TYPE_CHECKING

from discord.utils import _human_join as human_join
from discord.abc import Snowflake
from discord.app_commands import CheckFailure

if TYPE_CHECKING:
    from .enums import BucketType

__all__ = (
    'MissingSKU',
    'MaxConcurrencyReached',
)


class MissingSKU(CheckFailure):
    """An exception raised when a command invoker is missing a SKU.

    Attributes
    ----------
    skus: List[Union[:class:`discord.abc.Snowflake`, :class:`str`, :class:`int`]]
        The SKUs that are missing.
        These are the same as the ones provided in :class:`.has_skus`.
    """

    def __init__(self, skus: List[Union[Snowflake, str, int]], *args: Any) -> None:
        self.skus: List[Union[Snowflake, str, int]] = skus
        fmt = human_join(list(str(sku.id) if isinstance(sku, Snowflake) else sku for sku in skus), final="and")
        super().__init__(
            f'You are missing {fmt} SKU to run this command.',
            *args,
        )


class MaxConcurrencyReached(CheckFailure):
    """An exception raised when a command has reached its max concurrency.

    Attributes
    ----------
    number: :class:`int`
        The maximum number of concurrent invokers allowed.
    per: :class:`.BucketType`
        The bucket type passed to the :func:`.max_concurrency` decorator.
    """

    def __init__(self, number: int, per: BucketType) -> None:
        # MIT License (c) 2015 - present Rapptz
        self.number: int = number
        self.per: BucketType = per
        name = per.name
        suffix = 'per %s' % name if per.name != 'default' else 'globally'
        plural = '%s times %s' if number > 1 else '%s time %s'
        fmt = plural % (number, suffix)
        super().__init__(
            f'Too many people are using this command. It can only be used {fmt} concurrently.'
        )
