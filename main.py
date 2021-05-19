#!/home/gxhut/Glaceon/venv/bin/python3
import traceback
import pathlib
import aiosqlite
import discord
import os
from discord.ext import commands
from dotenv import load_dotenv


# load the token to its variable
load_dotenv()
path = pathlib.PurePath()
TOKEN = os.getenv('TOKEN')


# function to return the prefix based on a message and a bot instance
async def prefixgetter(_, message):
    # set default prefix
    default_prefix = "%"
    # try to get the guild id. if there isn't one, then it's a DM and uses the default prefix.
    try:
        sid = message.guild.id
    except AttributeError:
        return default_prefix
    # connect to the sqlite database for prefixes
    db = await aiosqlite.connect(path / 'system/data.db')
    # make sure everything is set up correctly
    await db.execute('''CREATE TABLE IF NOT EXISTS prefixes
                   (serverid INTEGER, prefix TEXT)''')
    # find which prefix matches this specific server id
    cur = await db.execute(f'''SELECT prefix FROM prefixes WHERE serverid = {sid}''')
    # fetch the prefix
    custom_prefix = await cur.fetchone()
    # close connection
    await db.close()
    # if the custom prefix exists, then send it back, otherwise return the default one
    if custom_prefix:
        return str(custom_prefix[0])
    else:
        return default_prefix


# help command class, mostly stolen so I don't fully understand it
class Help(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        # gets what the command should look like
        return '%s%s %s' % (self.clean_prefix, command.qualified_name, command.signature)

    # actually sends the help
    async def send_bot_help(self, mapping):
        # creates embed
        embed = discord.Embed(title="Help")
        for cog, commands in mapping.items():
            # sorts commands
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "System")
                # adds the needed categories for the commands
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)

        # for when it breaks
    async def send_error_message(self, error):
        embed = discord.Embed(title="Error", value=error)
        channel = self.get_destination()
        await channel.send(embed=embed)


# Sets the discord intents to all
intents = discord.Intents().all()
# defines the glaceon class as an autoshardedbot with the prefixgetter prefix and case-insensitive commands
glaceon = commands.AutoShardedBot(command_prefix=prefixgetter, case_insensitive=True, intents=intents, help_command=Help(), activity=discord.Activity(type=discord.ActivityType.watching, name="glaceon.xyz"), status=discord.Status.do_not_disturb)
# global color for embeds
embedcolor = 0xadd8e6


@glaceon.event
async def on_ready():
    print(f'Logged on as {glaceon.user.name}')  # Tells me if I'm running Glaceon or Eevee


# this function changes the message so that the pings will also work as a prefix
@glaceon.event
async def on_message(message):
    # gets the string for the mention
    bot_mention_str = glaceon.user.mention.replace('@', '@!') + ' '
    # gets length to compare things
    bot_mention_len = len(bot_mention_str)
    # magic
    if message.content[:bot_mention_len] == bot_mention_str:
        # gets the prefix and checks what it is, then subs in the prefix for the ping
        message.content = await prefixgetter(glaceon, message) + message.content[bot_mention_len:]
        await glaceon.process_commands(message)
    else:
        await glaceon.process_commands(message)


# bot's list of cogs that need to be loaded up, they are all in different files and all do something different.
glaceon.coglist = []
for x in pathlib.Path(path / 'cogs').rglob('*.py'):
    glaceon.coglist.append(str(x).replace('\\', '.').replace('/', '.').replace('.py', ''))

# makes sure this file is the main file, and then loads extentions
if __name__ == '__main__':
    for extension in glaceon.coglist:
        glaceon.load_extension(extension)


# error handling is the same as SachiBotPy by @SmallPepperZ.
@glaceon.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
        # await ctx.message.add_reaction('<:CommandError:804193351758381086>')
        return

    elif isinstance(error, discord.ext.commands.errors.CommandNotFound) or ctx.command.hidden:
        return

    elif isinstance(error, discord.ext.commands.errors.NotOwner):
        await ctx.reply("lol only valk can do that")
        return

    elif isinstance(error, discord.ext.commands.errors.MissingPermissions):
        await ctx.reply("You are not allowed to do that!")
        return

    elif isinstance(error, discord.ext.commands.errors.BotMissingPermissions):
        await ctx.reply("I do not have the requisite permissions to do that!")
        return

    elif isinstance(error, discord.ext.commands.errors.MissingRole):
        await ctx.send("I am missing the role to do that!")
        return

    elif isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
        if str(error.cooldown.type.name) != "default":
            cooldowntype = f'per {error.cooldown.type.name}'

        else:
            cooldowntype = 'global'
        await ctx.reply(
            f"This command is on a {round(error.cooldown.per, 0)} second {cooldowntype} cooldown.\n"
            f"Wait {round(error.retry_after, 1)} seconds, and try again.",
            delete_after=min(10, error.retry_after))
        return

    elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.reply(f"Missing required argument!\nUsage:`{ctx.command.signature}`", delete_after=30)
        return

    elif isinstance(error, discord.ext.commands.errors.BadArgument):
        await ctx.reply(f"Invalid argument!\nUsage:`{ctx.command.signature}`", delete_after=30)
        return

    elif isinstance(error, discord.ext.commands.errors.NoPrivateMessage):
        await ctx.reply("That can only be used in servers, not DMs!")
        return

    else:
        # Send user a message
        # get data from exception
        etype = type(error)
        trace = error.__traceback__

        # 'traceback' is the stdlib module, `import traceback`.
        lines = traceback.format_exception(etype, error, trace)

        # format_exception returns a list with line breaks embedded in the lines, so let's just stitch the elements together
        traceback_text = ''.join(lines)

        # now we can send it to the user
        await ctx.send("Error:\n```" + str(
            traceback_text) + "```\nvalkyrie_pilot will be informed.  Most likely this is a bug, but check your syntax.",
                       delete_after=30)


# my reload command, so i can reload the cogs without restarting the bot
@glaceon.command()
# only i can do this
@commands.is_owner()
async def reload(ctx):
    """Owner only, for debug."""
    # for everything in that cog list, it unloads and then loads the extention.
    for ext in glaceon.coglist:
        glaceon.unload_extension(ext)
        glaceon.load_extension(ext)
    await ctx.send("Reloaded cogs!")

# runs the bot with a token.
glaceon.run(TOKEN)
