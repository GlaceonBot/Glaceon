import discord
from discord.ext import commands


# kick
class Modcommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason specified."):
        await ctx.message.delete()
        if member is None:
            await ctx.send("No member specified!")
        if not member.bot:
            await member.send(f"You were kicked from {ctx.guild} for: {reason}")
        await member.kick(reason=reason)
        await ctx.send(f"User {member} Has Been Kicked!", delete_after=10)

    # ban
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason specified."):
        await ctx.message.delete()
        if member is None:
            await ctx.send("No member specified!")
        if not member.bot:
            await member.send(f"You were banned from {ctx.guild} for: {reason}")
        await member.ban(reason=reason)
        await ctx.send(f"User {member} Has Been Banned!", delete_after=10)

    @commands.command(aliases=['lockdown', 'archive'])
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(ctx.channel.mention + " **has been locked.**")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(ctx.channel.mention + " **has been unlocked.**")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def tempban(self, ctx):
        ctx.send("This command is under construction!")

    @commands.command()
    @commands.guild_only()  # Might not need ()
    async def unban(self, ctx, member: discord.User):
        user = await self.bot.fetch_user(member.id)
        await ctx.guild.unban(user)
        await ctx.send(f"Unbanned {user}!", delete_after=10)


def setup(glaceon):
    glaceon.add_cog(Modcommands(glaceon))
