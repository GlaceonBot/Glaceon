import pathlib
import platform
import shutil

import cpuinfo
import discord
import psutil
from discord.ext import commands

import utils

path = pathlib.PurePath()

with open(path / 'embeds/botcredits.txt', 'r') as file:
    botcredits = file.read()


class Info(commands.Cog):
    def __init__(self, glaceon):
        self.glaceon = glaceon

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    @utils.disableable()
    async def ping(self, ctx):
        """Shows bot ping."""
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
        embed.add_field(name="CPU",
                        value=f"{cpuinfo.get_cpu_info()['brand_raw']}\n{psutil.cpu_count()}-thread {int(psutil.cpu_freq().current)} MHz {cpuinfo.get_cpu_info()['arch']}",
                        inline=True)
        embed.add_field(name="RAM", value=str(round(psutil.virtual_memory().total / 1073741824)) + "GiB", inline=True)
        embed.add_field(name="OS", value=f"{platform.system()} {platform.release()}", inline=True)
        embed.add_field(name="Python version", value=platform.python_version(), inline=True)
        embed.add_field(name="Discord.py version", value=discord.__version__, inline=True)
        embed.add_field(name="Glaceon version", value="0.0.1", inline=True)
        embed.add_field(name="CPU usage", value=str(psutil.cpu_percent()) + "%", inline=True)
        embed.add_field(name="RAM usage",
                        value=f"{psutil.virtual_memory().percent}%, {int(psutil.virtual_memory().used / 1048576)}MiB used, {int(psutil.virtual_memory().free / 1048576)} MiB free",
                        inline=True)
        embed.add_field(name="Disk usage",
                        value=f"{int(shutil.disk_usage('.').total / 1073741824)}GiB total, {int(shutil.disk_usage('.').used / 1048576)} MiB used, {int(shutil.disk_usage('.').free / 1048576)} MiB free",
                        inline=True)
        await ctx.send(embed=embed)

    @commands.command(aliases=['listwhitelistedinvites', 'lswhitelisted'])
    @commands.has_guild_permissions(administrator=True)
    async def list_whitelisted_invites(self, ctx):
        guilds_list = []
        connection = await self.glaceon.sql_server_pool.acquire()
        db = await connection.cursor()
        await db.execute(f'''SELECT inviteguild FROM whitelisted_invites WHERE hostguild = {ctx.guild.id}''')
        guilds = await db.fetchall()
        await db.close()
        connection.close()
        self.glaceon.sql_server_pool.release(connection)
        if guilds:
            for guild in guilds:
                for guildid in guild:
                    guilds_list.append(str(guildid))
            await ctx.send("`" + "`, `".join(guilds_list) + "`")
        else:
            await ctx.send("No invites are whitelisted in this guild!")

    @commands.command()
    @commands.guild_only()
    @utils.disableable()
    async def disabled(self, ctx, command=None):
        """List commands that are disabled on this server. <:deny:843248140370313262> means disabled, <:allow:843248140551192606> means enabled, and <:permanantly_enabled:865819204652892201> is for commands that cannot be disabled."""
        connection = await self.glaceon.sql_server_pool.acquire()
        db = await connection.cursor()
        commands = []
        for command in self.glaceon.walk_commands():
            await db.execute("""SELECT state FROM disabled_commands WHERE command = %s AND guildid = %s""",
                             (command.qualified_name, ctx.guild.id))
            state = await db.fetchone()
            for check in command.checks:
                if 'disableable' not in check.__qualname__:
                    commands.append('<:permanantly_enabled:865819204652892201> ' + command.name)
                elif state is None:
                    commands.append('<:allow:843248140551192606> ' + command.name)
                elif state[0] == 0:
                    commands.append('<:deny:843248140370313262> ' + command.name)
                else:
                    commands.append('<:allow:843248140551192606> ' + command.name)
                break
        embed = discord.Embed(colour=self.glaceon.embedcolor, title="Commands currently enabled",
                              description='\n'.join(commands))
        embed.set_footer(text=f"Request by {ctx.author}")
        await ctx.send(embed=embed)
        await db.close()
        connection.close()
        self.glaceon.sql_server_pool.release(connection)


def setup(glaceon):
    glaceon.add_cog(Info(glaceon))
