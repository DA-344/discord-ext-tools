# This examples shows how to use the discord_tools.app_commands.max_concurrency
# check decorator. With comments so you know what happens in each part.

import asyncio
import discord
import discord_tools


intents = discord.Intents.default()
# You will need to enable this intent on the discord developer portal!
intents.members = True

# We create our client with the provided intents
client = discord.Client(intents=intents)

# and then our app commands tree
client.tree = tree = discord.app_commands.CommandTree(client)


# we define a command
@tree.command()
# and we apply our max_concurrency decorator, limiting to 1 usage per user
@discord_tools.app_commands.max_concurrency(1, per=discord_tools.app_commands.BucketType.user)
async def some_long_operation(interaction: discord.Interaction) -> None:
    await interaction.response.defer()  # we defer so we can respond in more than 3 seconds
    await asyncio.sleep(10)  # simulate some long operation: db calls, web requests, etc.
    await interaction.followup.send('Completed!')  # we tell the user the operation has finished


# we now define the error handling for our command
# this can be done in different ways, but in this case, we will use
# the @.error decorator
@some_long_operation.error
async def some_long_operation_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    # we now check if our error is the one that max_concurrency raises
    if isinstance(error, discord_tools.app_commands.MaxConcurrencyReached):
        # now we tell the user that they have reached maximum concurrency in X bucket

        # if the interaction has not been responded, we respond to it
        if not interaction.response.is_done():
            await interaction.response.send_message(
                f'You have reached the {error.number} per {error.per.name} command usage',
                ephemeral=True,
            )
        # if it has, then we send a followup
        else:
            await interaction.followup.send(
                f'You have reached the {error.number} per {error.per.name} command usage',
                ephemeral=True,
            )
    else:
        # if the error catched was not the one we expected, we can simply re-raise it
        raise error
