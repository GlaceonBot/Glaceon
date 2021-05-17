import asyncio
import pathlib

import aiosqlite
import discord
from discord.ext import commands

path = pathlib.PurePath()

NO_EMOJI = '<:deny:843248140370313262>'  # global variables for yes and no emojis
YES_EMOJI = '<:allow:843248140551192606>'

class ModCommands(commands.Cog):
    """Commands gated behind kick members, ban members, and manage channels."""

    def __init__(self, bot):
        self.bot = bot  # set self.bot
        self._last_member = None

    async def are_ban_confirms_enabled(self, message) -> bool:
        async with aiosqlite.connect(path / "system/data.db") as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS settingsbanconfirm 
                (serverid INTEGER, setto INTEGER)""")
            cur = await db.execute(f'''SELECT setto FROM settingsbanconfirm WHERE serverid = {message.guild.id}''')
            settings = await cur.fetchone()
            if settings is not None:
                return True if settings[0] == 1 else False
            else:
                return True

    async def if_no_reacted(self, ctx, confirmation_message: discord.Message) -> None:  # what should be done if the user reacts with no
        def added_no_emoji_check(reaction, user):  # the actual check
            return user == ctx.message.author and str(reaction.emoji) == NO_EMOJI

        try:  # checks to see if this happens
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=added_no_emoji_check)
        except asyncio.TimeoutError:  # if command times out then do nothing
            try:
                await confirmation_message.delete()
            except discord.HTTPException:
                pass
        else:  # delete the confirmation message if the x is pressed
            try:  # makes sure if someone presses both buttons no errors happen
                await confirmation_message.delete()
            except discord.HTTPException:
                pass

    async def if_yes_reacted(self, ctx, confirmation_message: discord.Message, member: discord.Member, reason: str, action: str):  # If yes is reacted. Takes params for the
        # message that asked, the member who should be banned, the reason for the action, and weather it is a kick or
        # a ban
        def added_yes_emoji_check(reaction, user: discord.Member) -> bool:  # the actual check
            return user == ctx.message.author and str(reaction.emoji) == YES_EMOJI

        try:  # checks to see if this happens
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=added_yes_emoji_check)
        except asyncio.TimeoutError:  # if the timeout is reached do nothing
            pass
        else:
            try:  # makes sure if someone presses both buttons no errors happen
                await confirmation_message.delete()  # delete confirmation message
            except discord.HTTPException:
                pass
            try:  # try to notify user
                
                await member.send(f"You were {'banned' if action == 'ban' else 'kicked' } from {ctx.guild} for: {reason}")
            except discord.Forbidden:  # if the user could not be messaged, do nothing
                pass
            try:
                if action == "ban": # Check if action is ban or kick
                    await member.ban(reason=reason,
                                        delete_message_days=0)  # actually bans user, does not delete history
                    await ctx.send(f"User {member} has been banned!",
                                    delete_after=5)  # says in chat that the user was banned successfully, deletes
                elif action == "kick":
                    await member.kick(reason=reason,)  # actually kicks user
                    await ctx.send(f"User {member} has been kicked!",
                                    delete_after=5)  # says in chat that the user was kicked successfully, deletes
                # after 5s
            except discord.Forbidden:  # if the bot can't ban people, notify the mods
                await ctx.send("I do not have the requisite permissions to do this!")
                

    # kick
    @commands.command(aliases=["k"])
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str="No reason specified."):
        """Kicks a user."""
        await ctx.message.delete()  # deletes command invocation
        if member is None:  # makes sure there is a member paramater and notify if there isnt
            await ctx.send("No member specified!")
        elif member.top_role >= ctx.me.top_role:
            await ctx.send("This user has a role above mine in the role hierarchy!")
        elif member == ctx.me:
            await ctx.send("I can't kick myself!")
        elif not member.bot and await self.are_ban_confirms_enabled(ctx):  # bots can't be DMd by other bots
            confirmation_message = await ctx.send(f"Are you sure you want to kick {member}?")  # asks for confirmation
            await confirmation_message.add_reaction(YES_EMOJI)  # add reaction for yes
            await confirmation_message.add_reaction(NO_EMOJI)  # add reaction for no
            confirmation_no_task = asyncio.create_task(self.if_no_reacted(ctx, confirmation_message))  # creates async task for no
            # creates async task for yes
            confirmation_yes_task = asyncio.create_task(self.if_yes_reacted(ctx, confirmation_message, member, reason, "kick"))
            await confirmation_no_task  # starts no task
            await confirmation_yes_task  # starts yes task
        elif not member.bot and not await self.are_ban_confirms_enabled(ctx):
            await ctx.send(f"Kicked user {member}", delete_after=5)
            await member.kick(reason=reason)
        else:
            await ctx.send(f"{member} is a bot, I can not DM other bots. Kicking without sending DM.", delete_after=5)
            await member.kick(reason=f'Kicked by {ctx.author} | {reason}')

    # ban
    @commands.command(aliases=["b"])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str="No reason specified."):
        """Bans a user."""
        await ctx.message.delete()  # deletes command invocation
        if member is None:  # makes sure there is a member paramater and notify if there isnt
            await ctx.send("No member specified!")
        elif member.top_role >= ctx.me.top_role:
            await ctx.send("This user has a role above mine in the role hierarchy!")
        elif member == ctx.me:
            await ctx.send("I can't ban myself!")
        elif not member.bot and await self.are_ban_confirms_enabled(ctx):  # bots can't be DMd by other bots
            confirmation_message = await ctx.send(f"Are you sure you want to ban {member}?")  # asks for confirmation
            await confirmation_message.add_reaction(YES_EMOJI)  # add reaction for yes
            await confirmation_message.add_reaction(NO_EMOJI)  # add reaction for no
            no_check_task = asyncio.create_task(self.if_no_reacted(ctx, confirmation_message))  # creates async task for no
            # creates async task for yes
            yes_check_task = asyncio.create_task(self.if_yes_reacted(ctx, confirmation_message, member, reason, "ban"))
            await no_check_task  # starts no task
            await yes_check_task  # starts yes task
        elif not member.bot and not await self.are_ban_confirms_enabled(ctx):
            await ctx.send(f"Banned user {member}", delete_after=5)
            await member.ban(reason=reason, delete_message_days=0)
        else:
            await ctx.send(f"{member} is a bot, I can not DM other bots. Banning without sending DM.", delete_after=5)
            await member.ban(reason=f'Banned by {ctx.author} | {reason}', delete_message_days=0)

    # lock
    @commands.command(aliases=['lockdown', 'archive'])
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        """Locks a channel"""
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)  # disallows default role
        # chatting perms in that channel
        await ctx.send(ctx.channel.mention + " **has been locked.**")  # notifies users the channel is locked

    # unlock
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        """Unlocks a channel"""
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)  # allows default role chatting
        # perms in that channel
        await ctx.send(ctx.channel.mention + " **has been unlocked.**")  # notifies users it has been unlocked

    # unban
    @commands.command(aliases=['ub', 'pardon'])
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: discord.User):
        """Unbans user."""
        await ctx.message.delete()  # deletes invocation
        user = await self.bot.fetch_user(member.id)  # gets the user id so the unban method can be invoked
        try:
            await ctx.guild.unban(user)  # unbans
        except discord.Forbidden:
            await ctx.send("I do not have permission to do this!")
        except discord.HTTPException:
            await ctx.send("User is not banned!")
        await ctx.send(f"Unbanned {user}!", delete_after=10)  # Notifies mods


def setup(glaceon):  # dpy setup cog
    glaceon.add_cog(ModCommands(glaceon))
