import asyncio

import discord
from discord.ext import commands


# kick
class ModCommands(commands.Cog):
    """Commands gated behind kick members, ban members, and manage channels."""

    def __init__(self, bot):
        self.bot = bot  # set self.bot
        self._last_member = None
        global nomoji
        global yesmoji
        nomoji = '<:deny:843248140370313262>'  # global variables for yes and no emojis
        yesmoji = '<:allow:843248140551192606>'

    async def if_no_reacted(self, ctx, askmessage):  # what should be done if the user reacts with no
        def added_no_emoji_check(reaction, user):  # the actual check
            return user == ctx.message.author and str(reaction.emoji) == nomoji

        try:  # checks to see if this happens
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=added_no_emoji_check)
        except asyncio.TimeoutError:  # if command times out then do nothing
            try:
                await askmessage.delete()
            except discord.HTTPException:
                pass
        else:  # delete the confirmation message if the x is pressed
            try:  # makes sure if someone presses both buttons no errors happen
                await askmessage.delete()
            except discord.HTTPException:
                pass

    async def if_yes_reacted(self, ctx, askmessage, member, reason, ban):  # If yes is reacted. Takes params for the
        # message that asked, the member who should be banned, the reason for the action, and weather it is a kick or
        # a ban
        def added_yes_emoji_check(reaction, user):  # the actual check
            return user == ctx.message.author and str(reaction.emoji) == yesmoji

        try:  # checks to see if this happens
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=added_yes_emoji_check)
        except asyncio.TimeoutError:  # if the timeout is reached do nothing
            pass
        else:
            try:  # makes sure if someone presses both buttons no errors happen
                await askmessage.delete()  # delete confirmation message
            except discord.HTTPException:
                pass
            if ban is True:  # check if we are banning or kicking
                try:  # try to notify user
                    await member.send(f"You were banned from {ctx.guild} for: {reason}")
                except discord.Forbidden:  # if the user could not be messaged, do nothing
                    pass
                try:
                    await member.ban(reason=reason,
                                     delete_message_days=0)  # actually bans user, does not delete history
                    await ctx.send(f"User {member} Has Been banned!",
                                   delete_after=5)  # says in chat that the user was banned successfully, deletes
                    # after 5s
                except discord.Forbidden:  # if the bot can't ban people, notify the mods
                    await ctx.send("I do not have the requisite permissions to do this!")
            else:  # if a kick is desired
                try:  # try to notify user
                    await member.send(f"You were kicked from {ctx.guild} for: {reason}")
                except discord.Forbidden:  # if the user could not be messaged, do nothing
                    pass
                try:
                    await member.kick(reason=reason)  # actually kicks the user
                    await ctx.send(f"User {member} Has Been Kicked!",
                                   delete_after=5)  # says in chat that the user was kicked successfully, deletes
                    # after 5s
                except discord.Forbidden:  # if the bot can't kick people, say so
                    await ctx.send("I do not have the requisite permissions to do this!")

    @commands.command(aliases=["k"])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason specified."):
        """Kicks a user."""
        await ctx.message.delete()  # deletes command invocation
        if member is None:  # makes sure there is a member paramater and notify if there isnt
            await ctx.send("No member specified!")
        elif not member.bot:  # bots can't be DMd by other bots
            askmessage = await ctx.send(f"Are you sure you want to kick {member}?")  # asks for confirmation
            await askmessage.add_reaction(yesmoji)  # add reaction for yes
            await askmessage.add_reaction(nomoji)  # add reaction for no
            confirmation_no_task = asyncio.create_task(self.if_no_reacted(ctx, askmessage))  # creates async task for no
            # creates async task for yes
            confirmation_yes_task = asyncio.create_task(self.if_yes_reacted(ctx, askmessage, member, reason, False))
            await confirmation_no_task  # starts no task
            await confirmation_yes_task  # starts yes task
        else:
            await ctx.send("User is a bot, I can not DM other bots. Kicking without sending DM.")
            await member.kick(reason=reason)

    # ban
    @commands.command(aliases=["b"])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason specified."):
        """Bans a user."""
        await ctx.message.delete()  # deletes command invocation
        if member is None:  # makes sure there is a member paramater and notify if there isnt
            await ctx.send("No member specified!")
        elif not member.bot:  # bots can't be DMd by other bots
            askmessage = await ctx.send(f"Are you sure you want to ban {member}?")  # asks for confirmation
            await askmessage.add_reaction(yesmoji)  # add reaction for yes
            await askmessage.add_reaction(nomoji)  # add reaction for no
            no_check_task = asyncio.create_task(self.if_no_reacted(ctx, askmessage))  # creates async task for no
            # creates async task for yes
            yes_check_task = asyncio.create_task(self.if_yes_reacted(ctx, askmessage, member, reason, True))
            await no_check_task  # starts no task
            await yes_check_task  # starts yes task
        else:
            await ctx.send("User is a bot, I can not DM other bots. Banning without sending DM.")
            await member.ban(reason=reason)

    @commands.command(aliases=['lockdown', 'archive'])
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        """Locks a channel"""
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)  # disallows default role
        # chatting perms in that channel
        await ctx.send(ctx.channel.mention + " **has been locked.**")  # notifies users the channel is locked

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        """Unlocks a channel"""
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)  # allows default role chatting
        # perms in that channel
        await ctx.send(ctx.channel.mention + " **has been unlocked.**")  # notifies users it has been unlocked

    @commands.command(aliases=['ub', 'pardon'])
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: discord.User):
        """Unbans user."""
        await ctx.message.delete()  # deletes invocation
        user = await self.bot.fetch_user(member.id)  # gets the user id so the unban method can be invoked
        await ctx.guild.unban(user)  # unbans
        await ctx.send(f"Unbanned {user}!", delete_after=10)  # Notifies mods


def setup(glaceon):  # dpy setup cog
    glaceon.add_cog(ModCommands(glaceon))
