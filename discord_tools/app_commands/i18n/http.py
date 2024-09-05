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

from typing import TYPE_CHECKING

from discord.http import HTTPClient as BHTTPC, MultipartParameters, Response

from .translator import Translator
from .agent import Agent

if TYPE_CHECKING:
    from discord.types import (
        message,
    )
    from discord.types.snowflake import Snowflake


class HTTPClient(BHTTPC):
    def edit_message(
        self, channel_id: Snowflake, message_id: Snowflake, *, params: MultipartParameters
    ) -> Response[message.Message]:
        content = params.payload.get('content')

        if content is not None:
            translated, language = Translator.decode_language(content)
            if language:
                params.payload.update({'content': Translator.translate(language, params, content, **Agent.config)})

        return super().edit_message(channel_id, message_id, params=params)

    def send_message(
        self,
        channel_id: Snowflake,
        *,
        params: MultipartParameters,
    ) -> Response[message.Message]:
        content = params.payload.get('content')

        if content is not None:
            payload, language = Translator.decode_language(content)

            if language:
                payload = Translator.translate(
                    language, params, **Agent.config,
                )
                params.payload.update(payload)
        return super().send_message(channel_id, params=params)
