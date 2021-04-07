import pathlib
import sqlite3
import discord
from discord.ext import commands

path = pathlib.PurePath()


class Modsend(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(aliases=['staffsay', 'modsay', 'staffsend'])
    @commands.has_permissions(manage_messages=True)
    async def modsend(self, ctx, *, message):
        """Sends a message for the moderators"""
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def modmailsetup(self, ctx, channel: discord.TextChannel):
        serverid = ctx.guild.id
        modmailchannel = sqlite3.connect(path / 'system/data.sqldb')
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

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def modmail(self, ctx, *, message):
        sid = ctx.guild.id
        prefixes = sqlite3.connect(path / 'system/data.sqldb')
        cur = prefixes.cursor()
        cur.execute(f'''SELECT channelid FROM mailchannels WHERE serverid = {sid}''')
        channel = cur.fetchone()
        prefixes.close()
        if channel:
            sendchannel = self.bot.get_channel(channel[0])
            print(sendchannel)
            await sendchannel.send(message)
        else:
            ctx.send(
                "The moderators need to set up a modmail channel first, they can do so with the `modmailsetup` command!"
            )
        pass


def setup(glaceon):
    glaceon.add_cog(Modsend(glaceon))
