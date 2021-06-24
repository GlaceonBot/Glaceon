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
    @commands.has_guild_permissions(manage_messages=True)
    async def ping(self, ctx):
        '''Shows bot ping. 5s cooldown to prevent spam.'''
        await ctx.message.delete()
        embed = discord.Embed(colour=self.glaceon.embedcolor, title="Pong!",
                              description=str(round(self.glaceon.latency * 1000)) + " MS")
        embed.set_footer(text=f"Request by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
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

    @commands.command(aliases=['listwhitelistedinvites', 'lswhitelisted'])
    @commands.has_guild_permissions(administrator=True)
    async def list_whitelisted_invites(self, ctx):
        guilds_list = []
        db = self.glaceon.sql_server_connection.cursor()
        db.execute(f'''SELECT inviteguild FROM whitelisted_invites WHERE hostguild = {ctx.guild.id}''')
        guilds = db.fetchall()
        print(guilds)
        for guild in guilds:
            for guildid in guild:
                guilds_list.append(str(guildid))
        await ctx.send("`" + "`, `".join(guilds_list) + "`")



def setup(glaceon):
    glaceon.add_cog(Info(glaceon))
