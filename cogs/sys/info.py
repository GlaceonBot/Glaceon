import pathlib

import discord
import requests
from discord.ext import commands

path = pathlib.PurePath()

with open(path / 'embeds/botcredits.txt', 'r') as file:
    botcredits = file.read()


class Info(commands.Cog):
    def __init__(self, glaceon):
        self.glaceon = glaceon

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, ctx):
        """Shows bot ping. 5s cooldown to prevent spam."""
        await ctx.message.delete()
        embed = discord.Embed(colour=self.glaceon.embedcolor, title="Pong!",
                              description=str(round(self.glaceon.latency * 1000)) + " MS")
        embed.set_footer(text=f"Request by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def credits(self, ctx):
        """People who helped with bot <:panda_love_purple:845475547437989888>"""
        embed = discord.Embed(colour=self.glaceon.embedcolor, title="Credits", description=botcredits)
        embed.set_footer(text=f"Request by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def invite(self, ctx):
        """Invite Glaceon to other servers."""
        embed = discord.Embed(color=self.glaceon.embedcolor)
        embed.add_field(
            name="**__You can invite Glaceon to your server with the link below__**",
            value=f"**[Invite](https://discord.com/oauth2/authorize?client_id={self.glaceon.user.id}&permissions=3100503255&scope=bot)**",
            inline=True)
        await ctx.send(embed=embed)


def setup(glaceon):
    glaceon.add_cog(Info(glaceon))
