import asyncio
import pathlib
import typing
from datetime import datetime

import discord
from discord.ext import commands

path = pathlib.PurePath()


# kick
class ModCommands(commands.Cog):
    '''Commands gated behind kick members, ban members, and manage channels.'''

    def __init__(self, glaceon):
        self.glaceon = glaceon  # set self.bot
        self._last_member = None
        global nomoji
        global yesmoji
        nomoji = '<:deny:843248140370313262>'  # global variables for yes and no emojis
        yesmoji = '<:allow:843248140551192606>'

    async def are_ban_confirms_enabled(self, message):
        db = self.glaceon.sql_server_connection.cursor()
        db.execute('''CREATE TABLE IF NOT EXISTS settings_ban_confirm 
                (serverid BIGINT, setto BIGINT)''')
        db.execute(f'''SELECT setto FROM settings_ban_confirm WHERE serverid = {message.guild.id}''')
        settings = db.fetchone()
        if settings:
            return settings[0]
        else:
            return 1

    async def if_no_reacted(self, ctx, askmessage):  # what should be done if the user reacts with no
        def added_no_emoji_check(reaction, user):  # the actual check
            return user == ctx.message.author and str(reaction.emoji) == nomoji

        try:  # checks to see if this happens
            reaction, user = await self.glaceon.wait_for('reaction_add', timeout=30.0, check=added_no_emoji_check)
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

    async def if_yes_reacted(self, ctx, askmessage, member, reason, ban,
                             time):  # If yes is reacted. Takes params for the
        # message that asked, the member who should be banned, the reason for the action, and weather it is a kick or
        # a ban
        def added_yes_emoji_check(reaction, user):  # the actual check
            return user == ctx.message.author and str(reaction.emoji) == yesmoji

        try:  # checks to see if this happens
            reaction, user = await self.glaceon.wait_for('reaction_add', timeout=30.0, check=added_yes_emoji_check)
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
                        ban_ends_at = int(datetime.utcnow().timestamp()) + revoke_in_secs
                        db = self.glaceon.sql_server_connection.cursor()
                        db.execute(f'''SELECT userid FROM current_bans WHERE serverid = %s''', (
                            ctx.guild.id,))  # get the current prefix for that server, if it exists
                        if db.fetchone():  # actually check if it exists
                            db.execute('''UPDATE current_bans SET banfinish = %s WHERE serverid = %s AND userid = %s''',
                                       (ban_ends_at, ctx.guild.id, member.id))  # update prefix
                        else:
                            db.execute("INSERT INTO current_bans(serverid, userid, banfinish) VALUES (%s,%s,%s)",
                                       (ctx.guild.id, member.id, ban_ends_at))  # set new prefix
                        self.glaceon.sql_server_connection.commit()
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
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *, reason="No reason specified."):
        '''Kicks a user.'''
        await ctx.message.delete()  # deletes command invocation
        if member is None:  # makes sure there is a member paramater and notify if there isnt
            await ctx.send("No member specified!")
        elif member == ctx.me:
            await ctx.send("I can't kick myself!")
        elif member.top_role >= ctx.me.top_role:
            await ctx.send("This user has a role above mine in the role hierarchy!")
        elif member.top_role >= ctx.me.top_role:
            await ctx.send("This user has a role above or equal to yours in the role hierarchy!")
        elif not member.bot and await self.are_ban_confirms_enabled(ctx) == 1:  # bots can't be DMd by other bots
            askmessage = await ctx.send(f"Are you sure you want to kick {member}?")  # asks for confirmation
            await askmessage.add_reaction(yesmoji)  # add reaction for yes
            await askmessage.add_reaction(nomoji)  # add reaction for no
            confirmation_no_task = asyncio.create_task(self.if_no_reacted(ctx, askmessage))  # creates async task for no
            confirmation_yes_task = asyncio.create_task(
                self.if_yes_reacted(ctx, askmessage, member, reason, False, time=None))  # creates async task for yes
            await confirmation_no_task  # starts no task
            await confirmation_yes_task  # starts yes task
        elif not member.bot and await self.are_ban_confirms_enabled(ctx) == 0:
            await ctx.send(f"Kicked user {member}", delete_after=5)
            await member.kick(reason=reason)
        else:
            await ctx.send("User is a bot, I can not DM other bots. Kicking without sending DM.", delete_after=5)
            await member.kick(reason=reason)

    # ban
    @commands.command(aliases=["b"])
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, time: typing.Optional[str] = None, *,
                  reason="No reason specified."):
        '''Bans a user.'''
        await ctx.message.delete()  # deletes command invocation
        if member is None:  # makes sure there is a member paramater and notify if there isnt
            await ctx.send("No member specified!")
        elif member == ctx.me:
            await ctx.send("I can't ban myself!")
        elif member.top_role >= ctx.me.top_role:
            await ctx.send("This user has a role above mine in the role hierarchy!")
        elif member.top_role >= ctx.me.top_role:
            await ctx.send("This user has a role above or equal to yours in the role hierarchy!")
        elif not member.bot and await self.are_ban_confirms_enabled(ctx) == 1:  # bots can't be DMd by other bots
            askmessage = await ctx.send(f"Are you sure you want to ban {member}?")  # asks for confirmation
            await askmessage.add_reaction(yesmoji)  # add reaction for yes
            await askmessage.add_reaction(nomoji)  # add reaction for no
            no_check_task = asyncio.create_task(self.if_no_reacted(ctx, askmessage))  # creates async task for no
            # creates async task for yes
            yes_check_task = asyncio.create_task(self.if_yes_reacted(ctx, askmessage, member, reason, True, time))
            await no_check_task  # starts no task
            await yes_check_task  # starts yes task
        elif not member.bot and await self.are_ban_confirms_enabled(ctx) == 0:
            await ctx.send(f"Banned user {member}", delete_after=5)
            await member.ban(reason=reason, delete_message_days=0)
        else:
            await ctx.send("User is a bot, I can not DM other bots. Banning without sending DM.", delete_after=5)
            await member.ban(reason=reason, delete_message_days=0)

    @commands.command(aliases=['lockdown', 'archive'])
    @commands.has_guild_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    async def lock(self, ctx, channel=None):
        '''Locks a channel'''
        if channel is None:
            channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)  # disallows default role
        # chatting perms in that channel
        await ctx.send(channel.mention + " **has been locked.**")  # notifies users the channel is locked

    @commands.command()
    @commands.has_guild_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    async def unlock(self, ctx, channel=None):
        '''Unlocks a channel'''
        if channel is None:
            channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)  # allows default role chatting
        # perms in that channel
        await ctx.send(channel.mention + " **has been unlocked.**")  # notifies users it has been unlocked

    @commands.command(aliases=['ub', 'pardon'])
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, member: discord.User):
        '''Unbans user.'''
        await ctx.message.delete()  # deletes invocation
        user = await self.glaceon.fetch_user(member.id)  # gets the user id so the unban method can be invoked
        try:
            await ctx.guild.unban(user)  # unbans
        except discord.Forbidden:
            await ctx.send("I do not have permission to do this!")
        except discord.HTTPException:
            await ctx.send("User is not banned!")
        await ctx.send(f"Unbanned {user}!", delete_after=10)  # Notifies mods

    @commands.command(aliases=['hoists', 'dehoist'])
    @commands.has_guild_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.cooldown(1, 3600, commands.BucketType.guild)
    @commands.guild_only()
    async def cleanhoists(self, ctx):
        await ctx.reply("This command has had to be disabled until the bot is verified or a better way to find the top users is found.")
        return
        await ctx.send("Dehoisting in progress (THIS WILL TAKE WHILE)")
        permissions = discord.Permissions(manage_nicknames=True)
        can_set_nick_to_username = True
        hoisting_chars = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '.', ',', '/', '>', '<', '\'',
                          '"', '?', '`', '[', ']', '{', '}', ':', ';', '+', '=', '\\']
        while True:
            member = None
            for hoisting_char in hoisting_chars:
                member = discord.utils.find(lambda m: m.permissions_in(ctx.channel) != permissions and m.display_name.startswith(hoisting_char), ctx.guild.members)
                if member:
                    break
            if member is None:
                await ctx.send("Hoisted members cleaned!")
                return
            for hoisting_char in hoisting_chars:
                if member.display_name.startswith(hoisting_char):
                    for hoisting_char in hoisting_chars:
                        if member.name.startswith(hoisting_char):
                            can_set_nick_to_username = False
                        if can_set_nick_to_username:
                            try:
                                await member.edit(nick=member.name)
                            except discord.Forbidden:
                                pass
                        else:
                            try:
                                await member.edit(nick="Dehoisted")
                            except discord.Forbidden:
                                pass


def setup(glaceon):  # dpy setup cog
    glaceon.add_cog(ModCommands(glaceon))
