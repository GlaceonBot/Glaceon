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
    async def settings(self, ctx):
        """all the settings for Glaceon"""
        if ctx.invoked_subcommand is None:
            await ctx.send("You must specify a setting to change!")

    @settings.command(aliases=['logging', 'logging_enabled'])
    async def enable_logging(self, ctx, isenabled: bool):
        """Enable Glaceon logging messages on your server."""
        if isenabled is True:
            isenabled = 1
            db = self.glaceon.sql_server_connection.cursor()
            db.execute("""CREATE TABLE IF NOT EXISTS settingslogging 
                (serverid BIGINT, setto BIGINT)""")
            db.execute(f'''SELECT serverid FROM settingslogging WHERE serverid = %s''',
                       (ctx.guild.id,))  # get the current setting
            if db.fetchone():
                db.execute("""UPDATE settingslogging SET setto = %s WHERE serverid = %s""",
                           (isenabled, ctx.guild.id))  # update the old setting
            else:
                db.execute("INSERT INTO settingslogging VALUES (%s,%s)",
                           (ctx.guild.id, isenabled))  # set the new setting
            self.glaceon.sql_server_connection.commit()  # say "yes i want to do this for sure"
            await ctx.send("Logging enabled!")
        else:
            isenabled = 0
            db = self.glaceon.sql_server_connection.cursor()
            db.execute("""CREATE TABLE IF NOT EXISTS settingslogging 
                (serverid BIGINT, setto BIGINT)""")
            db.execute(f'''SELECT serverid FROM settingslogging WHERE serverid = %s''',
                       (ctx.guild.id,))  # get the current setting
            if db.fetchone():
                db.execute("""UPDATE settingslogging SET setto = %s WHERE serverid = %s""",
                           (isenabled, ctx.guild.id))  # update the old setting
            else:
                db.execute("INSERT INTO settingslogging VALUES (%s,%s)",
                           (ctx.guild.id, isenabled))  # set the setting newly
            self.glaceon.sql_server_connection.commit()  # say "yes i want to do this for sure"
            await ctx.send("Logging disabled!")

    @settings.command()
    async def confirm_bans(self, ctx, isenabled: bool):
        """Enable the confirmation of ban messages via reactions"""
        if isenabled is True:
            isenabled = 1
            db = self.glaceon.sql_server_connection.cursor()
            db.execute("""CREATE TABLE IF NOT EXISTS settingsbanconfirm 
                (serverid BIGINT, setto BIGINT)""")
            db.execute(f'''SELECT serverid FROM settingsbanconfirm WHERE serverid = %s''',
                       (ctx.guild.id,))  # get the current setting
            if db.fetchone():
                db.execute("""UPDATE settingsbanconfirm SET setto = %s WHERE serverid = %s""",
                           (isenabled, ctx.guild.id))  # update the old setting
            else:
                db.execute("INSERT INTO settingsbanconfirm VALUES (%s,%s)",
                           (ctx.guild.id, isenabled))  # set the new setting
            self.glaceon.sql_server_connection.commit()  # say "yes i want to do this for sure"
            await ctx.send("Ban confirms enabled!")
        else:
            isenabled = 0
            db = self.glaceon.sql_server_connection.cursor()
            db.execute("""CREATE TABLE IF NOT EXISTS settingsbanconfirm 
                (serverid BIGINT, setto BIGINT)""")
            db.execute(f'''SELECT serverid FROM settingsbanconfirm WHERE serverid = %s''',
                       (ctx.guild.id,))  # get the current setting
            if db.fetchone():
                db.execute("""UPDATE settingsbanconfirm SET setto = %s WHERE serverid = %s""",
                           (isenabled, ctx.guild.id))  # update the old setting
            else:
                db.execute("INSERT INTO settingsbanconfirm VALUES (%s,%s)",
                           (ctx.guild.id, isenabled))  # set the setting newly
            self.glaceon.sql_server_connection.commit()  # say "yes i want to do this for sure"
            await ctx.send("Ban confirms disabled!")

    @settings.command()
    async def auto_dehoist(self, ctx, isenabled: bool):
        """Enable the system to remove hoisted users on join"""
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
                   (ctx.guild.id, "auto_dehoist"))  # get the current setting
        if db.fetchone():
            db.execute("""UPDATE settings SET setto = %s WHERE serverid = %s AND setting = %s""",
                       (isenabled, ctx.guild.id, "auto_dehoist"))  # update the old setting
        else:
            db.execute("INSERT INTO settings VALUES (%s,%s,%s)",
                       (ctx.guild.id, isenabled, "auto_dehoist"))  # set the new setting
        self.glaceon.sql_server_connection.commit()  # say "yes i want to do this for sure"
        await ctx.send(f"Dehoisting {enabledtext}!")


def setup(glaceon):
    glaceon.add_cog(Settings(glaceon))
