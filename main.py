#!/usr/bin/python3
import pathlib
import sqlite3

import discord
from discord.ext import commands
from discord.ext.commands.errors import *

path = pathlib.PurePath()
with open(path / 'system/token.txt', 'r') as file:
    TOKEN = file.read()


def prefixgetter(_, message):
    sid = message.guild.id
    prefixes = sqlite3.connect(path / 'system/data.db')
    cur = prefixes.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS prefixes
                   (serverid INTEGER, prefix TEXT)''')
    cur.execute(f'''SELECT prefix FROM prefixes WHERE serverid = {sid}''')
    default_prefix = "%"
    custom_prefix = cur.fetchone()
    prefixes.close()
    if custom_prefix:
        return str(custom_prefix[0])
    else:
        return default_prefix


class Help(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        return '%s%s %s' % (self.clean_prefix, command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help")
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "System")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_error_message(self, error):
        embed = discord.Embed(title="Error", value=error)
        channel = self.get_destination()
        await channel.send(embed=embed)


intents = discord.Intents().all()
glaceon = commands.AutoShardedBot(command_prefix=prefixgetter, case_insensitive=True, intents=intents)
glaceon.help_command = Help()
embedcolor = 0xadd8e6


@glaceon.event
async def on_ready():
    print(f'Logged on as {glaceon.user.name}')
    await glaceon.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                            name="the world go by"),
                                  status=discord.Status.do_not_disturb)


@glaceon.event
async def on_message(message):
    if "<@!808149899182342145>" in message.content or "<@808149899182342145>" in message.content:
        await message.channel.send(f'`{glaceon.command_prefix(glaceon, message)}` is my prefix!')
    await glaceon.process_commands(message)


glaceon.coglist = ['cogs.sys.logger',
                   'cogs.manual.modsend',
                   'cogs.manual.modcommands',
                   'cogs.manual.helpercommands',
                   'cogs.sys.system',
                   'cogs.sys.info',
                   'cogs.auto.antispam']

if __name__ == '__main__':
    for extension in glaceon.coglist:
        glaceon.load_extension(extension)


@glaceon.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
        # await ctx.message.add_reaction('<:CommandError:804193351758381086>')
        return

    elif isinstance(error, CommandNotFound) or ctx.command.hidden:
        return

    elif isinstance(error, NotOwner):
        await ctx.reply("lol only valk can do that")
        return

    elif isinstance(error, MissingPermissions):
        await ctx.reply("You are not allowed to do that!")
        return

    elif isinstance(error, BotMissingPermissions):
        await ctx.reply("I do not have the requisite permissions to do that!")
        return

    elif isinstance(error, MissingRole):
        await ctx.send("I am missing the role to do that!")
        return

    elif isinstance(error, CommandOnCooldown):
        if str(error.cooldown.type.name) != "default":
            cooldowntype = f'per {error.cooldown.type.name}'

        else:
            cooldowntype = 'global'
        await ctx.reply(
            f"This command is on a {round(error.cooldown.per, 0)} second {cooldowntype} cooldown.\n"
            f"Wait {round(error.retry_after, 1)} seconds, and try again.",
            delete_after=min(10, error.retry_after))
        return

    elif isinstance(error, MissingRequiredArgument):
        await ctx.reply(f"Missing required argument!\nUsage:`{ctx.command.signature}`", delete_after=30)
        return

    elif isinstance(error, BadArgument):
        await ctx.reply(f"Invalid argument!\nUsage:`{ctx.command.signature}`", delete_after=30)
        return

    elif isinstance(error, NoPrivateMessage):
        await ctx.reply("That can only be used in servers, not DMs!")
        return

    else:
        # Send user a message
        await ctx.send("Error:\n```" + str(
            error) + "```\nvalkyrie_pilot will be informed.  Most likley this is a bug, but check your syntax.",
                       delete_after=60)


@glaceon.command()
@commands.is_owner()
async def reload(ctx):
    """Owner only, for debug."""
    for ext in glaceon.coglist:
        glaceon.unload_extension(ext)
        print("reloading " + str(ext))
        glaceon.load_extension(ext)
    await ctx.send("Reloaded cogs!")


glaceon.run(TOKEN)
