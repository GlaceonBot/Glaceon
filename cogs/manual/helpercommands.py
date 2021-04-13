import discord
from discord.ext import commands

embedcolor = 0xadd8e6


class Hcommands(commands.Cog):
    @commands.command(aliases=['clean', 'clear'])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, clear: int = 10, user: discord.Member = None):
        if user:
            check_func = lambda msg: msg.author == user and not msg.pinned
        else:
            check_func = lambda msg: not msg.pinned

        await ctx.message.delete()
        await ctx.channel.purge(limit=clear, check=check_func)
        embed = discord.Embed(colour=embedcolor)
        embed.add_field(name="Clear", value="cleared " + str(clear) + " messages")
        embed.set_footer(text=f"Request by {ctx.author}")
        await ctx.send(embed=embed, delete_after=10)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason):
        await ctx.message.delete()
        if member is None:
            await ctx.send("No member specified!")
        if not member.bot:
            await member.send(
                f"You were warned in {ctx.guild} for {reason}. Make sure to reread the rules, and follow them.")
        else:
            ctx.send("I can't warn a bot!")
        await ctx.send(f"User {member} Has Been Warned! Reason sent in DMs.", delete_after=10)

    @commands.command(description="Mutes the specified user.")
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member, time=None, *, reason="No reason specified."):
        await ctx.message.delete()
        guild = ctx.guild
        muted_role = discord.utils.get(guild.roles, name="Muted")

        if not muted_role:
            muted_role = await guild.create_role(name="Muted", permissions=discord.Permissions(66560))

            for channel in guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False, read_message_history=True,
                                              read_messages=None)
        embed = discord.Embed(title="muted", description=f"{member.mention} was muted ",
                              colour=discord.Colour.light_gray())
        embed.add_field(name="reason:", value=reason, inline=False)
        await ctx.send(embed=embed, delete_after=10)
        await member.add_roles(muted_role, reason=reason)
        if time is None:
            time = "when it it manually revoked."
        await member.send(f" you have been muted from: {guild.name} for: {reason}. Your mute will expire {time}")

    @commands.command(description="Unmutes a specified user.")
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(muted_role)
        await member.send(f" you have been unmuted in: - {ctx.guild.name}")
        embed = discord.Embed(title="unmute", description=f" unmuted-{member.mention}",
                              colour=discord.Colour.light_gray())
        await ctx.send(embed=embed, delete_after=10)


def setup(glaceon):
    glaceon.add_cog(Hcommands(glaceon))
