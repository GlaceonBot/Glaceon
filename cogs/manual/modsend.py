import pathlib

import discord
from discord.ext import commands

path = pathlib.PurePath()


class ModCommmunications(commands.Cog):
    """Communicate with the mods and for the mods"""

    def __init__(self, glaceon):
        self.glaceon = glaceon
        self._last_member = None

    @commands.command(aliases=['staffsay', 'modsay', 'staffsend'])
    @commands.has_permissions(manage_messages=True)
    async def modsend(self, ctx, *, message):
        """Sends a message for the moderators"""
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command(aliases=['embed', 'embedsend'])
    @commands.has_permissions(manage_messages=True)
    async def sendembed(self, ctx, title, *, message):
        await ctx.message.delete()
        embed = discord.Embed(colour=self.glaceon.embedcolor, title=title, description=message)
        embed.set_footer(text=f"Request by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.bot_has_permissions(manage_channels=True)
    async def modmail(self, ctx, *, message=None):
        """Sends a message TO the moderators"""
        global modmail_category
        await ctx.message.delete()
        modmail_dm = await ctx.message.author.create_dm()
        for category in ctx.guild.categories:
            print(category.name)
            if category.name == 'modmail' or category.name == 'mail':
                modmail_category = category
        modmail_channel = await ctx.guild.create_text_channel(ctx.author, category=modmail_category)
        if message:
            await modmail_dm.send("You: " + message)
        await modmail_dm.send("Thank you for reporting this, we should respond shortly!")


def setup(glaceon):
    glaceon.add_cog(ModCommmunications(glaceon))
