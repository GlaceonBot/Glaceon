import pathlib
from datetime import datetime

import aiosqlite
import discord
from discord.ext import tasks, commands

path = pathlib.PurePath()


class UnCog(commands.Cog):
    def __init__(self, glaceon):
        self.index = 0
        self.glaceon = glaceon
        self.unmuter.start()
        self.unbanner.start()

    def cog_unload(self):
        self.unbanner.cancel()
        self.unmuter.cancel()

    @tasks.loop(seconds=5.0)
    async def unbanner(self):
        current_time = int(datetime.utcnow().timestamp())
        for guild in self.glaceon.guilds:
            # connect to the sqlite database for prefixes
            db = await aiosqlite.connect(path / 'system/moderation.db')
            # make sure everything is set up correctly
            await db.execute('''CREATE TABLE IF NOT EXISTS current_bans
                                       (serverid INTEGER,  userid INTEGER, banfinish INTEGER)''')
            # find which prefix matches this specific server id
            cur = await db.execute(
                '''SELECT userid FROM current_bans WHERE serverid = ? AND banfinish >= ? AND banfinish != -1''', (guild.id, current_time))
            member_line = await cur.fetchone()
            if member_line is not None:
                member = member_line[0]
                print(member_line)
                member: discord.Member
                await guild.unban(member)

    @tasks.loop(seconds=5.0)
    async def unmuter(self):
        current_time = int(datetime.utcnow().timestamp())
        for guild in self.glaceon.guilds:
            # connect to the sqlite database for prefixes
            db = await aiosqlite.connect(path / 'system/moderation.db')
            # make sure everything is set up correctly
            await db.execute('''CREATE TABLE IF NOT EXISTS current_mutes
                           (serverid INTEGER,  userid INTEGER, mutefinish INTEGER)''')
            # find which prefix matches this specific server id
            cur = await db.execute(
                f'''SELECT userid FROM current_mutes WHERE serverid = {guild.id} AND mutefinish >= {current_time}''')

    @unmuter.before_loop
    async def before_umuter(self):
        await self.glaceon.wait_until_ready()

    @unbanner.before_loop
    async def before_unbanner(self):
        await self.glaceon.wait_until_ready()


def setup(glaceon):
    glaceon.add_cog(UnCog(glaceon))
