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

from dataclasses import dataclass
import re
from typing import TYPE_CHECKING, Any, TypeVar, Union

from discord.utils import maybe_coroutine, MISSING
from discord.ext.commands import (
    FlagConverter,
    Flag as BaseFlag,
    MissingFlagArgument,
    TooManyArguments,
    Context,
    Bot,
    AutoShardedBot,
    MissingRequiredFlag,
    TooManyFlags,
)
from discord.ext.commands.flags import convert_flag

BotT = TypeVar("BotT", bound=Union[Bot, AutoShardedBot], covariant=True)

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = (
    "Flag",
    "flag",
    "ImplicitBoolFlagConverter",
)


@dataclass
class Flag(BaseFlag):
    """Represents a flag parameter for a :class:`FlagConverter`.

    The :func:`flag` function helps with the creation of these flag
    objects, but it is not necessary to do so. These cannot be constructed
    manually.

    Attributes
    ----------
    name: :class:`str`
        The name of the flag.
    aliases: List[:class:`str`]
        The aliases of the flag name.
    attribute: :class:`str`
        The attribute in the class that corresponds to this flag.
    default: Any
        The default value of the flag, if available.
    annotation: Any
        The underlying evaluated annotation of the flag.
    max_args: :class:`int`
        The maximum number of arguments the flag can accept.
        A negative value indicates an unlimited amount of arguments.
    override: :class:`bool`
        Whether multiple given values override the previous one.
    description: :class:`str`
        The description of the flag. Shown for hybrid commands when they're
        used as application commands.
    positional: :class:`bool`
        Whether the flag is positional or not. There can only be one positional flag.
    implicit: :class:`bool`
        Whether the flag is implicit, this means that only being present makes the flag value
        ``True``, and if not present, ``False``.

        .. warning::

            This can only be used on subclasses of :class:`ImplicitBoolFlagConverter`.

        .. note::

            Settings this to ``True`` will change the ``default`` and ``annotation``
            to ``False`` and ``bool``, respectively.
    """

    implicit: bool = MISSING

    def __post_init__(self):
        if self.implicit is True:
            self.annotation = bool
            self.default = False


def flag(
    *,
    name: str = MISSING,
    aliases: list[str] = MISSING,
    default: Any = MISSING,
    max_args: int = MISSING,
    override: bool = MISSING,
    converter: Any = MISSING,
    description: str = MISSING,
    positional: bool = MISSING,
    implicit: bool = MISSING,
) -> Any:
    """Override default functionality and parameters of the underlying :class:`FlagConverter`
    class attributes.

    Parameters
    ------------
    name: :class:`str`
        The flag name. If not given, defaults to the attribute name.
    aliases: List[:class:`str`]
        Aliases to the flag name. If not given no aliases are set.
    default: Any
        The default parameter. This could be either a value or a callable that takes
        :class:`Context` as its sole parameter. If not given then it defaults to
        the default value given to the attribute.
    max_args: :class:`int`
        The maximum number of arguments the flag can accept.
        A negative value indicates an unlimited amount of arguments.
        The default value depends on the annotation given.
    override: :class:`bool`
        Whether multiple given values overrides the previous value. The default
        value depends on the annotation given.
    converter: Any
        The converter to use for this flag. This replaces the annotation at
        runtime which is transparent to type checkers.
    description: :class:`str`
        The description of the flag. Shown for hybrid commands when they're
        used as application commands.
    positional: :class:`bool`
        Whether the flag is positional or not. There can only be one positional flag.
    implicit: :class:`bool`
        Whether the flag is implicit or not. This means that only being present makes the flag
        value be ``True``, and if not present, `False``.

        .. warning::

            This can only be used on subclasses of :class:`ImplicitBoolFlagConverter`.

        .. note::

            Settings this to ``True`` will change the ``default`` and ``converter``
            values to ``False`` and ``bool``, respectively.
    """

    kwgs = {
        "name": name,
        "aliases": aliases,
        "default": default,
        "max_args": max_args,
        "override": override,
        "annotation": converter,
        "description": description,
        "positional": positional,
    }

    # Try to default to discord.py's Flag object
    if implicit is MISSING:
        return BaseFlag(**kwgs)
    return Flag(**kwgs, implicit=implicit)


class ImplicitBoolFlagConverter(FlagConverter):
    """A custom :class:`discord.ext.commands.FlagConverter` subclass that allows boolean flags to not have a value.

    For example:

    .. code-block:: python3

        from discord_tools import ImplicitBoolFlagConverter, flag

        class MyFlags(ImplicitBoolFlagConverter):
            some_flag = flag(implicit=True)
    """

    if TYPE_CHECKING:
        __commands_flags__: dict[str, Flag | BaseFlag]

    @classmethod
    def parse_flags(
        cls, argument: str, *, ignore_extra: bool = True
    ) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}
        flags = cls.__commands_flags__
        aliases = cls.__commands_flag_aliases__
        positional_flag = cls.__commands_flag_positional__
        last_position = 0
        last_flag: Flag | BaseFlag | None = None

        case_insensitive = cls.__commands_flag_case_insensitive__

        regex_flags = 0
        if case_insensitive:
            flags = {key.casefold(): value for key, value in flags.items()}
            aliases = {
                key.casefold(): value.casefold() for key, value in aliases.items()
            }
            regex_flags = re.IGNORECASE

        prefix = cls.__commands_flag_prefix__
        delimiter = cls.__commands_flag_delimiter__
        keys = [re.escape(k) for k in flags]
        keys.extend(re.escape(a) for a in aliases)
        keys = sorted(keys, key=len, reverse=True)

        joined = "|".join(keys)
        pattern = re.compile(
            f"(({re.escape(prefix)})(?P<flag>{joined})({re.escape(delimiter)}?))",
            flags=regex_flags,
        )

        if positional_flag is not None:
            match = pattern.search(argument)

            if match is not None:
                begin, end = match.span(0)
                value = argument[:begin].strip()
            else:
                value = argument.strip()
                last_position = len(argument)

            if value:
                name = (
                    positional_flag.name.casefold()
                    if case_insensitive
                    else positional_flag.name
                )
                result[name] = [value]

        for match in pattern.finditer(argument):
            begin, end = match.span(0)
            key = match.group("flag")
            if case_insensitive:
                key = key.casefold()

            if key in aliases:
                key = aliases[key]

            flag = flags.get(key)
            if last_position and last_flag is not None:
                value = argument[last_position : begin - 1].lstrip()

                is_implicit = getattr(last_flag, "implicit", False)

                delim = match.group("delimiter")
                if not delim and not is_implicit:
                    continue  # ignore

                if not value and not is_implicit:
                    raise MissingFlagArgument(last_flag)
                elif is_implicit:
                    value = "1"

                name = last_flag.name.casefold() if case_insensitive else last_flag.name

                try:
                    values = result[name]
                except KeyError:
                    result[name] = [value]
                else:
                    values.append(value)

            last_position = end
            last_flag = flag

        value = argument[last_position:].strip()

        if last_flag is not None:
            is_implicit = getattr(last_flag, "implicit", False)

            if not value and not is_implicit:
                raise MissingFlagArgument(last_flag)
            elif is_implicit:
                value = "1"

            name = last_flag.name.casefold() if case_insensitive else last_flag.name

            try:
                values = result[name]
            except KeyError:
                result[name] = [value]
            else:
                values.append(value)
        elif value and not ignore_extra:
            raise TooManyArguments(f"Too many arguments passed to {cls.__name__}")

        return result

    @classmethod
    async def convert(cls, ctx: Context[BotT], argument: str) -> Self:
        ignore_extra = True

        if (
            ctx.command is not None
            and ctx.current_parameter is not None
            and ctx.current_parameter.kind == ctx.current_parameter.KEYWORD_ONLY
        ):
            ignore_extra = ctx.command.ignore_extra

        arguments = cls.parse_flags(argument, ignore_extra=ignore_extra)
        flags = cls.__commands_flags__

        self = cls.__new__(cls)

        for name, flag in flags.items():
            try:
                values = arguments[name]
            except KeyError:
                if flag.required:
                    raise MissingRequiredFlag(flag)
                else:
                    if callable(flag.default):
                        default = await maybe_coroutine(flag.default, ctx)
                        setattr(self, flag.attribute, default)
                    else:
                        setattr(self, flag.attribute, flag.default)
                    continue

            if flag.max_args > 0 and len(values) > flag.max_args:
                if flag.override:
                    value = values[-flag.max_args :]
                else:
                    raise TooManyFlags(flag, values)

            if flag.max_args == 1:
                value = await convert_flag(ctx, values[0], flag)
                setattr(self, flag.attribute, value)
                continue

            values = [await convert_flag(ctx, value, flag) for value in values]
            if flag.cast_to_dict:
                values = dict(values)
            setattr(self, flag.attribute, values)
        return self
