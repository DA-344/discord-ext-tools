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

import inspect
from typing import Generic, Union, TypeVar, Any, Callable, Optional

from discord import Interaction, Message, Member, User
from discord.utils import MISSING, find
from discord.ext.commands import Cog, GroupCog, Bot
from discord.app_commands import ContextMenu, locale_str, CommandTree

CogLike = Union[Cog, GroupCog]
CogT = TypeVar("CogT", bound=CogLike)
T = TypeVar("T")
InteractionT = TypeVar("InteractionT", bound=Interaction[Any])
ContextMenuCallback = Union[
    Callable[[CogT, InteractionT, Message], Any],
    Callable[[CogT, InteractionT, Member], Any],
    Callable[[CogT, InteractionT, User], Any],
    Callable[[CogT, InteractionT, Union[Member, User]], Any],
]

__all__ = ("CogContextMenuHolder",)


class CogContextMenuHolder(Generic[CogT]):
    """Represents a :class:`discord.ext.commands.Cog` or :class:`discord.ext.commands.GroupCog` context menu holder.

    .. versionadded:: 1.0

    Parameters
    ----------
    cog: Union[:class:`discord.ext.commands.Cog`, :class:`discord.ext.commands.GroupCog`]
        The cog this context menu holder belongs to.
    """

    def __init__(self, cog: CogT) -> None:
        self.cog: CogT = cog
        self._context_menus: list[ContextMenu] = []

    @classmethod
    def context_menu(
        cls,
        *,
        name: str | locale_str = MISSING,
        nsfw: bool = False,
        auto_locale_strings: bool = True,
        extras: dict[Any, Any] = MISSING,
    ):
        """A decorator that makes a function a context menu.

        Unlike :func:`discord.app_commands.context_menu` this is designed for
        cogs only.

        Parameters
        ----------
        name: Union[:class:`str`, :class:`discord.app_commands.locale_str`]
            The name of the context menu command. If not given, it defaults to a title-case
            version of the callback name. Note that unlike regular slash commands this can have
            spaces and upper case characters in the name.
        nsfw: :class:`bool`
            Whether the command is NSFW and should only work in NSFW channels. Defaults to ``False``.
            Due to a Discord limitation, this does not work on subcommands.
        auto_locale_strings: :class:`bool`
            If this is set to ``True``, then all translatable strings will implicitly be wrapped into
            :class:`discord.app_commands.locale_str` rather than :class:`str`. This could avoid some
            repetition and be more ergonomic for certain defaults such as default command names, command
            descriptions, and parameter names. Defaults to ``True``.
        extras: :class:`dict`
            A dictionary that can be used to store extraneous data.
        """

        kwargs = {
            "name": name,
            "nsfw": nsfw,
            "auto_locale_strings": auto_locale_strings,
            "extras": extras,
        }

        def wrapper(func: ContextMenuCallback):
            func.__context_menu__ = True  # type: ignore
            func.__context_menu_kwargs__ = kwargs  # type: ignore
            return func

        return wrapper

    @property
    def context_menus(self) -> list[ContextMenu]:
        """List[:class:`discord.app_commands.ContextMenu`]: Returns all the context menus
        that this holder has loaded.
        """
        return self._context_menus.copy()

    def load_menus(self):
        """Loads all the context menus to this holder.

        .. note::

            This **does not** add it to the tree, you must call :meth:`.add_to_tree`
            for the commands to be added to the tree.
        """

        for attr, value in inspect.getmembers(self.cog):
            if getattr(value, "__context_menu__", False):
                data = value.__context_menu_kwargs__
                ret = ContextMenu(
                    **data,
                    callback=value,
                )
                self._context_menus.append(ret)

                # this updates the cog attribute, so it is now a ContextMenu
                # object instead of leaving it as a function
                setattr(self.cog, attr, ret)

    def _get_cog_client(self) -> Optional[Bot]:
        if hasattr(self.cog, "bot"):
            return self.cog.bot  # type: ignore
        if hasattr(self.cog, "client"):
            return self.cog.client  # type: ignore
        return None

    def add_to_tree(self, *, tree: CommandTree = MISSING):
        """Adds the context menus to the command tree.

        If no ``tree`` is passed then it tries to resolve to ``cog.bot`` or ``cog.client``, and after
        that, ``bot.tree``.

        Raises
        ------
        RuntimeError
            No client/bot found on the cog.

        Parameters
        ----------
        tree: :class:`discord.app_commands.CommandTree`
            The tree to add the context menus to.
        """

        if tree is MISSING:
            client = self._get_cog_client()

            if client is None:
                raise RuntimeError(f"No client/bot found on the {self.cog!r} cog.")

            tree = client.tree

        for menu in self.context_menus:
            tree.add_command(menu)

    def remove_menu(self, menu: str) -> Optional[ContextMenu]:
        """Removes a menu from this holder.

        .. note::

            This **does not** remove it from the tree.

        Parameters
        ----------
        menu: :class:`str`
            The context menu name to remove.

        Returns
        -------
        Optional[:class:`discord.app_commands.ContextMenu`]
            The context menu that was removed, or ``None``.
        """

        app_menu = find(lambda cm: cm.name == menu, self._context_menus)
        if app_menu is not None:
            self._context_menus.remove(app_menu)
            return app_menu
        return None

    def clear(self):
        """Clears all the current menus in this holder.

        .. note::

            This **does not** clear them from the tree.
        """
        self._context_menus.clear()
