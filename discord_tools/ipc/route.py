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

import asyncio
from typing import TypeVar, Generic, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ._types import CoroFunc, Coro
    from .response import Request

R = TypeVar('R')

__all__ = (
    'Route',
)


class Route(Generic[R]):
    """Represents a server route.

    .. container:: operations

        .. describe:: str(x)

            Returns this route name.

    Attributes
    ----------
    name: :class:`str`
        The route name, always prefixed with ``/``.
    callback: Callable[..., Coroutine[Any, Any, Any]]
        The callback of the route, this is called when it receives a request.
    """

    __slots__ = (
        'callback',
        'name',
    )

    def __init__(self, callback: CoroFunc[R], name: str) -> None:
        if not asyncio.iscoroutinefunction(callback):
            raise TypeError(
                f'callback on {name!r} route is not a coroutine'
            )
        self.callback: CoroFunc[R] = callback
        self.name: str = name

    def __call__(self, request: Request) -> Coro[R]:
        return self.callback(request)

    def __str__(self) -> str:
        return f'{self.name}'

    def __setattr__(self, name: str, value: Any) -> None:
        raise TypeError(
            'routes are immutable'
        )
