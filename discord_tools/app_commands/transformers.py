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

from functools import partial
from typing import TypeVar, Generic, Any

import discord
from discord.app_commands import Transformer
from discord.ext.commands import Context, run_converters, CommandError, ArgumentParsingError, MissingRequiredArgument
from discord.ext.commands.converter import CONVERTER_MAPPING, is_generic_type

T = TypeVar('T')

__all__ = ('Greedy',)


class Greedy(Transformer[list[T]]):
    """The app commands version of :class:`~discord.ext.commands.Greedy`.

    This is a :class:`~discord.app_commands.Transformer` subclass, so you need to
    annotate your options as `app_commands.Transform[..., Greedy[...]]`

    .. versionadded:: 1.0
    """

    def __init__(self, converter: T) -> None:
        if converter not in CONVERTER_MAPPING and not is_generic_type(converter):
            raise ValueError(f'Cannot set the Greedy converter to {converter.__class__.__name__}')
        self._converter: T = converter

    async def transform(self, interaction: discord.Interaction, argument: str) -> Any:
        ctx = await Context.from_interaction(interaction)
        assert ctx.current_parameter is not None
        view = ctx.view.__class__(argument)
        conv = partial(run_converters, ctx=ctx, param=ctx.current_parameter, converter=self._converter)

        ret = []

        while not view.eof:
            view.skip_ws()

            arg = view.get_quoted_word() or view.get_word()
            try:
                transformed = await conv(argument=arg)
            except (CommandError, ArgumentParsingError):
                break
            else:
                ret.append(transformed)

        if not ret and ctx.current_parameter.required:
            raise MissingRequiredArgument(ctx.current_parameter)
        elif not ret and not ctx.current_parameter.required:
            ret = ctx.current_parameter.get_default(ctx)

        return ret

    def __class_getitem__(cls, typ: T | tuple[T]) -> "Greedy":
        if isinstance(typ, tuple) and len(typ) > 1:
            raise TypeError('Greedy only accepts one argument')
        elif isinstance(typ, tuple):
            resolved = typ[0]
        else:
            resolved = typ

        if resolved is str:
            raise TypeError('Greedy[str] is not valid')

        return cls(resolved)
