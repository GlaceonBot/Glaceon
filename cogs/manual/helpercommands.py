import pathlib
import typing
from datetime import datetime

import discord
from discord.ext import commands

import utils

path = pathlib.PurePath()


class HelperCommands(commands.Cog):
    """Commands gated to Manage Messages"""

    def __init__(self, glaceon):
        self.glaceon = glaceon

    @commands.command(aliases=['clean', 'clear'])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.guild_only()
    @utils.disableable()
    async def purge(self, ctx, clear: int = 10, user: discord.Member = None):
        """Clear channel of messages, optionally from a specific user.
        Add their ping/ID to the end of the command to set it to only delete messages from that user."""
        if user:
            check_func = lambda msg: msg.author == user and not msg.pinned
        else:
            check_func = lambda msg: not msg.pinned

        await ctx.message.delete()
        await ctx.channel.purge(limit=clear, check=check_func)
        embed = discord.Embed(colour=self.glaceon.embedcolor)
        embed.add_field(name="Clear", value="cleared " + str(clear) + " messages")
        embed.set_footer(text=f"Request by {ctx.author}")
        await ctx.send(embed=embed, delete_after=10)

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    @commands.guild_only()
    @utils.disableable()
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

    @commands.command(aliases=['staffsay', 'modsay', 'staffsend'])
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @utils.disableable()
    async def modsend(self, ctx, *, message):
        """Sends a message for the moderators"""
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command(aliases=['embed', 'embedsend'])
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @utils.disableable()
    async def sendembed(self, ctx, title, *, message):
        await ctx.message.delete()
        embed = discord.Embed(colour=self.glaceon.embedcolor, title=title, description=message)
        embed.set_footer(text=f"Request by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command(description="Mutes the specified user.")
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    @utils.disableable()
    async def mute(self, ctx, member: discord.Member, time: typing.Optional[str] = None, *,
                   reason="No reason specified"):
        """Mute a user. Optionally has a time and a reason.
        Times should be of the form `[number](letter).
        valid letters: s(econds), m(inutes), h(ours), d(ays), w(eeks), y(ears)"""
        await ctx.message.delete()
        if time is not None:
            if time.lower().endswith("y"):
                revoke_in_secs = int(time[:-1]) * 31536000
            elif time.lower().endswith("w"):
                revoke_in_secs = int(time[:-1]) * 604800
            elif time.lower().endswith("d"):
                revoke_in_secs = int(time[:-1]) * 86400
            elif time.lower().endswith("h"):
                revoke_in_secs = int(time[:-1]) * 3600
            elif time.lower().endswith("m"):
                revoke_in_secs = int(time[:-1]) * 60
            elif time.lower().endswith("s"):
                revoke_in_secs = int(time[:-1])
            else:
                revoke_in_secs = -1
                reason = time + reason
            ban_ends_at = int(datetime.utcnow().timestamp()) + revoke_in_secs
            async with self.glaceon.sql_server_pool.acquire() as connection:
                async with connection.cursor() as db:
                    await db.execute(f'''SELECT userid FROM current_bans WHERE serverid = %s''', (
                        ctx.guild.id,))  # get the current prefix for that server, if it exists
                    if await db.fetchone():  # actually check if it exists
                        await db.execute('''UPDATE current_mutes SET mutefinish = %s WHERE serverid = %s AND userid = %s''',
                                         (ban_ends_at, ctx.guild.id, member.id))  # update prefix
                    else:
                        await db.execute("INSERT INTO current_mutes(serverid, userid, mutefinish) VALUES (%s,%s,%s)",
                                         (ctx.guild.id, member.id, ban_ends_at))  # set new prefix
        guild = ctx.guild
        muted_role = discord.utils.get(guild.roles, name="Muted")

        if not muted_role:
            muted_role = await guild.create_role(name="Muted", permissions=discord.Permissions(66560))

            for channel in guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False, read_message_history=True,
                                              read_messages=None)
        embed = discord.Embed(color=self.glaceon.embedcolor, title="muted", description=f"{member.mention} was muted ")
        embed.add_field(name="reason:", value=reason, inline=False)
        await ctx.send(embed=embed, delete_after=10)
        try:
            await member.add_roles(muted_role, reason=reason)
        except discord.Forbidden:
            ctx.send("Whoops! I don't have the `manage roles` permission!")
        if time is None:
            time = "when it is manually revoked."
        else:
            time = "in " + time
        try:
            await member.send(f"You have been muted in: {guild.name} for: {reason}. Your mute will expire {time}")
        except discord.Forbidden:
            await ctx.send("Unable to DM, muting anyway!", delete_after=10)

    @commands.command(description="Unmutes a specified user.")
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    @utils.disableable()
    async def unmute(self, ctx, member: discord.Member):
        """Unmutes a member."""
        await ctx.message.delete()
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        try:
            await member.remove_roles(muted_role)
        except discord.Forbidden:
            ctx.send("Whoops! I don't have the `manage roles` permission!")
        try:
            await member.send(f" you have been unmuted in: - {ctx.guild.name}")
        except discord.Forbidden:
            pass
        embed = discord.Embed(color=self.glaceon.embedcolor, title="Unmute", description=f" Unmuted-{member.mention}")
        await ctx.send(embed=embed, delete_after=10)


def setup(glaceon):
    glaceon.add_cog(HelperCommands(glaceon))
