# This example shows how to use the I18N feature with a JSON file.

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
        self.tree: discord.app_commands.CommandTree = discord.app_commands.CommandTree(self)
        self.translator: discord_tools.app_commands.i18n.Translator = discord_tools.app_commands.i18n.Translator()

    async def setup_hook(self) -> None:
        await self.tree.set_translator(self.translator)


client = CustomClient(...)
client.translator.load_translations('translations.json')

@client.tree.command(
    name='commands.echo.name',
    description='commands.echo.description',
)
async def echo(interaction: discord.Interaction, text: str) -> None:
    await interaction.response.send_message(text)


if __name__ == '__main__':
    client.run(...)
