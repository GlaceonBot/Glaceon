import pathlib
import aiofile
import discord
from discord.ext import commands

embedcolor = 0xadd8e6

path = pathlib.PurePath()

with open(path / 'embeds/botcredits.txt', 'r') as file:
    botcredits = file.read()


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['v', 'ver', '-v', '-ver', '-version'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def version(self, ctx):
        async with aiofile.async_open(path / "embeds/version.txt", "r") as file:
            version = await file.read()
            await ctx.send(version)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, ctx):
        """Shows bot ping. 5s cooldown to prevent spam."""
        await ctx.message.delete()
        embed = discord.Embed(colour=embedcolor, title="Pong!", description=str(round(self.bot.latency * 1000)) + " MS")
        embed.set_footer(text=f"Request by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def credits(self, ctx):
        """People who helped with bot <Panda_Love_Purple:832029566427856956>"""
        embed = discord.Embed(colour=embedcolor, title="Credits", description=botcredits)
        embed.set_footer(text=f"Request by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def invite(self, ctx):
        """Invite Glaceon to other servers."""
        embed = discord.Embed(color=embedcolor)
        embed.add_field(
            name="**__You can invite Glaceon to your server with the link below__**",
            value="**[Invite](https://discord.com/oauth2/authorize?client_id=808149899182342145&permissions=3100503255"
                  "&scope=bot)**",
            inline=True)
        await ctx.send(embed=embed)


def setup(glaceon):
    glaceon.add_cog(Info(glaceon))
