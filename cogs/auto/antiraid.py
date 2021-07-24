# TODO AntiRaid coming soon :D
import discord
from discord.ext import commands


class Antiraid(commands.Cog):
    """Antiraid coming soon :D"""

    def __init__(self, glaceon):
        self.glaceon = glaceon

    async def is_dehoisting_enabled(self, ctx):
        async with self.glaceon.sql_server_pool.acquire() as connection:
            async with connection.cursor() as db:
                await db.execute(f'''SELECT setto FROM settings WHERE serverid = %s AND setting = %s''',
                                 (ctx.guild.id, "auto_dehoist"))  # get the current setting
                if await db.fetchone():
                    try:
                        await db.execute(f'''SELECT setto FROM settings WHERE serverid = %s AND setting = %s''',
                                         (ctx.guild.id, "auto_dehoist"))
                    except AttributeError:
                        return 0
                settings = await db.fetchone()
                if settings:
                    return settings[0]
                else:
                    return 0

    @commands.Cog.listener()
    async def on_member_join(self, ctx):
        if await self.is_dehoisting_enabled(ctx) == 1:
            hoisters = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '.', ',', '/', '>', '<', '\'', '"',
                        '?', '`', '[', ']', '{', '}', ':', ';', '+', '=', '\\']
            for hoisting_char in hoisters:
                if ctx.display_name.startswith(hoisting_char):
                    try:
                        await ctx.edit(nick="Dehoisted")
                    except discord.Forbidden:
                        pass

    @commands.Cog.listener()
    async def on_member_update(self, _, ctx):
        if await self.is_dehoisting_enabled(ctx) == 1:
            can_set_nick_to_username = True
            hoisters = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '.', ',', '/', '>', '<', '\'', '"',
                        '?', '`', '[', ']', '{', '}', ':', ';', '+', '=', '\\']
            for hoisting_char in hoisters:
                if ctx.display_name.startswith(hoisting_char):
                    for hoisting_character in hoisters:
                        if ctx.name.startswith(hoisting_character):
                            can_set_nick_to_username = False
                        if can_set_nick_to_username:
                            try:
                                await ctx.edit(nick=ctx.name)
                            except discord.Forbidden:
                                pass
                        else:
                            try:
                                await ctx.edit(nick="Dehoisted")
                            except discord.Forbidden:
                                pass


def setup(glaceon):
    glaceon.add_cog(Antiraid(glaceon))
