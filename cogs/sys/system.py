import pathlib
import aiosqlite

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
        db = aiosqlite.connect(path / 'system/data.db')
        cur = await db.execute(f'''SELECT prefix FROM prefixes WHERE serverid = {serverid}''')
        if await cur.fetchone() is not None:
            await db.execute("""UPDATE prefixes SET prefix = ? WHERE serverid = ?""", (newprefix, serverid))
        else:
            await db.execute("INSERT INTO prefixes(serverid, prefix) VALUES (?,?)",
                        (serverid, newprefix))
        await db.commit()
        await db.close()
        await ctx.send(f"Prefix set to {newprefix}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def modmailsetup(self, ctx, channel: discord.TextChannel):
        """Sets up ModMail"""
        serverid = ctx.guild.id
        db = await aiosqlite.connect(path / 'system/data.db')
        await db.execute('''CREATE TABLE IF NOT EXISTS mailchannels
                           (serverid INTEGER, channelid INTEGER)''')
        cur = await db.execute(f'''SELECT serverid FROM mailchannels WHERE serverid = ?''', serverid)
        if cur.fetchone() is not None:
            await db.execute("""UPDATE mailchannels SET channelid = ? WHERE serverid = ?""", (channel.id, serverid))
        else:
            await db.execute("INSERT INTO mailchannels(serverid, channelid) VALUES (?,?)",
                        (serverid, channel.id))
        await db.commit()
        await db.close()
        await ctx.send(f"ModMail channel is now {channel}")

    @commands.Cog.listener()
    async def on_guild_join(self, ctx):
        sent = False
        for name in ctx.text_channels:
            if not sent:
                if name.name == "bot-spam":
                    await sendwelcome(name)
                    break
                elif name.name == "bot-commands":
                    await sendwelcome(name)

                elif name.name == "bot":
                    await sendwelcome(name)
                    sent = True
                elif name.name == "off-topic":
                    await sendwelcome(name)
                    sent = True
                elif name.name == "general":
                    await sendwelcome(name)
                    sent = True
        if not sent:
            await sendwelcome(ctx.text_channels[0])


def setup(glaceon):
    glaceon.add_cog(BotSystem(glaceon))
