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

from typing import Dict, Any, TYPE_CHECKING

from discord import Interaction
from discord.ext.commands.cooldowns import _Semaphore as Semaphore

from .enums import BucketType
from .errors import MaxConcurrencyReached

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = (
    'MaxConcurrency',
)


class MaxConcurrency:
    # Similar copy from discord.py's max_concurrency object
    # MIT License (c) 2015 - present Rapptz

    __slots__ = (
        'number',
        'per',
        '_mapping',
    )

    def __init__(self, number: int, *, per: BucketType) -> None:
        self._mapping: Dict[Any, Semaphore] = {}
        self.per: BucketType = per
        self.number: int = number

        if number <= 0:
            raise ValueError(
                "max_concurrency 'number' cannot be lower than 0"
            )

        if not isinstance(per, BucketType):
            raise TypeError(
                f"max_concurrency 'per' must be of type BucketType, not '{per.__class__.__name__}'"
            )

    def copy(self) -> Self:
        return self.__class__(self.number, per=self.per)

    def __repr__(self) -> str:
        return f'<MaxConcurrency per={self.per!r} number={self.number}>'

    def get_key(self, interaction: Interaction[Any]) -> Any:
        return self.per.get_key(interaction)

    async def acquire(self, interaction: Interaction[Any]) -> None:
        key = self.get_key(interaction)

        try:
            sem = self._mapping[key]
        except KeyError:
            self._mapping[key] = sem = Semaphore(self.number)

        acquired = await sem.acquire(wait=False)
        if not acquired:
            raise MaxConcurrencyReached(self.number, self.per)

    async def release(self, interaction: Interaction[Any]) -> None:
        key = self.get_key(interaction)

        try:
            sem = self._mapping[key]
        except KeyError:
            return
        else:
            sem.release()

        if sem.value >= self.number and not sem.is_active():
            del self._mapping[key]
