import pathlib

import discord
from discord.ext import commands

# gets global path and embed color
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
        """all the settings for Glaceon"""
        if ctx.invoked_subcommand is None:
            await ctx.send("You must specify a setting to change!")

    @settings.command(aliases=['logging', 'logging_enabled'])
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def enable_logging(self, ctx, isenabled: bool):
        """Enable Glaceon logging messages on your server."""
        if isenabled is True:
            isenabled = 1
            enabledtext = "enabled"
        else:
            isenabled = 0
            enabledtext = "disabled"
        db = self.glaceon.sql_server_connection.cursor()
        db.execute("""CREATE TABLE IF NOT EXISTS settings 
                (serverid BIGINT, setto BIGINT, setting TEXT)""")
        db.execute(f'''SELECT serverid FROM settings WHERE serverid = %s AND setting = %s''',
                   (ctx.guild.id, "message_logging"))  # get the current setting
        if db.fetchone():
            db.execute("""UPDATE settings SET setto = %s WHERE serverid = %s AND setting = %s""",
                       (isenabled, ctx.guild.id, "message_logging"))  # update the old setting
        else:
            db.execute("INSERT INTO settings VALUES (%s,%s,%s)",
                       (ctx.guild.id, isenabled, "message_logging"))  # set the new setting
        self.glaceon.sql_server_connection.commit()  # say "yes i want to do this for sure"
        await ctx.send(f"Message logging {enabledtext}!")

    @settings.command(aliases=['banconfirms', 'confirmbans', 'banconfirm'])
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def confirm_bans(self, ctx, isenabled: bool):
        """Enable the confirmation of ban messages via reactions"""
        if isenabled is True:
            isenabled = 1
            enabledtext = "enabled"
        else:
            isenabled = 0
            enabledtext = "disabled"
        db = self.glaceon.sql_server_connection.cursor()
        db.execute("""CREATE TABLE IF NOT EXISTS settings 
                (serverid BIGINT, setto BIGINT, setting TEXT)""")
        db.execute(f'''SELECT serverid FROM settings WHERE serverid = %s AND setting = %s''',
                   (ctx.guild.id, "ban_confirms"))  # get the current setting
        if db.fetchone():
            db.execute("""UPDATE settings SET setto = %s WHERE serverid = %s AND setting = %s""",
                       (isenabled, ctx.guild.id, "ban_confirms"))  # update the old setting
        else:
            db.execute("INSERT INTO settings VALUES (%s,%s,%s)",
                       (ctx.guild.id, isenabled, "ban_confirms"))  # set the new setting
        self.glaceon.sql_server_connection.commit()  # say "yes i want to do this for sure"
        await ctx.send(f"Ban confirmations {enabledtext}!")

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
        db = self.glaceon.sql_server_connection.cursor()
        db.execute("""CREATE TABLE IF NOT EXISTS settings 
                (serverid BIGINT, setto BIGINT, setting TEXT)""")
        db.execute(f'''SELECT serverid FROM settings WHERE serverid = %s AND setting = %s''',
                   (ctx.guild.id, "auto_dehoist"))  # get the current setting
        if db.fetchone():
            db.execute("""UPDATE settings SET setto = %s WHERE serverid = %s AND setting = %s""",
                       (isenabled, ctx.guild.id, "auto_dehoist"))  # update the old setting
        else:
            db.execute("INSERT INTO settings VALUES (%s,%s,%s)",
                       (ctx.guild.id, isenabled, "auto_dehoist"))  # set the new setting
        self.glaceon.sql_server_connection.commit()  # say "yes i want to do this for sure"
        await ctx.send(f"Auto-dehoisting {enabledtext}!")


def setup(glaceon):
    glaceon.add_cog(Settings(glaceon))
