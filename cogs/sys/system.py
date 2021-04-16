import pathlib
import sqlite3

import discord
from discord.ext import commands

path = pathlib.PurePath()
embedcolor = 0xadd8e6


async def sendwelcome(channel: discord.TextChannel):
    embed = discord.Embed(colour=embedcolor, title="Hi!")
    embed.add_field(name="Thank you for adding me to your server!",
                    value="I appreciate your interest in Glaceon! Run `%help` to get started!\n"
                          "Make sure to read the [TOS](https://randomairborne.dev/glaceon/tos)"
                          " and the [privacy policy](https://randomairborne.dev/glaceon/privacy).",
                    inline=False)
    await channel.send(embed=embed)


class BotSystem(commands.Cog):
    """Commands for the bot configuration. Admin only."""

    def __init__(self, glaceon):
        self.glaceon = glaceon

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, newprefix):
        """Sets the bot prefix for this server"""
        serverid = ctx.guild.id
        prefixesls = sqlite3.connect(path / 'system/data.db')
        cur = prefixesls.cursor()
        cur.execute(f'''SELECT prefix FROM prefixes WHERE serverid = {serverid}''')
        if cur.fetchone() is not None:
            cur.execute("""UPDATE prefixes SET prefix = ? WHERE serverid = ?""", (newprefix, serverid))
        else:
            cur.execute("INSERT INTO prefixes(serverid, prefix) VALUES (?,?)",
                        (serverid, newprefix))
        prefixesls.commit()
        prefixesls.close()
        await ctx.send(f"Prefix set to {newprefix}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def modmailsetup(self, ctx, channel: discord.TextChannel):
        """Sets up ModMail"""
        serverid = ctx.guild.id
        modmailchannel = sqlite3.connect(path / 'system/data.db')
        cur = modmailchannel.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS mailchannels
                           (serverid INTEGER, channelid INTEGER)''')
        cur.execute(f'''SELECT serverid FROM mailchannels WHERE serverid = {serverid}''')
        if cur.fetchone() is not None:
            cur.execute("""UPDATE mailchannels SET channelid = ? WHERE serverid = ?""", (channel, serverid))
        else:
            cur.execute("INSERT INTO mailchannels(serverid, channelid) VALUES (?,?)",
                        (serverid, channel.id))
        modmailchannel.commit()
        modmailchannel.close()
        await ctx.send(f"ModMail channel is now {channel}")

    @commands.Cog.listener()
    async def on_guild_join(self, ctx):
        sent = False
        for name in ctx.channels:
            if not sent:
                if name.name == "bot-spam":
                    await sendwelcome(name)
                    sent = True
                elif name.name == "bot-commands":
                    await sendwelcome(name)
                    sent = True
                elif name.name == "bot":
                    await sendwelcome(name)
                    sent = True
                elif name.name == "off-topic":
                    await sendwelcome(name)
                    sent = True
                elif name.name == "general":
                    await sendwelcome(name)
                    sent = True
                else:
                    for text_channels in ctx.channels:
                        if sent is False:
                            try:
                                await sendwelcome(text_channels)
                                sent = True
                            except AttributeError:
                                pass


def setup(glaceon):
    glaceon.add_cog(BotSystem(glaceon))
