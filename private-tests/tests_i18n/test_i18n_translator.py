# Test for the discord_tools.app_commands.i18n submodule

import sys

RESERVED_ARGS = (
    'python',
    'test_i18n_translator.py',
)
POSSIBLE_TOKEN: str = ''

for arg in sys.argv:
    if arg in RESERVED_ARGS:
        continue
    POSSIBLE_TOKEN = arg

import discord
import discord_tools.app_commands.i18n

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(
    intents=intents,
)
tree = discord.app_commands.CommandTree(client)
translator = discord_tools.app_commands.i18n.Translator()

translator.load_translations(
    'test_yml_translations.yml',
)


@client.event
async def setup_hook() -> None:
    # Not recommended way but works anyways
    await tree.set_translator(translator)


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author.id not in (1097155878731395134,):
        return

    if not message.content.startswith('!'):
        return

    args: tuple[str, ...]
    command: str
    command, *args = message.content[1:].split(' ')

    if command == 'sync':
        if not args:
            synced = await tree.sync()
            await message.reply(
                f'{len(synced)} commands were synced globally!'
            )
            return

        if len(args) == 1:
            spec_or_guild = args[0]
            if spec_or_guild.isdigit():
                guild_id = int(spec_or_guild)
                synced = await tree.sync(
                    guild=discord.Object(guild_id),
                )
                await message.reply(
                    f'{len(synced)} commands were synced to {guild_id}!'
                )
                return

            if spec_or_guild == '*':
                if not message.guild:
                    await message.reply('Spec passed was current guild ("*"), but no guild was found!')
                    return
                synced = await tree.sync(guild=message.guild)
                await message.reply(
                    f'{len(synced)} commands were synced to the current guild!',
                )
                return
            elif spec_or_guild == '~':
                if not message.guild:
                    await message.reply('Spec passed was copy global to guild ("~"), but no guild was found!')
                    return
                tree.copy_global_to(guild=message.guild)
                synced = await tree.sync(guild=message.guild)
                await message.reply(
                    f'{len(synced)} commands were copied from global to current guild successfully!',
                )
                return
            else:
                await message.reply(f'"{spec_or_guild}" is not a valid spec!')
                return


@tree.command(
    auto_locale_strings=True,
    name="commands_help_name",
    description="commands_help_description",
)
async def help(interaction: discord.Interaction) -> None:
    content = await interaction.translate('responses.help.invoked')
    await interaction.response.send_message(content=content)


client.run(POSSIBLE_TOKEN)
