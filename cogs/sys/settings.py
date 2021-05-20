import pathlib

import mysql.connector
import discord
from discord.ext import commands

# gets global path and embed color
path = pathlib.PurePath()
embedcolor = 0xadd8e6


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
        if ctx.invoked_subcommand is None:
            await ctx.send("You must specify a setting to change!")

    @settings.command()
    async def enable_logging(self, ctx, isenabled: bool):
        if isenabled is True:
            isenabled = 1
            async with aiosqlite.connect(path / "system/data.db") as db:
                await db.execute("""CREATE TABLE IF NOT EXISTS settingslogging 
                (serverid INTEGER, setto INTEGER)""")
                dataline = await db.execute(f'''SELECT serverid FROM settingslogging WHERE serverid = ?''',
                                            (ctx.guild.id,))  # get the current setting
                if await dataline.fetchone() is not None:
                    await db.execute("""UPDATE settingslogging SET setto = ? WHERE serverid = ?""",
                                     (isenabled, ctx.guild.id))  # update the old setting
                else:
                    await db.execute("INSERT INTO settingslogging VALUES (?,?)",
                                     (ctx.guild.id, isenabled))  # set the new setting
                await db.commit()  # say "yes i want to do this for sure"
                await ctx.send("Logging enabled!")
        else:
            isenabled = 0
            async with aiosqlite.connect(path / "system/data.db") as db:
                await db.execute("""CREATE TABLE IF NOT EXISTS settingslogging 
                (serverid INTEGER, setto INTEGER)""")
                dataline = await db.execute(f'''SELECT serverid FROM settingslogging WHERE serverid = ?''',
                                            (ctx.guild.id,))  # get the current setting
                if await dataline.fetchone() is not None:
                    await db.execute("""UPDATE settingslogging SET setto = ? WHERE serverid = ?""",
                                     (isenabled, ctx.guild.id))  # update the old setting
                else:
                    await db.execute("INSERT INTO settingslogging VALUES (?,?)",
                                     (ctx.guild.id, isenabled))  # set the setting newly
                await db.commit()  # say "yes i want to do this for sure"
                await ctx.send("Logging disabled!")

    @settings.command()
    async def confirm_bans(self, ctx, isenabled: bool):
        if isenabled is True:
            isenabled = 1
            async with aiosqlite.connect(path / "system/data.db") as db:
                await db.execute("""CREATE TABLE IF NOT EXISTS settingsbanconfirm 
                (serverid INTEGER, setto INTEGER)""")
                dataline = await db.execute(f'''SELECT serverid FROM settingsbanconfirm WHERE serverid = ?''',
                                            (ctx.guild.id,))  # get the current setting
                if await dataline.fetchone() is not None:
                    await db.execute("""UPDATE settingsbanconfirm SET setto = ? WHERE serverid = ?""",
                                     (isenabled, ctx.guild.id))  # update the old setting
                else:
                    await db.execute("INSERT INTO settingsbanconfirm VALUES (?,?)",
                                     (ctx.guild.id, isenabled))  # set the new setting
                await db.commit()  # say "yes i want to do this for sure"
                await ctx.send("Ban confirms enabled!")
        else:
            isenabled = 0
            async with aiosqlite.connect(path / "system/data.db") as db:
                await db.execute("""CREATE TABLE IF NOT EXISTS settingsbanconfirm 
                (serverid INTEGER, setto INTEGER)""")
                dataline = await db.execute(f'''SELECT serverid FROM settingsbanconfirm WHERE serverid = ?''',
                                            (ctx.guild.id,))  # get the current setting
                if await dataline.fetchone() is not None:
                    await db.execute("""UPDATE settingsbanconfirm SET setto = ? WHERE serverid = ?""",
                                     (isenabled, ctx.guild.id))  # update the old setting
                else:
                    await db.execute("INSERT INTO settingsbanconfirm VALUES (?,?)",
                                     (ctx.guild.id, isenabled))  # set the setting newly
                await db.commit()  # say "yes i want to do this for sure"
                await ctx.send("Ban confirms disabled!")


def setup(glaceon):
    glaceon.add_cog(Settings(glaceon))
