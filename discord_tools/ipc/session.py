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
import logging
from typing import Any, overload, TYPE_CHECKING, Coroutine

from .route import Route
from ._types import dumps, loads

import aiohttp
from discord.utils import MISSING

if TYPE_CHECKING:
    from typing_extensions import Self

logger = logging.getLogger(__name__)

__slots__ = ("ServerSession",)


class ClientSession:
    """A simple wrapper around an :class:`~aiohttp.ClientSession` for easy handling with an IPC server.

    .. container:: operations

        .. describe:: async with x

            Asynchronously starts this client session.

    Parameters
    ----------
    host: :class:`str`
        The host to connect to. Defaults to ``localhost``.
    port: :class:`int`
        The port to connect to. If missing, uses the multicast port.
    multicast_port: :class:`int`
        The multicast port to connect to. Defaults to ``20000``.
    secret_key: :class:`str`
        The secret key to use on the ``Authorization`` header on request.
        This must have the same value as :attr:`Server.secret_key`.
    session: :class:`~aiohttp.ClientSession`
        The session to use with this handler. If not provided creates a new one.
    """

    __slots__ = (
        "host",
        "port",
        "multicast_port",
        "_secret_key",
        "session",
    )

    def __init__(
        self,
        host: str = "localhost",
        port: int = MISSING,
        multicast_port: int = 20000,
        secret_key: str = MISSING,
        *,
        session: aiohttp.ClientSession = MISSING,
    ) -> None:
        self.host: str = host
        self.port: int | None = port if port is not MISSING else None
        self.multicast_port: int = multicast_port
        self._secret_key: str = secret_key

        if session is MISSING:
            session = aiohttp.ClientSession()
        self.session: aiohttp.ClientSession = session

    @property
    def resolved_port(self) -> int:
        """:class:`int`: Returns the resolved port to connect to, this is either the ``port`` parameter
        or the ``multicast_port`` parameter if no value was provided on the previous one.
        """
        return self.port or self.multicast_port

    @property
    def secret_key(self) -> str | None:
        """Optional[:class:`str`]: The secret key to use on authorization, or ``None``."""
        return self._secret_key if self._secret_key is not MISSING else None

    @property
    def url(self) -> str:
        """:class:`str`: Returns the URL of the websocket."""
        return f"ws://{self.host}:{self.resolved_port}"

    @overload
    async def request(self, route: str, /, **options: Any) -> dict[str, Any]: ...

    @overload
    async def request(self, route: Route, /, **options: Any) -> dict[str, Any]: ...

    async def request(self, route: str | Route, /, **data: Any) -> dict[str, Any]:
        """Makes a request to the IPC server.

        Parameters
        ----------
        route: Union[:class:`str`, :class:`~.Route`]
            The route to perform the request to.
        **data: Any
            The data to send to the endpoint.
        """

        route = str(route)

        async with self.session.ws_connect(
            url=self.url, autoping=False, autoclose=False
        ) as ws:
            payload = {
                "endpoint": route,
                "data": data,
                "headers": {"Authorization": self.secret_key},
            }

            await ws.send_json(payload, dumps=dumps)
            logger.debug("Session -> %s", payload)

            resp = await ws.receive()

            if resp.type == aiohttp.WSMsgType.PING:
                logger.debug("Received a PING request")
                await ws.ping()
                logger.debug("Sent a PING request, retrying request...")
                return await self.request(route, **data)

            if resp.type == aiohttp.WSMsgType.PONG:
                logger.debug("Received a PONG request, retrying request...")
                return await self.request(route, **data)

            if resp.type == aiohttp.WSMsgType.CLOSED:
                sleep_time = 5.5
                tries = 0
                logger.error(
                    f"WebSocket connection was closed: IPC server is unreachable. Attempting reconnection in {sleep_time}...\n"
                    "Make sure the IPC is available and you have provided the correct host and port values."
                )

                reconnection_failed = (
                    "WebSocket reconnection failed. Retrying in {0} seconds..."
                )

                await asyncio.sleep(5)

                while (await ws.receive()).type == aiohttp.WSMsgType.CLOSED:
                    logger.debug(reconnection_failed.format(sleep_time))
                    await asyncio.sleep(sleep_time)
                    tries += 1

                    if tries > 5:
                        raise aiohttp.ServerDisconnectedError(resp)  # type: ignore

                    sleep_time += (
                        0.5 * tries
                    )  # Wait (1/2)n per iteration assuming n < 5

                logger.info(
                    "Successfully reconnected to IPC server. Retrying request..."
                )
                return await self.request(route, **data)

            return await resp.json(loads=loads)

    def __call__(
        self, route: str | Route, /, **data: Any
    ) -> Coroutine[Any, Any, dict[str, Any]]:
        return self.request(route, **data)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
