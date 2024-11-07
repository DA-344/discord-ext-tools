# This example shows how to use the I18N feature.

import discord
import discord_tools


class CustomClient(discord.Client):
    # We override client to have our own setup_hook
    # and attributes. This works the same with discord.AutoShardedClient and
    # commands.(AutoSharded)Bot

    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.tree: discord.app_commands.CommandTree = discord.app_commands.CommandTree(
            self
        )
        self.translator: discord_tools.app_commands.i18n.Translator = (
            discord_tools.app_commands.i18n.Translator()
        )

    async def setup_hook(self) -> None:
        await self.tree.set_translator(self.translator)


client = CustomClient(...)
client.translator.load_translations("path/to/the/translations")
# Example translations show how the structure of each file should be
# .po and .mo files should be loaded independently and take the locale kwarg, this means, if you want to load
# the 3 po example files you need to call "load_translations" 3 times.
# There are no examples for .mo files as those are binary encoded .po files, and this library treats them
# as the same.


@client.tree.command(
    name="commands_echo_name",
    description="commands_echo_description",
    # auto_locale_strings=True,  # If this is "True" then the name and description strings are not required to be
    # wrapped around locale_str
)
async def echo(interaction: discord.Interaction, text: str) -> None:
    await interaction.response.send_message(text)


if __name__ == "__main__":
    client.run("TOKEN")
