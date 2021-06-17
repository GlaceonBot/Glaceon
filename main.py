#!/home/Glaceon/Glaceon/venv/bin/python3
import logging
import os
import pathlib
import traceback
# load the token to its variable
from typing import List

import discord
import mysql.connector
from discord.ext import commands
from disputils import BotEmbedPaginator
from dotenv import load_dotenv

load_dotenv()
path = pathlib.PurePath()
TOKEN = os.getenv('TOKEN')

# Basic logging
logging.basicConfig(level=logging.INFO)


# function to return the prefix based on a message and a bot instance
async def prefixgetter(glaceon, message):
    # set default prefix
    default_prefix = "%"
    # list of pings so that they can be used as prefixes
    ping_prefixes = [glaceon.user.mention, glaceon.user.mention.replace('@', '@!')]
    # try to get the guild id. if there isn't one, then it's a DM and uses the default prefix.
    try:
        sid = message.guild.id
    except AttributeError:
        return default_prefix
    db = glaceon.sql_server_connection.cursor()
    # make sure everything is set up correctly
    db.execute('''CREATE TABLE IF NOT EXISTS prefixes
                   (serverid BIGINT, prefix TEXT)''')
    # find which prefix matches this specific server id
    db.execute(f'''SELECT prefix FROM prefixes WHERE serverid = {sid}''')
    # fetch the prefix
    custom_prefix = db.fetchone()
    # close connection
    db.close()
    # if the custom prefix exists, then send it back, otherwise return the default one
    if custom_prefix:
        return str(custom_prefix[0]), *ping_prefixes
    else:
        return default_prefix, *ping_prefixes


# help command class, mostly stolen so I don't fully understand it
class Help(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        # gets what the command should look like

        return '%s%s %s' % (self.clean_prefix, command.qualified_name, command.signature)

    # actually sends the help
    async def send_bot_help(self, mapping):
        # creates embed
        embeds: List[discord.Embed] = []
        for cog, commands in mapping.items():
            # sorts commands
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "System")
                # adds the needed categories for the commands
                embeds.append(discord.Embed(color=glaceon.embedcolor, title=f"Help - {cog_name}",
                                            description="\n".join(command_signatures)))
        ctx = self.context
        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()

        # for when it breaks

    async def send_error_message(self, error):
        embed = discord.Embed(color=glaceon.embedcolor, title="Error", value=error)
        channel = self.get_destination()
        await channel.send(embed=embed)


# Sets the discord intents to all
intents = discord.Intents().all()
# defines the glaceon class as a bot with the prefixgetter prefix and case-insensitive commands
glaceon = commands.Bot(command_prefix=prefixgetter, case_insensitive=True, intents=intents,
                       help_command=Help(),
                       activity=discord.Activity(type=discord.ActivityType.watching, name="out for you"),
                       status=discord.Status.do_not_disturb,
                       strip_after_prefix=True)

# global sql connection

glaceon.sql_server_connection = mysql.connector.connect(host=os.getenv('SQLserverhost'),
                                                            user=os.getenv('SQLusername'),
                                                            password=os.getenv('SQLpassword'),
                                                            database=os.getenv('SQLdatabase'))
# global color for embeds
glaceon.embedcolor = 0xadd8e6


@glaceon.event
async def on_ready():
    print(f'Logged on as {glaceon.user.name}')  # Tells me if I'm running Glaceon or Eevee


# bot's list of cogs that need to be loaded up, they are all in different files and all do something different.
glaceon.coglist = []
for x in pathlib.Path(path / 'cogs').rglob('*.py'):
    glaceon.coglist.append(str(x).replace('\\', '.').replace('/', '.').replace('.py', ''))
# makes sure this file is the main file, and then loads extentions
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

        traceback_text = ''.join(lines)
        n = 1988
        chunks = [traceback_text[i:i + n] for i in range(0, len(traceback_text), n)]
        # now we can send it to the us
        bug_channel = glaceon.get_channel(845453425722261515)
        for traceback_part in chunks:
            await bug_channel.send("```\n" + traceback_part + "\n```")
        await bug_channel.send(" Command being invoked: " + ctx.command.name)
        await ctx.send("Error!\n```" + str(
            error) + "```\nvalkyrie_pilot will be informed.  Most likely this is a bug, but check your syntax.",
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


@glaceon.command()
@commands.is_owner()
async def restart(ctx):
    await ctx.send("Restarting bot!")
    os.system("reload")


# runs the bot with a token.
glaceon.run(TOKEN)
