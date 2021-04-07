import pathlib
import sqlite3

from discord.ext import commands

path = pathlib.PurePath()
embedcolor = 0xadd8e6


class BotSystem(commands.Cog):
    def __init__(self, glaceon):
        self.glaceon = glaceon

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, newprefix):
        serverid = ctx.guild.id
        prefixesls = sqlite3.connect(path / 'system/data.sqldb')
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


def setup(glaceon):
    glaceon.add_cog(BotSystem(glaceon))
