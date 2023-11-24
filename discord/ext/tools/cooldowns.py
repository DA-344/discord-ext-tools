"""
discord.ext.tools.cooldowns
~~~~~~~~~~~~~~~~~~~~~~~~~

Cooldown utils for explicit requirements.
"""
from __future__ import annotations

from discord.role import Role

from discord.ext.commands.context import Context
from discord.ext.commands.cooldowns import BucketType, Cooldown, DynamicCooldownMapping
from discord.ext.commands.core import Command
from discord.ext.commands._types import CoroFunc

from typing import Callable, List, Optional, Union

def cooldown(rate: int, per: float, *, bucket: BucketType = BucketType.member, bypass_owners: bool = False, has_any_role: Optional[List[Role]] = None, hasnt_any_role: Optional[List[Role]] = None) -> Callable[..., Command]:
    """A decorator that adds a advanced cooldown to a :class:`.Command`

    This is the same as :func:`.dynamic_cooldown` but, it is just this
    decorator, that has special keyword arguments to make the cooldown
    creation as user-friendly as possible.

    Parameters
    ----------
    rate: int
        The number of times a command can be used before triggering a cooldown.
    per: int
        The amount of seconds to wait for a cooldown when it's been triggered
    bucket: :class:`.BucketType`
        The type of cooldown to have.
    
    Keyword parameters
    ------------------
    bypass_owners: bool
        If the cooldown should bypass owners.
    has_any_role: Optional[List[:class:`.Role`]]
        If the cooldown should bypass users WITH ANY of this roles.
    hasnt_any_role: Optional[List[:class:`.Role`]]
        If the cooldown should bypass users THAT DOESN'T HAVE ANY of this roles.
    """
    
    def mapping(ctx: Context) -> bool:
        if bypass_owners:
            if ctx.bot.is_owner(ctx.author):
                return None

        if ctx.guild:            
            if has_any_role:
                for role in has_any_role:
                    if role in ctx.author.roles:
                        return None

            if hasnt_any_role:
                for role in hasnt_any_role:
                    if role in ctx.author.roles:
                        break
                    

        else:
            if any((has_any_role != None, hasnt_any_role != None)):
                raise ValueError('cannot user has_any_role or hasnt_any_role kwargs when command is invoked outside a guild')
            
        return Cooldown(rate, per)
    
    def decorator(cmd: Union[Command, CoroFunc]) -> Union[Command, CoroFunc]:
        if isinstance(cmd, Command):
            cmd._buckets = DynamicCooldownMapping(mapping, bucket)

        else:
            cmd.__commands_cooldown__ = DynamicCooldownMapping(mapping, bucket)

        return cmd
    
    return decorator
