"""
discord.ext.tools.database
~~~~~~~~~~~~~~~~~~~~~~~~~~

Extesion to easily manage bots databases.

This uses the :module:`tortoise-orm` module
to connect and interact with your DB, so please
install it.
"""

from __future__ import annotations

import logging, asyncio

from discord import app_commands
from discord.ext.commands.help import HelpCommand
from discord.ext.commands.bot import Bot as BotBase, PrefixType
from discord.app_commands.tree import CommandTree
from discord.flags import Intents

try:
    import tortoise
except ImportError:
    raise UserWarning('cannot use ext.tools.database if tortoise-orm isn\'t installed, this module is required for the database management. Please install it using \'python -m pip install tortoise-orm\'')

from typing import Any, List, Optional

class DataBase:
    r"""A class that represents a new database connection.
    
    Parameters
    ----------
    url: :class:`str`
        The URL for the database.
        Currently, only SQLite, PostgreSQL, MySQL / MariaDB and Microsoft SQL Server are supported.
        
        This follows this syntax:
        
        >>> `db_type://url`

        DB Types:
        ~~~~~~~~~

        ``sqlite``:
            Typically in the form of ``sqlite://DB_FILE`` So if the ``DB_FILE``
            is “/data/db.sqlite3” then the string will be ``sqlite:///data/db.sqlite`` (note the three /’s)

        ``postgres``:
            Using ``asyncpg``: Typically in the form of ``postgres://postgres:pass@db.host:5432/somedb``

            Or specifically ``asyncpg``/``psycopg`` using:

            ``psycopg``: ``psycopg://postgres:pass@db.host:5432/somedb``

            ``asyncpg``: ``asyncpg://postgres:pass@db.host:5432/somedb``

        ``mysql``:
            Typically in the form of ``mysql://myuser:mypass@db.host:3306/somedb``

        ``mssql``:
            Typically in the form of ``mssql://myuser:mypass@db.host:1433/somedb?driver=the odbc driver``

    models: List[:class:`str`]
        The list of path dirs to the Python files that contains all the models (tables) for this database.

        This models are made using the `tortoise.models.Model` object:

        ```py
        from tortoise.models import Model
        from tortoise.fields import ... # Import the needed fields (Text, Int, BigInt, SmallInt,...)

        class Guild(Model): # should be a subclass of Model
            # you must declare all table rows as follows
            id = BigIntField(pk=True) # pk kwargs is used to mark a field as primary key
            ...                       # all fields have a name ended with `Field`, i.e.: TextField
        ```

    Example
    -------
    ```py
    from discord.ext.commands import Bot
    from discord.ext.tools import DataBase

    # EXAMPLE USING THE ext.commands BOT
    # Create a Bot instance
    bot = Bot(...)

    # Create an instance of the DataBase class
    # Database URL is an SQLite-based file named 'base.db'
    # Tables/models for this database are specified in 'my_tables.py'
    # we remove the '.py' extension.
    database = DataBase('sqlite://base.db', ['my_tables'])

    # Set a new attribute to the Bot class named 'database'
    bot.database = database

    # Now, we can access the database connection wherever we want.

    # EXAMPLE USING THE ext.tools BOT
    from discord.ext.tools import Bot, DataBase

    bot = Bot(..., database=DataBase(...))

    bot.run(TOKEN)
    # This runs both the bot and the connection to the DB
    ```
    """
    
    def __init__(self, url: str, models: List[str], /) -> None:
        self.url: str = url
        self.models: List[str] = models

    async def connect(self, *, safe_schemas: bool = False) -> None:
        r"""|coro|

        Starts a connection to the database.

        Parameters
        ----------
        safe_schemas: :class:`bool`
            If the modules loaded should be safely edited.
        """
        await tortoise.Tortoise.init(db_url=self.url, modules={'models': self.models})

        await tortoise.Tortoise.generate_schemas(safe=safe_schemas)

class Bot(BotBase):
    r"""A class that represents a new bot.

    This inherits from :class:`.ext.commands.bot.Bot`, so it has all its functionalities.
    """

    def __init__(self, command_prefix: PrefixType, *, help_command: HelpCommand | None = ..., tree_cls: type[CommandTree[Any]] = app_commands.CommandTree, description: str | None = None, intents: Intents, database: Optional[DataBase] = None, **options: Any) -> None:
        super().__init__(command_prefix, help_command=help_command, tree_cls=tree_cls, description=description, intents=intents, **options)

        self._db: Optional[DataBase] = database

    @property
    def database(self) -> DataBase:
        """Returns the database linked to this bot"""
        return self._db
    
    @database.setter
    def database(self, db: Any) -> None:
        if not isinstance(db, DataBase):
            raise ValueError(f'cannot set a {type(db).__name__} class as a database')
        
        self._db = db

    @database.deleter
    def database(self) -> None:
        self._db = None

    db = database

    def run(self, token: str, *, reconnect: bool = True, log_handler: logging.Handler | None = ..., log_formatter: logging.Formatter = ..., log_level: int = ..., root_logger: bool = False) -> None:
        t1 = asyncio.create_task(self.db.connect())
        t2 = asyncio.create_task(super().run(token, reconnect=reconnect, log_handler=log_handler, log_formatter=log_formatter, log_level=log_level, root_logger=root_logger))

        asyncio.run(asyncio.gather(t1, t2))
