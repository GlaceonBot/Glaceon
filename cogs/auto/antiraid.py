# TODO AntiRaid coming soon :D
import discord
from discord.ext import commands


class Antiraid(commands.Cog):
    """Antiraid coming soon :D"""

    def __init__(self, glaceon):
        self.glaceon = glaceon

    @commands.Cog.listener()
    async def on_member_join(self, ctx):
        try:
            if ctx.display_name.startswith("!"):
                await ctx.edit(nick="Dehoisted")
            elif ctx.display_name.startswith("."):
                await ctx.edit(nick="Dehoisted")
            elif ctx.display_name.startswith(")"):
                await ctx.edit(nick="Dehoisted")
            elif ctx.display_name.startswith("("):
                await ctx.edit(nick="Dehoisted")
            elif ctx.display_name.startswith("*"):
                await ctx.edit(nick="Dehoisted")
            elif ctx.display_name.startswith("."):
                await ctx.edit(nick="Dehoisted")
        except discord.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_member_update(self, before, ctx):
        try:
            if ctx.display_name.startswith("!"):
                await ctx.edit(nick="Dehoisted")
            elif ctx.display_name.startswith("."):
                await ctx.edit(nick="Dehoisted")
            elif ctx.display_name.startswith(")"):
                await ctx.edit(nick="Dehoisted")
            elif ctx.display_name.startswith("("):
                await ctx.edit(nick="Dehoisted")
            elif ctx.display_name.startswith("*"):
                await ctx.edit(nick="Dehoisted")
            elif ctx.display_name.startswith("."):
                await ctx.edit(nick="Dehoisted")
        except discord.Forbidden:
            pass


def setup(glaceon):
    glaceon.add_cog(Antiraid(glaceon))
