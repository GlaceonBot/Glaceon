#/bin/bash
"true" '''\'
exec "$(dirname "$(readlink -f "$0")")"/venv/bin/python "$0" "$@"
'''
import argparse
import asyncio
import logging
import os
import pathlib
import traceback

import aiomysql
import discord
from discord.ext import commands
from dotenv import load_dotenv

import utils

# load the token to its variable

load_dotenv()
path = pathlib.PurePath()
TOKEN = os.getenv('TOKEN')

# Basic logging
argparser = argparse.ArgumentParser(description='Launch Glaceon discord bot')
argparser.add_argument('--loglevel', help='Set the logging level of Glaceon', dest='logginglevel', default='INFO')
argparser.add_argument('--logfile', help='Set the file for Glaceon to log to', dest='loggingfile',
                       default='glaceon.log')
argparser.add_argument('--status', help='Set Glaceon\'s status ', dest='botstatus', default=os.getenv('status'))
argparser.add_argument('--activity', help='Set Glaceon\'s activity', dest='botactivity', default=os.getenv('activity'))
flags, wrongflags = argparser.parse_known_args()
logginglevel = getattr(logging, flags.logginglevel.upper())
if flags.botstatus:
    botstatus = getattr(discord.Status, flags.botstatus.lower())
else:
    botstatus = discord.Status.online
if flags.botactivity:
    botactivity = getattr(discord.ActivityType, flags.botactivity.split()[0].lower())
    botdoing = flags.botactivity.split(' ', 1)[1]
else:
    botactivity = None
    botdoing = None

logging.basicConfig(level=logginglevel, filename=flags.loggingfile, filemode='w+', )
if wrongflags:
    logging.warning("An unrecognised flag was passed, skipping")
logging.info("Starting Jolteon.....")


# help command class :D
class Help(commands.MinimalHelpCommand):
    # actually sends the help
    # noinspection PyTypeChecker
    async def send_bot_help(self, mapping):
        permissions = self.context.channel.permissions_for(self.context.author)
        if not getattr(permissions, "manage_messages"):
            embed = discord.Embed(colour=glaceon.embedcolor, title="Help")
            prefix = await utils.prefixgetter(glaceon, self.context.message)
            embed.add_field(name="Commands",
                            value=f"You can use the tags by using `{prefix[0]}t <tag> [@mention]`\n\nYou can get a list of tags by running `{prefix[0]}tl`",
                            inline=False)
            prefix = await utils.prefixgetter(glaceon, self.context.message)
            embed.add_field(name="Prefix", value=f"`{prefix[0]}` or <@{self.context.me.id}>", inline=False)
            await self.get_destination().send(embed=embed)
        else:
            embed = discord.Embed(colour=glaceon.embedcolor, title="Help")
            embed.add_field(name="Commands",
                            value="You can see a list of my commands at [glaceon.xyz/help](https://glaceon.xyz/help/)!",
                            inline=False)
            prefix = await utils.prefixgetter(glaceon, self.context.message)
            embed.add_field(name="Prefix", value=f"`{prefix[0]}` or <@{self.context.me.id}>", inline=False)
            await self.get_destination().send(embed=embed)


# Sets the discord intents to all
intents = discord.Intents().all()
# defines the glaceon class as a bot with the prefixgetter prefix and case-insensitive commands
glaceon = commands.Bot(command_prefix=utils.prefixgetter, case_insensitive=True, intents=intents,
                       help_command=Help(command_attrs={'aliases': ['man']}),
                       activity=discord.Activity(type=botactivity, name=botdoing),
                       status=botstatus,
                       strip_after_prefix=True)
# global color for embeds
glaceon.embedcolor = 0xadd8e6

# global sql connection
loop = asyncio.get_event_loop()
glaceon.sql_server_pool = loop.run_until_complete(aiomysql.create_pool(host=os.getenv('SQLserverhost'),
                                                                       user=os.getenv('SQLusername'),
                                                                       password=os.getenv('SQLpassword'),
                                                                       db=os.getenv('SQLdatabase'),
                                                                       minsize=1,
                                                                       maxsize=100,
                                                                       autocommit=True))


@glaceon.event
async def on_ready():
    logging.info(f'Logged on as {glaceon.user.name}')  # Tells me if I'm running Glaceon or Eevee


# bot's list of cogs that need to be loaded up, they are all in different files and all do something different.
async def load_extentions():
    await glaceon.wait_until_ready()
    glaceon.coglist = []
    for x in pathlib.Path(path / 'cogs').rglob('*.py'):
        glaceon.coglist.append(str(x).replace('\\', '.').replace('/', '.').replace('.py', ''))
    # makes sure this file is the main file, and then loads extentions
    for extension in glaceon.coglist:
        try:
            glaceon.load_extension(extension)
        except Exception as error:
            bug_channel = glaceon.get_channel(int(os.getenv('ErrorChannel')))
            await bug_channel.send("There was a fatal error loading cog " + extension)
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


glaceon.loop.create_task(load_extentions())


# error handling is the same as SachiBotPy by @SmallPepperZ.
@glaceon.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
        # await ctx.message.add_reaction('<:CommandError:804193351758381086>')
        return

    elif isinstance(error, discord.ext.commands.errors.CommandNotFound) or ctx.command.hidden:
        return

    elif isinstance(error, discord.ext.commands.errors.NotOwner):
        await ctx.reply("Only bot administrators can do that.")
        return

    elif isinstance(error, discord.ext.commands.errors.MissingPermissions):
        await ctx.reply("You are not allowed to do that!")
        return

    elif isinstance(error, discord.ext.commands.errors.BotMissingPermissions):
        try:
            await ctx.reply("I do not have the requisite permissions to do that!")
        except discord.Forbidden:
            pass
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

    elif isinstance(error, discord.ext.commands.errors.CheckFailure):
        await ctx.send(error)

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
