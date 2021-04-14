import discord
from discord.ext import commands

embedcolor = 0xadd8e6


class HelperCommands(commands.Cog):
    """Commands gated to Manage Messages"""

    @commands.command(aliases=['clean', 'clear'])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, clear: int = 10, user: discord.Member = None):
        """Clear channel of messages, optionally from a specific user.
        Add their ping/ID to the end of the comamnd to set it to only delete messages from that user."""
        if user:
            check_func = lambda msg: msg.author == user and not msg.pinned
        else:
            check_func = lambda msg: not msg.pinned

        await ctx.message.delete()
        try:
            await ctx.channel.purge(limit=clear, check=check_func)
            embed = discord.Embed(colour=embedcolor)
            embed.add_field(name="Clear", value="cleared " + str(clear) + " messages")
            embed.set_footer(text=f"Request by {ctx.author}")
            await ctx.send(embed=embed, delete_after=10)
        except discord.Forbidden:
            await ctx.send("Whoops! I don't have the `manage messages` permission!")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason):
        """Warn a member."""
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
        """Mute a user. Optionally has a reason."""
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
        try:
            await member.add_roles(muted_role, reason=reason)
        except discord.Forbidden:
            ctx.send("Whoops! I don't have the `manage roles` permission!")
        if time is None:
            time = "when it is manually revoked."
        try:
            await member.send(f" you have been muted from: {guild.name} for: {reason}. Your mute will expire {time}")
        except discord.Forbidden:
            await ctx.send("Unable to DM, muting anyway!", delete_after=10)

    @commands.command(description="Unmutes a specified user.")
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member):
        """Unmutes a member."""
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        try:
            await member.remove_roles(muted_role)
        except discord.Forbidden:
            ctx.send("Whoops! I don't have the `manage roles` permission!")
        try:
            await member.send(f" you have been unmuted in: - {ctx.guild.name}")
        except discord.Forbidden:
            pass
        embed = discord.Embed(title="unmute", description=f" unmuted-{member.mention}",
                              colour=discord.Colour.light_gray())
        await ctx.send(embed=embed, delete_after=10)


def setup(glaceon):
    glaceon.add_cog(HelperCommands(glaceon))
