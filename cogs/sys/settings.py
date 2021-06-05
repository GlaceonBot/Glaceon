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
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx):
        """all the settings for Glaceon"""
        if ctx.invoked_subcommand is None:
            await ctx.send("You must specify a setting to change!")

    @settings.command()
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


def setup(glaceon):
    glaceon.add_cog(Settings(glaceon))
