"""
discord.ext.tools
~~~~~~~~~~~~~~~~~

Miscellaneous utils for Discord, treated as extensions.
"""

from typing import Tuple as __t__

__author__: str = "Developer-Anony"
__license__: str = "MIT"
__copyright__: str = "(c) Developer-Anony // 2023"
__version__: str = "1.0.0"

__all__: __t__[str] = (
    'Embed',
    'cooldown',
    'DataBase',
    'Bot'
)

from .embeds import Embed
from .cooldowns import cooldown
from .database import DataBase, Bot
