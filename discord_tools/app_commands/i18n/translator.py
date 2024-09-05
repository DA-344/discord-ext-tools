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
from typing import TYPE_CHECKING, Set

from discord import Locale
from discord.utils import MISSING

try:
    import googletrans
except ImportError:
    raise RuntimeError(
        'I18N uses the googletrans module for better translation experience, please make sure to install it '
        'by using "pip install googletrans".'
    )

if TYPE_CHECKING:
    from typing_extensions import ParamSpec, ClassVar

    TranslatorSpec = ParamSpec('TranslatorSpec', bound='googletrans.Translator')

__all__ = ('Translator',)


class Translator:
    """The translator for the I18N agent.

    This is a simple wrapper of :class:`googletrans.Translator`.

    Parameters
    ----------
    suppress_errors: :class:`bool`
        Whether to suppress any errors raised in the translation methods or not. Defaults to ``False``.
    *args
        The arguments to use to initialize the translator.
    **kwargs
        The key-word arguments to use to initialize the translator.
    """

    __tasks: ClassVar[Set[asyncio.Task]] = set()

    def __init__(
        self,
        *args: TranslatorSpec.args,
        suppress_errors: bool = False,
        **kwargs: TranslatorSpec.kwargs,
    ) -> None:
        self.antecedent: googletrans.Translator = googletrans.Translator(
            *args,
            **kwargs,
        )
        self.suppress_errors: bool = suppress_errors
        self._loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

    async def _a_translate(self, content: str, dest: str = 'en', source: str = 'auto') -> str:
        try:
            res = await self._loop.run_in_executor(None, self.antecedent.translate, content, dest, source)
        except:  # NOQA
            if not self.suppress_errors:
                raise
            return content
        else:
            return res.text

    def _translate(
        self,
        content: str,
        /, *,
        destination: Locale = Locale.british_english,
        source: Locale = MISSING,
    ) -> str:
        """Translates a text from ``source`` to ``destination``.

        If it cannot be translated then it returns the original string.

        Parameters
        ----------
        content: :class:`str`
            The content to translate.
        destination: :class:`discord.Locale`
            The locale to translate the text to.
        source: :claass:`discord.Locale`
            The locale the text is from.

        Returns
        -------
        :class:`str`
            The translated string, or the original if it could not be translated.
        """
        dest_code = destination.value[:2]
        source = source.value[:2] if source is not MISSING else 'auto'
        task = self._loop.create_task(self._a_translate(content, dest_code, source))
        self.__tasks.add(task)
        task.add_done_callback(self.__tasks.discard)
        yield from task
