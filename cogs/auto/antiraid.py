# TODO AntiRaid coming soon :D
import discord
from discord.ext import commands


class Antiraid(commands.Cog):
    """Antiraid coming soon :D"""

    def __init__(self, glaceon):
        self.glaceon = glaceon

    async def is_dehoisting_enabled(self, ctx):
        db = self.glaceon.sql_server_connection.cursor()
        db.execute("""CREATE TABLE IF NOT EXISTS settings 
                                (serverid BIGINT, setto BIGINT, setting TEXT)""")
        db.execute(f'''SELECT setto FROM settings WHERE serverid = %s AND setting = %s''',
                   (ctx.guild.id, "auto_dehoist"))  # get the current setting
        if db.fetchone():
            try:
                db.execute(f'''SELECT setto FROM settings WHERE serverid = %s AND setting = %s''',
                           (ctx.guild.id, "auto_dehoist"))
            except AttributeError:
                return 0
            settings = db.fetchone()
            if settings:
                print(settings[0])
                return settings[0]
            else:
                return 0

    @commands.Cog.listener()
    async def on_member_join(self, ctx):
        if await self.is_dehoisting_enabled(ctx) == 1:
            hoisters = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '.', ',', '/', '>', '<', '\'', '"',
                        '?', '`', '[', ']', '{', '}', ':', ';', '+', '=']
            for hoisting_char in hoisters:
                if ctx.display_name.startswith(hoisting_char):
                    try:
                        await ctx.edit(nick="Dehoisted")
                    except discord.Forbidden:
                        pass

    @commands.Cog.listener()
    async def on_member_update(self, _, ctx):
        if await self.is_dehoisting_enabled(ctx) == 1:
            hoisters = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '.', ',', '/', '>', '<', '\'', '"',
                        '?', '`', '[', ']', '{', '}', ':', ';', '+', '=']
            for hoisting_char in hoisters:
                if ctx.display_name.startswith(hoisting_char):
                    try:
                        await ctx.edit(nick="Dehoisted")
                    except discord.Forbidden:
                        pass


def setup(glaceon):
    glaceon.add_cog(Antiraid(glaceon))
