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
from typing import Any, Iterator
from collections.abc import KeysView, ValuesView, ItemsView

from ._types import dumps

import aiohttp.web

__all__ = (
    'Request',
)


class Request:
    """Represents an IPC request.

    .. container:: operations

        .. describe:: for ... in x

            Iterates through all the request data keys.

    Attributes
    ----------
    endpoint: :class:`str`
        The endpoint this request pointed to.
    headers: Dict[:class:`str`, Any]
        The headers the request provided.
    """

    __slots__ = (
        '_data',
        '_ws',
        '_response_future',
        '_loop',
        'endpoint',
        'headers',
    )

    def __init__(
        self,
        data: dict[str, Any],
        ws: aiohttp.web.WebSocketResponse,
        endpoint: str,
        headers: dict[str, Any],
        loop: asyncio.AbstractEventLoop,
    ) -> None:
        self._data: dict[str, Any] = data
        self._ws: aiohttp.web.WebSocketResponse = ws
        self._response_future: asyncio.Future[None] = loop.create_future()
        self._loop: asyncio.AbstractEventLoop = loop
        self.endpoint: str = endpoint
        self.headers: dict[str, Any] = headers

    def __getitem__(self, key: str):
        return self._data[key]

    def __setitem__(self, key: str, value: Any):
        raise TypeError('Responses are immutable')

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def keys(self) -> KeysView:
        """:class:`~collections.abc.KeysView`: Returns all the keys of the data the request provided.

        This is similar to :meth:`dict.keys`.
        """
        return self._data.keys()

    def values(self) -> ValuesView:
        """:class:`~collections.abc.ValuesView`: Returns all the values of the data the request provided.

        This is similar to :meth:`dict.values`.
        """
        return self._data.values()

    def items(self) -> ItemsView:
        """:class:`~collections.abc.ItemsView`: Returns (key, value) pairs of all the keys and values the request
        provided.

        This is similar to :meth:`dict.items`.
        """
        return self._data.items()

    def is_done(self) -> bool:
        """:class:`bool`: Returns whether the request has been responded."""
        return self._response_future.done()

    async def wait_until_done(self) -> bool:
        """Waits for this request to be completed.

        This could be useful if you respond to a request on another place outside :func:`on_ipc_request`.
        """
        result = await self._response_future
        if result:
            raise result
        return True

    async def respond(self, data: dict[str, Any], *, compress: bool | None = None) -> None:
        """Sends a JSON response to this request.

        Parameters
        ----------
        data: Dict[:class:`str`, Any]
            The data to send as response.
        compress: Optional[:class:`bool`]
            Whether to compress the response data.
        """

        try:
            await self._ws.send_json(
                data,
                compress=compress,
                dumps=dumps,
            )
        except Exception as exc:
            self._response_future.set_exception(exc)
        else:
            self._response_future.set_result(None)

