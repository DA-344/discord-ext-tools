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

import logging
from typing import Generic, Optional, ClassVar, TYPE_CHECKING, TypeVar, Any

from .state import ServerState
from .route import Route

from discord.utils import MISSING, copy_doc

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ._types import CoroFunc, ClientT

C = TypeVar('C')
CT = TypeVar('CT')

__all__ = (
    'route',
    'Server',
)


def route(name: str = MISSING):
    """A decorator that registers a coroutine as a server route.

    Parameters
    ----------
    name: :class:`str`
        The route name. Defaults to the function name.
    """

    def decorator(func: CoroFunc[C]) -> Route[C]:
        resolved_name = func.__name__ if name is MISSING else name
        if not resolved_name:
            raise ValueError('cannot have an empty route name')
        if resolved_name[0] != '/':
            resolved_name = '/' + resolved_name
        return Route(func, resolved_name)

    return decorator


class Server(Generic[CT]):
    """The server used for the IPC.

    Parameters
    ----------
    client: :class:`~discord.Client`
        The client associated to this server.
    host: :class:`str`
        The host to run the server on. Defaults to ``localhost``.
    port: :class:`int`
        The port to run the server on. Defaults to ``8000``.
    secret_key: :class:`str`
        The secret key to check for on the ``Authorization`` header on requests.
        This can be used to limit requests to your bot, you must have the same secret
        key on the client.
    multicast: :class:`bool`
        Whether to enable multicasting. Defaults to ``True``.
    multicast_port: :class:`int`
        The port to run the multicasting server on. Defaults to ``20000``.
    """

    _routes: ClassVar[dict[str, Route[Any]]] = {}

    __slots__ = (
        'client',
        '_secret_key',
        'host',
        'port',
        'multicast',
        'multicast_port',
        '_state',
    )

    def __init__(
        self,
        client: ClientT[CT],
        host: str = "localhost",
        port: int = 8000,
        secret_key: str = MISSING,
        multicast: bool = True,
        multicast_port: int = 20000,
    ) -> None:
        self.client: ClientT[CT] = client

        self._secret_key: str = secret_key
        self.host: str = host
        self.port: int = port
        self.multicast: bool = multicast
        self.multicast_port: int = multicast_port

        self._state: ServerState = ServerState(client, host, port, multicast, multicast_port, self.secret_key)

    @property
    def secret_key(self) -> str | None:
        """Optional[:class:`str`]: Returns the secret key required for requests handling, or ``None``."""
        return self._secret_key if self._secret_key is not MISSING else None

    @property
    def ws_url(self) -> str:
        """:class:`str`: Returns the websocket URL of this server."""
        return f"ws://{self.host}:{self.port}"

    @property
    def multicast_ws_url(self) -> str:
        """:class:`str`: Returns the multicast websocket URL of this server."""
        return f"ws://{self.host}:{self.multicast_port}"

    @copy_doc(route)
    def route(self, name: str = MISSING):
        return route(name)

    async def terminate_server(self) -> None:
        """Terminates the web server."""
        await self._state.terminate_applications()
