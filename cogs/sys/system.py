import os
import pathlib
import shutil

import discord
import requests
from discord.ext import commands

# gets global path and embed color
import utils

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
    @commands.has_guild_permissions(
        administrator=True)  # requires that the person issuing the command has administrator perms
    @commands.guild_only()
    async def prefix(self, ctx, newprefix):  # context and what we should set the new prefix to
        """Sets the bot prefix for this server"""
        serverid = ctx.guild.id  # gets serverid for convinience
        connection = await self.glaceon.sql_server_pool.acquire()
        db = await connection.cursor()  # connect to our server database
        await db.execute(
            f'''SELECT prefix FROM prefixes WHERE serverid = {serverid}''')  # get the current prefix for that server, if it exists
        if await db.fetchone():  # actually check if it exists
            await db.execute('''UPDATE prefixes SET prefix = %s WHERE serverid = %s''',
                       (newprefix, serverid))  # update prefix
        else:
            await db.execute("INSERT INTO prefixes(serverid, prefix) VALUES (%s,%s)",
                       (serverid, newprefix))  # set new prefix
        # close connection
        await db.close()
        connection.close()
        self.glaceon.sql_server_pool.release(connection)
        await ctx.send(f"Prefix set to {newprefix}")  # tell admin what happened

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
                                       f"https://discord.com/developers/applications/{self.glaceon.user.id}/bot")
            os.remove(path / f'tmp/{pfp_path}')
            await ctx.send("Avatar updated!", delete_after=10)
        else:
            await ctx.send("Failed to update avatar!", delete_after=10)


def setup(glaceon):
    glaceon.add_cog(BotSystem(glaceon))
