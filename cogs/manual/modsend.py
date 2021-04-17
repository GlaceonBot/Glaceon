import pathlib
import sqlite3
from discord.ext import commands

path = pathlib.PurePath()


class ModCommmunications(commands.Cog):
    """Communicate with the mods and for the mods"""

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
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def modmail(self, ctx, *, message):
        """Sends a message TO the moderators"""
        sid = ctx.guild.id
        prefixes = sqlite3.connect(path / 'system/data.db')
        cur = prefixes.cursor()
        cur.execute(f'''SELECT channelid FROM mailchannels WHERE serverid = {sid}''')
        channel = cur.fetchone()
        prefixes.close()
        if channel:
            sendchannel = self.bot.get_channel(channel[0])
            print(sendchannel)
            await sendchannel.send(message)
        else:
            await ctx.send(
                "The moderators need to set up a modmail channel first, they can do so with the `modmailsetup` command!"
            )
        pass

def setup(glaceon):
    glaceon.add_cog(ModCommmunications(glaceon))
