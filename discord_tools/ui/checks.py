"""
The MIT License (MIT)

Copyright (c) 2025-present Developer Anonymous

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

from typing import TYPE_CHECKING, Any, Callable, Hashable

from discord import Interaction, app_commands
from discord.ext import commands
from discord.ui.item import Item
from discord.utils import maybe_coroutine, MISSING

from ..errors import ItemOnCooldown

if TYPE_CHECKING:
    from discord.ui.item import ItemCallbackType
    from discord._types import ClientT
    from discord.app_commands.checks import CooldownFunction

    Check = Callable[[Interaction[ClientT], Item[Any]], Any]

__all__ = (
    'check',
    'cooldown',
)


class _callback:
    def __init__(self, checks: list[Check], callback: ItemCallbackType) -> None:
        self.checks: list[Check] = checks
        self.callback: ItemCallbackType = callback

    @property
    def __discord_ui_model_type__(self) -> type[Item]:
        return self.callback.__discord_ui_model_type__

    @property
    def __discord_ui_model_kwargs__(self) -> dict[str, Any]:
        return self.callback.__discord_ui_model_kwargs__

    async def _run_checks(self, interaction: Interaction[ClientT], item: Item[Any]) -> None:
        for check in self.checks:
            ret = await maybe_coroutine(check, interaction, item)

            if not ret:
                raise app_commands.CheckFailure('You are not allowed to use this item.')

    async def _callback(self, view, interaction, item) -> Any:
        await self._run_checks(interaction, item)
        await self.callback(view, interaction, item)

    def __call__(self, view, interaction, item):
        return self._callback(view, interaction, item)


def check(pred: Check):
    """Creates a check for a UI item.

    This can be placed either over the ``@ui.item`` decorator or
    below.

    Parameters
    ----------
    pred: Callable[[:class:`discord.Interaction`], Any]
        The check predicate, which is a function that takes a single parameter: ``interaction``,
        and returns a truthy or falsey value. This can be an async function.
    """

    def decorator(func: ItemCallbackType):
        if isinstance(func, _callback):
            func.checks.append(pred)
        else:
            checks = [pred]
            checks.append(pred)
            callback = _callback(checks, func)
        return callback

    return decorator


def cooldown(
    rate: float,
    per: float,
    *,
    key: CooldownFunction[Hashable] | None = None,
):
    """A decorator that adds a cooldown to an item.

    A cooldown allows a command to only be used a specific amount
    of times in a specific time frame. These cooldowns are based off
    of the ``key`` function provided. If a ``key`` is not provided
    then it defaults to a user-level cooldown. The ``key`` function
    must take a single parameter, the :class:`discord.Interaction` and
    return a value that is used as a key to the internal cooldown mapping.

    The ``key`` function can optionally be a coroutine.

    If a cooldown is triggered, then :exc:`ItemOnCooldown` is
    raised to the error handlers.

    Examples
    ---------

    Setting a one per 5 seconds per member cooldown on a button:

    .. code-block:: python3

        class MyView(discord.ui.View):
            @discord.ui.button(label='Click Me!')
            @discord_tools.ui.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
            async def test(self, interaction: discord.Interaction, button: discord.ui.View):
                await interaction.response.send_message('Hello')

            async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item):
                if isinstance(error, discord_tools.ItemOnCooldown):
                    await interaction.response.send_message(str(error), ephemeral=True)

    Parameters
    ------------
    rate: :class:`int`
        The number of times a command can be used before triggering a cooldown.
    per: :class:`float`
        The amount of seconds to wait for a cooldown when it's been triggered.
    key: Optional[Callable[[:class:`discord.Interaction`], :class:`collections.abc.Hashable`]]
        A function that returns a key to the mapping denoting the type of cooldown.
        Can optionally be a coroutine. If not given then defaults to a user-level
        cooldown. If ``None`` is passed then it is interpreted as a "global" cooldown.
    """

    async def pred(interaction: Interaction, item: Item) -> bool:
        cd_map: commands.CooldownMapping[Interaction] = getattr(pred, '__discord_ui_checks_cooldown__', MISSING)

        if cd_map is MISSING:
            cd_map = commands.CooldownMapping.from_cooldown(rate, per, key or (lambda i: None))
            setattr(pred, '__discord_ui_checks_cooldown__', cd_map)

        retry_after = cd_map.update_rate_limit(interaction)

        if retry_after:
            raise ItemOnCooldown(item, cd_map._cooldown or commands.Cooldown(rate, per))
        return True
    return check(pred)
