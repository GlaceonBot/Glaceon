import pathlib
import time
import datetime
import discord
from discord.ext import commands

embedcolor = 0xadd8e6

path = pathlib.PurePath()

with open(path / 'embeds/helputility.txt', 'r') as file:
    helputility = file.read()
with open(path / 'embeds/helpmod.txt', 'r') as file:
    helpmod = file.read()
with open(path / 'embeds/helphelper.txt', 'r') as file:
    helphelper = file.read()
with open(path / 'embeds/botcredits.txt', 'r') as file:
    botcredits = file.read()


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.message.delete()
        embed = discord.Embed(colour=embedcolor, title="Pong!")
        embed.add_field(name="Ping:",
                        value=str(round(self.bot.latency * 1000)) + " MS",
                        inline=True)
        embed.set_footer(text=f"Request by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command()
    async def credits(self, ctx):
        embed = discord.Embed(colour=embedcolor, title="Commands")
        embed.add_field(name="Bot credits:",
                        value=botcredits,
                        inline=True)
        embed.set_footer(text=f"Request by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(colour=embedcolor, title="Commands", timestamp=ctx.message.created_at)
        embed.add_field(name="Bot utilities:",
                        value=helputility,
                        inline=True)
        embed.add_field(name="Moderation commands:",
                        value=helpmod,
                        inline=True)
        embed.add_field(name="Helper commands:",
                        value=helphelper,
                        inline=True)
        embed.set_footer(text=f"Request by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx):
        embed = discord.Embed(color=embedcolor)
        embed.add_field(
            name="**__You can invite Glaceon to your server with the link below__**",
            value="**[Invite](https://discord.com/oauth2/authorize?client_id=808149899182342145&permissions=3100503255"
                  "&scope=bot)**",
            inline=True,)
        await ctx.send(embed=embed)

def setup(glaceon):
    glaceon.add_cog(Info(glaceon))
