"""
discord.ext.tools.embeds
~~~~~~~~~~~~~~~~~~~~~~~~

Tools for embeds and some parsers to create embeds a user-friendly way.
"""
from __future__ import annotations

import discord
from typing import List


class Embed(discord.Embed):
    """
    An embed class that inherits from `.Embed`.

    To initialize this, it is the same way as a normal embed.
    """

    @classmethod
    def from_message(cls, message: discord.Message) -> Embed:
        """
        Creates an embed using the message content.

        This uses the messages new lines to create title,
        description and fields.

        Example message:

        ```md
        This would be the embed title!
        This would be the embed description!
        This a new field name...
        and the same new field value...
        ```

        That would be the same as hard-coding...:

        ```py
        embed = Embed(title='This would be the embed title!', description='This would be the embed description!')
        embed.add_field(name='This a new field name...', value='and the same new field value')
        ```

        Parameters
        ----------
        message: discord.Message
            The message that you want to create an embed for.

        Returns
        -------
        A new Embed class based on the message.
        """

        clean_content = message.content

        if clean_content == "":
            raise ValueError("cannot initialize an embed by an empty message")

        if "\n" in clean_content:
            contents: List[str] = clean_content.splitlines(keepends=False)

        else:
            contents: List[str] = [
                clean_content,
            ]

        done_lines: List[int] = []
        embed: cls = cls()
        for index, line in enumerate(contents):
            if index == 0:
                embed.title = line

            if index == 1:
                embed.description = line

            else:
                if index not in done_lines and index + 1 not in done_lines:
                    embed.add_field(name=line, value=contents[index + 1])
                    done_lines.extend([index, index + 1])
                    # NOTE: This appends the done lines index so no lines, even value, are
                    # repeated.

        return embed
