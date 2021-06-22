import pathlib
import cpuinfo
import shutil
import psutil
import platform
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
            value=f"**[Invite](https://glaceon.xyz/invite)**",
            inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def info(self, ctx):
        embed = discord.Embed(colour=self.glaceon.embedcolor, title="System Info")
        embed.set_footer(text=f"Request by {ctx.author}")
        cpu_info = platform.uname().processor.split(" ")
        embed.add_field(name="CPU", value=f"{cpuinfo.get_cpu_info()['brand_raw']}\n{psutil.cpu_count()}-thread {int(psutil.cpu_freq().current)} MHz {cpuinfo.get_cpu_info()['arch']}", inline=True)
        embed.add_field(name="RAM", value=str(round(psutil.virtual_memory().total / 1073741824)) + "GiB", inline=True)
        embed.add_field(name="OS", value=f"{platform.system()} {platform.release()}", inline=True)
        embed.add_field(name="Python version", value=platform.python_version(), inline=True)
        embed.add_field(name="Discord.py version", value=discord.__version__, inline=True)
        embed.add_field(name="Glaceon version", value="0.0.1", inline=True)
        embed.add_field(name="CPU usage", value=str(psutil.cpu_percent()) + "%", inline=True)
        embed.add_field(name="RAM usage", value=f"{psutil.virtual_memory().percent}%, {int(psutil.virtual_memory().used / 1048576)}MiB used, {int(psutil.virtual_memory().free / 1048576)} MiB free", inline=True)
        embed.add_field(name="Disk usage", value=f"{int(shutil.disk_usage('.').total / 1073741824)}GiB total, {int(shutil.disk_usage('.').used / 1048576)} MiB used, {int(shutil.disk_usage('.').free / 1048576)} MiB free", inline=True)
        await ctx.send(embed=embed)


def setup(glaceon):
    glaceon.add_cog(Info(glaceon))
