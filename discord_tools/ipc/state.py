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
import asyncio
from typing import Optional, Any

from .response import Request
from ._types import loads, dumps, CoroFunc
from .route import Route

import aiohttp
import aiohttp.web
from discord import Client
from discord.utils import MISSING

logger = logging.getLogger(__name__)

__all__ = ("ServerState",)


class ServerState:
    def __init__(
        self,
        client: Client,
        host: str,
        port: int,
        multicast: bool,
        multicast_port: int,
        secret_key: Optional[str],
    ) -> None:
        self.loop: asyncio.AbstractEventLoop = client.loop
        self.client: Client = client
        self.host: str = host
        self.port: int = port
        self.multicast: bool = multicast
        self.multicast_port: int = multicast_port
        self.secret_key: Optional[str] = secret_key
        self.routes: dict[str, Route[Any]] = {}
        self.application: aiohttp.web.Application = MISSING
        self.multicast_application: aiohttp.web.Application = MISSING
        self.applications_tcps: dict[
            aiohttp.web.Application, tuple[aiohttp.web.AppRunner, aiohttp.web.TCPSite]
        ] = {}

    async def send_json(
        self,
        websocket: aiohttp.web.WebSocketResponse,
        data: dict[str, Any],
        compress: bool | None = None,
    ):
        await websocket.send_json(
            data,
            compress=compress,
            dumps=dumps,
        )
        logger.debug("IPC -> %r", data)

    @property
    def index_router(self) -> CoroFunc:
        if "/" in self.routes:
            return self.routes["/"]
        return self.handle_request

    async def setup_application(self):
        self.application = aiohttp.web.Application()
        self.application.router.add_route("GET", "/", self.index_router)

        if self.multicast:
            self.multicast_application = aiohttp.web.Application()
            self.multicast_application.router.add_route("GET", "/", self.handle_multicast_request)  # type: ignore

    async def start_application(self, multicast: bool = False):
        if multicast:
            application = self.multicast_application
            port = self.multicast_port
        else:
            application = self.application
            port = self.port

        if application is MISSING:
            raise RuntimeError("Application is not yet set up")

        app_runner = aiohttp.web.AppRunner(application)
        await app_runner.setup()

        tcp = aiohttp.web.TCPSite(app_runner, self.host, port)
        await tcp.start()

        self.applications_tcps[application] = (app_runner, tcp)

    async def terminate_applications(self) -> None:
        if self.application is not MISSING:
            await self.application.shutdown()
            await self.application.cleanup()
            del self.applications_tcps[self.application]
        if self.multicast_application is not MISSING:
            await self.multicast_application.shutdown()
            await self.multicast_application.cleanup()
            del self.applications_tcps[self.multicast_application]

    async def handle_request(self, request: aiohttp.web.Request):
        ws = aiohttp.web.WebSocketResponse()
        await ws.prepare(request)

        msg: aiohttp.WSMessage
        async for msg in ws:
            payload = msg.json(loads=loads)
            logger.debug("IPC <- %r", payload)

            if "endpoint" not in payload:
                logger.warning(
                    "A request (%s) had no endpoint set",
                    repr(request),
                )
                await self.send_json(
                    ws,
                    {"error": "No endpoint was set", "code": 401},
                )
                return

            endpoint = payload["endpoint"]
            if endpoint not in self.routes:
                logger.warning(
                    "Received a request pointing to %s, which is not a valid route.",
                    endpoint,
                )
                await self.send_json(
                    ws,
                    {"error": "Invalid endpoint provided", "code": 400},
                )
                return

            headers = request.get("headers", {})

            if "Authorization" not in headers:
                logger.warning("Received an unauthorized request.")
                await self.send_json(ws, {"error": "Unauthorized", "code": 401})
                return

            if headers["Authorization"] != self.secret_key:
                await self.send_json(ws, {"error": "Unauthorized", "code": 403})
                return

            ret = Request(payload.get("data", {}), ws, endpoint, headers, self.loop)
            self.client.dispatch("raw_ipc_request", ret)

            if endpoint in self.routes:
                await self.routes[endpoint](ret)
                self.client.dispatch("ipc_request_completion", ret)

    async def handle_multicast_request(self, request: aiohttp.web.Request):
        logger.debug("Starting IPC multicast server")
        ws = aiohttp.web.WebSocketResponse()
        await ws.prepare(request)

        msg: aiohttp.WSMessage
        async for msg in ws:
            payload = msg.json(loads=loads)
            logger.debug("IPC Multicast <- %r", payload)

            headers = payload.get("headers", {})

            if "Authorization" not in headers:
                logger.warning("Received an unauthorized request.")
                await self.send_json(ws, {"error": "Unauthorized", "code": 403})
                return

            if headers["Authorization"] != self.secret_key:
                await self.send_json(
                    ws,
                    {"error": "Unauthorized", "code": 403},
                )
                return

            await self.send_json(
                ws,
                {
                    "message": "Successfully connected",
                    "code": 200,
                    "port": self.port,
                },
            )
