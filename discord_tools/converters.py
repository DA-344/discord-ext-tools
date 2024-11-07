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

import re
from typing import TYPE_CHECKING

from .errors import StringDoesNotMatch

from discord.ext.commands import Converter, Context, clean_content

if TYPE_CHECKING:
    from typing_extensions import Self

    from discord.ext.commands.core import BotT

__all__ = ("RegexConverter",)


class RegexConverter(Converter[re.Match[str]]):
    """A converter that finds a regex on an argument.

    This converter can be used as it follows:

    .. code-block:: python3

        # pattern = re.compile(r"some-regex")

        @commands.command()
        # async def test(ctx, arg: RegexConverter[pattern]):
        async def test(ctx, arg: RegexConverter[r"some-regex"]):
            await ctx.reply(f'{arg} matches!')

    Or if you want to have more precise options:

    .. code-block:: python3

        @commands.command()
        async def test(ctx, arg: RegexConverter(pattern, **options)):
            await ctx.reply(f'{arg} matches!')

    As Python does not know this returns a :class:`re.Match` object using the previous shown ways, the recommended way
    is to use ``Annotated[re.Match[str], RegexConverter[...]]``. For example:

    .. code-block:: python3

        @commands.command()
        async def test(ctx, arg: typing.Annotated[re.Match[str], RegexConverter[...]]):
            await ctx.reply(f'{arg} matches!')

    Parameters
    ----------
    pattern: Union[:class:`re.Pattern`, :class:`str`]
        The pattern to search for. If it is a string it is compiled into a :class:`re.Pattern` object
        without any flags.
    use_clean_content: :class:`bool`
        Whether to use the message clean content or not.
    """

    def __init__(
        self,
        pattern: re.Pattern[str] | str,
        *,
        use_clean_content: bool = False,
    ) -> None:
        if isinstance(pattern, str):
            pattern = re.compile(pattern)

        self.pattern: re.Pattern[str] = pattern
        self.use_clean_content: bool = use_clean_content

    def __repr__(self) -> str:
        return f"RegexConverter[r{self.pattern.pattern!r}]"

    def __class_getitem__(cls, obj: re.Pattern[str] | tuple[re.Pattern[str]]) -> Self:
        if isinstance(obj, tuple):
            pattern = obj[0]
        else:
            pattern = obj
        return cls(pattern=pattern)

    async def convert(self, ctx: Context[BotT], argument: str) -> re.Match[str]:
        if self.use_clean_content:
            content = await clean_content().convert(ctx, argument)
        else:
            content = argument

        match = self.pattern.fullmatch(content)
        if match is None:
            raise StringDoesNotMatch(self, argument)
        return match
