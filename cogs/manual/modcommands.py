import discord
from discord.ext import commands


# kick
class ModCommands(commands.Cog):
    """Commands gated behind kick members, ban members, and manage channels."""

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason specified."):
        """Kicks a user."""
        await ctx.message.delete()
        if member is None:
            await ctx.send("No member specified!")
        if not member.bot:
            try:
                await member.send(f"You were banned from {ctx.guild} for: {reason}")
            except discord.Forbidden:
                await ctx.send("I could not DM the member, they must have DMs off or me blocked. Banning anyway.",
                               delete_after=10)
        try:
            await member.kick(reason=reason)
        except discord.Forbidden:
            await ctx.send("I do not have the requisite permissions to do this!")
        await ctx.send(f"User {member} Has Been Kicked!", delete_after=10)

    # ban
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason specified."):
        """Bans a user."""
        await ctx.message.delete()
        if member is None:
            await ctx.send("No member specified!")
        if not member.bot:
            try:
                await member.send(f"You were banned from {ctx.guild} for: {reason}")
            except discord.Forbidden:
                await ctx.send("I could not DM the member, they must have DMs off or me blocked. Banning anyway.",
                               delete_after=10)
        try:
            await member.ban(reason=reason)
        except discord.Forbidden:
            await ctx.send("I do not have the requisite permissions to do this!")
        await ctx.send(f"User {member} Has Been Banned!", delete_after=10)

    @commands.command(aliases=['lockdown', 'archive'])
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        """Locks a channel"""
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(ctx.channel.mention + " **has been locked.**")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        """Unlocks a channel"""
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(ctx.channel.mention + " **has been unlocked.**")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def tempban(self, ctx):
        """Temporarily bans a user."""
        ctx.send("This command is under construction!")

    @commands.command()
    async def unban(self, ctx, member: discord.User):
        """Unbans user."""
        user = await self.bot.fetch_user(member.id)
        await ctx.guild.unban(user)
        await ctx.send(f"Unbanned {user}!", delete_after=10)


def setup(glaceon):
    glaceon.add_cog(ModCommands(glaceon))
