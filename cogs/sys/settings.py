import pathlib

import discord
from discord.ext import commands

# gets global path and embed color
import utils

path = pathlib.PurePath()


class Settings(discord.ext.commands.Cog):
    """Commands for your server's settings. """  # This is a docstring, used by the auto-help command to

    # describe this class.

    def __init__(self, glaceon):  # This is an init function. Runs when the class is constructed, and in this case
        # creates
        # a few variables.
        self.glaceon = glaceon  # making local global

    @commands.group()
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def settings(self, ctx):
        """All the settings for Glaceon"""
        if ctx.invoked_subcommand is None:
            await ctx.send("You must specify a setting to change!")

    @settings.command(aliases=['logging', 'logging_enabled'])
    async def enable_logging(self, ctx, isenabled: bool):
        """Enable Glaceon logging messages on your server."""
        if isenabled is True:
            isenabled = 1
            enabledtext = "enabled"
        else:
            isenabled = 0
            enabledtext = "disabled"
        connection = await self.glaceon.sql_server_pool.acquire()
        db = await connection.cursor()
        await db.execute(f'''SELECT serverid FROM settings WHERE serverid = %s AND setting = %s''',
                   (ctx.guild.id, "message_logging"))  # get the current setting
        if await db.fetchone():
            await db.execute('''UPDATE settings SET setto = %s WHERE serverid = %s AND setting = %s''',
                       (isenabled, ctx.guild.id, "message_logging"))  # update the old setting
        else:
            await db.execute("INSERT INTO settings VALUES (%s,%s,%s)",
                       (ctx.guild.id, isenabled, "message_logging"))  # set the new setting
        await db.close()
        connection.close()
        self.glaceon.sql_server_pool.release(connection)
        await ctx.reply(f"Message logging {enabledtext}!")

    @settings.command(aliases=['banconfirms', 'confirmbans', 'banconfirm'])
    async def confirm_bans(self, ctx, isenabled: bool):
        """Enable the confirmation of ban messages via reactions"""
        if isenabled is True:
            isenabled = 1
            enabledtext = "enabled"
        else:
            isenabled = 0
            enabledtext = "disabled"
        connection = await self.glaceon.sql_server_pool.acquire()
        db = await connection.cursor()
        await db.execute(f'''SELECT serverid FROM settings WHERE serverid = %s AND setting = %s''',
                   (ctx.guild.id, "ban_confirms"))  # get the current setting
        if await db.fetchone():
            await db.execute('''UPDATE settings SET setto = %s WHERE serverid = %s AND setting = %s''',
                       (isenabled, ctx.guild.id, "ban_confirms"))  # update the old setting
        else:
            await db.execute("INSERT INTO settings VALUES (%s,%s,%s)",
                       (ctx.guild.id, isenabled, "ban_confirms"))  # set the new setting
        await db.close()
        connection.close()
        self.glaceon.sql_server_pool.release(connection)
        await ctx.reply(f"Ban confirmations {enabledtext}!")

    @settings.command(aliases=['dehoist', 'dehoister', 'autodehoist'])
    async def auto_dehoist(self, ctx, isenabled: bool):
        """Enable the system to remove hoisted users on join"""
        if isenabled is True:
            isenabled = 1
            enabledtext = "enabled"
        else:
            isenabled = 0
            enabledtext = "disabled"
        # check bot's permissions
        permissions = ctx.channel.permissions_for(ctx.guild.me)
        # check if the bot is allowed to manage nicknames, and, if it isn't, let the user know
        if not getattr(permissions, "manage_nicknames") and isenabled == 1:
            await ctx.send("Dehoisting will not work unless the bot has the Manage Nicknames permission!")
            return
        connection = await self.glaceon.sql_server_pool.acquire()
        db = await connection.cursor()
        await db.execute(f'''SELECT serverid FROM settings WHERE serverid = %s AND setting = %s''',
                   (ctx.guild.id, "auto_dehoist"))  # get the current setting
        if await db.fetchone():
            await db.execute('''UPDATE settings SET setto = %s WHERE serverid = %s AND setting = %s''',
                       (isenabled, ctx.guild.id, "auto_dehoist"))  # update the old setting
        else:
            await db.execute("INSERT INTO settings VALUES (%s,%s,%s)",
                       (ctx.guild.id, isenabled, "auto_dehoist"))  # set the new setting
        await db.close()
        connection.close()
        self.glaceon.sql_server_pool.release(connection)
        await ctx.reply(f"Auto-dehoisting {enabledtext}!")

    @settings.command(aliases=['whitelist_invites', 'whitelist_enable'])
    async def whitelisted_invites(self, ctx, isenabled: bool):
        """Enable the system to autodelete whitelisted invites"""
        if isenabled is True:
            isenabled = 1
            enabledtext = "enabled"
        else:
            isenabled = 0
            enabledtext = "disabled"
        connection = await self.glaceon.sql_server_pool.acquire()
        db = await connection.cursor()
        await db.execute(f'''SELECT serverid FROM settings WHERE serverid = %s AND setting = %s''',
                   (ctx.guild.id, "whitelisted_invites"))  # get the current setting
        if await db.fetchone():
            await db.execute('''UPDATE settings SET setto = %s WHERE serverid = %s AND setting = %s''',
                       (isenabled, ctx.guild.id, "whitelisted_invites"))  # update the old setting
        else:
            await db.execute("INSERT INTO settings VALUES (%s,%s,%s)",
                       (ctx.guild.id, isenabled, "whitelisted_invites"))  # set the new setting
        await db.close()
        connection.close()
        self.glaceon.sql_server_pool.release(connection)
        await ctx.reply(f"Invite moderation {enabledtext}!")

    @settings.command(aliases=['whitelist_invite', 'whitelist_add', 'add_whitelist_invite'])
    async def add_whitelisted_invite(self, ctx, whitelist_guild_id: int):
        """Add an invite to the invite whitelist"""
        connection = await self.glaceon.sql_server_pool.acquire()
        db = await connection.cursor()
        await db.execute('''INSERT INTO whitelisted_invites VALUES (%s, %s)''', (ctx.guild.id, whitelist_guild_id))
        await db.close()
        connection.close()
        self.glaceon.sql_server_pool.release(connection)
        await ctx.reply(f"Added whitelisted invite for guild {whitelist_guild_id}!")

    @settings.command(aliases=['dewhitelist_invite', 'whitelist_del', 'whitelist_rem', 'whitelist_remove'])
    async def remove_whitelisted_invite(self, ctx, whitelist_guild_id: int):
        """Remove an invite from the invite whitelist"""
        connection = await self.glaceon.sql_server_pool.acquire()
        db = await connection.cursor()
        await db.execute('''DELETE FROM whitelisted_invites WHERE hostguild = %s AND inviteguild = %s''',
                   (ctx.guild.id, whitelist_guild_id))
        await db.close()
        connection.close()
        self.glaceon.sql_server_pool.release(connection)
        await ctx.reply(f"Removed whitelisted invite for guild {whitelist_guild_id}!")

    @settings.command()
    async def disable(self, ctx, command):
        connection = await self.glaceon.sql_server_pool.acquire()
        db = await connection.cursor()
        all_commands = []
        for x in self.glaceon.walk_commands():
            all_commands.append(x.qualified_name)
        if command not in all_commands:
            await ctx.send("That is not a valid command.")
            return
        await db.execute('''DELETE FROM disabled_commands WHERE guildid = %s AND command = %s''',
                         (ctx.guild.id, command))
        await db.execute('''INSERT INTO disabled_commands VALUES (%s, %s, %s)''', (ctx.guild.id, command, 0))
        await db.close()
        connection.close()
        self.glaceon.sql_server_pool.release(connection)
        await ctx.reply(f"Command {command} disabled!")

    @settings.command()
    async def enable(self, ctx, command):
        connection = await self.glaceon.sql_server_pool.acquire()
        db = await connection.cursor()
        all_commands = []
        for x in self.glaceon.walk_commands():
            all_commands.append(x.qualified_name)
        if command not in all_commands:
            await ctx.send("That is not a valid command.")
            return
        await db.execute('''DELETE FROM disabled_commands WHERE guildid = %s AND command = %s''', (ctx.guild.id, command))
        await db.execute('''INSERT INTO disabled_commands VALUES (%s, %s, %s)''', (ctx.guild.id, command, 1))
        await db.close()
        connection.close()
        self.glaceon.sql_server_pool.release(connection)
        await ctx.reply(f"Command {command} enabled!")


def setup(glaceon):
    glaceon.add_cog(Settings(glaceon))
