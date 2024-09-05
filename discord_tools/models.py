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

from typing import Dict, Any, Union, Literal, Coroutine, TYPE_CHECKING

from discord import Interaction
from discord.ext.commands import BucketType as ExtBucketType, Context

from .errors import MaxUsagesReached

if TYPE_CHECKING:
    from .app_commands.enums import BucketType as AppBucketType

    BucketType = Union[ExtBucketType, AppBucketType]

__all__ = (
    'MaxUsages',
)


class MaxUsages:
    """Represents a maximum usages object.

    This is not meant to be constructed manually but rather built by :func:`.max_usages`.

    Attributes
    ----------
    limit: :class:`int`
        The usages limit that are allowed before raising :exc:`MaxUsagesReached`.
    bucket: Union[:class:`discord.ext.commands.BucketType`, :class:`.BucketType`]
        The bucket in which the usages are restricted by.
    hide_after_limit: :class:`bool`
        Whether to set the ``hidden`` attribute to ``True`` when the limit is reached.
    disable_after_limit: :class:`bool`
        Whether to set the ``enabled`` attribute to ``False`` when the limit is reached.
    """
    def __init__(self, limit: int, bucket: BucketType, **options: Any) -> None:
        self.limit: int = limit
        self.bucket: BucketType = bucket
        self.hide_after_limit: bool = options.pop('hide_after_limit', False)
        self.disable_after_limit: bool = options.pop('disable_after_limit', False)
        self._data: Dict[Any, int] = {}

    async def check_usage(self, context: Union[Context[Any], Interaction[Any]]) -> Literal[True]:
        key = self.get_bucket(context)

        if key in self._data:
            usages = self._data[key]
        else:
            self._data[key] = usages = 0

        if usages < self.limit:
            self._data[key] += 1
            return True

        if self.bucket.name == 'default':
            if self.hide_after_limit is True:
                context.command.hidden = True
            if self.disable_after_limit is True:
                context.command.enabled = False
        raise MaxUsagesReached(context.command, self.limit)

    def __call__(self, context: Union[Context[Any], Interaction[Any]]) -> Coroutine[Any, Any, Literal[True]]:
        return self.check_usage(context)

    def get_bucket(self, context: Union[Context[Any], Interaction[Any]]) -> Any:
        return self.bucket.get_key(context)
