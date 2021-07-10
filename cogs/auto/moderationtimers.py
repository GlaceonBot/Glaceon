import pathlib
from datetime import datetime

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
            # connect to the sqlite database for data
            db = self.glaceon.sql_server_connection.cursor()
            # find which prefix matches this specific server id
            db.execute(
                '''SELECT userid FROM current_bans WHERE serverid = %s AND banfinish <= %s AND banfinish <> %s''',
                (guild.id, current_time, -1))
            member_line = db.fetchone()
            if member_line:
                db.execute(
                    '''DELETE FROM current_bans WHERE serverid = %s AND banfinish <= %s AND banfinish <> %s''',
                    (guild.id, current_time, -1))
                member = self.glaceon.get_user(member_line[0])
                self.glaceon.sql_server_connection.commit()
                try:
                    await guild.unban(member)
                    await member.send(f"You have been unbanned in {guild}!")
                except discord.Forbidden:
                    pass

    @tasks.loop(seconds=5.0)
    async def unmuter(self):
        current_time = int(datetime.utcnow().timestamp())
        for guild in self.glaceon.guilds:
            # connect to the sqlite database for prefixes
            db = self.glaceon.sql_server_connection.cursor()
            # find which prefix matches this specific server id
            db.execute(
                '''SELECT userid FROM current_mutes WHERE serverid = %s AND mutefinish <= %s AND mutefinish <> %s''',
                (guild.id, current_time, -1))
            member_line = db.fetchone()
            if member_line:
                db.execute(
                    '''DELETE FROM current_mutes WHERE serverid = %s AND mutefinish <= %s AND mutefinish <> %s''',
                    (guild.id, current_time, -1))
                member = guild.get_member(member_line[0])
                muted_role = discord.utils.get(guild.roles, name="Muted")
                self.glaceon.sql_server_connection.commit()
                try:
                    await member.remove_roles(muted_role)
                    await member.send(f"You have been unmuted in {guild}!")
                except discord.Forbidden:
                    pass

    @unmuter.before_loop
    async def before_umuter(self):
        await self.glaceon.wait_until_ready()

    @unbanner.before_loop
    async def before_unbanner(self):
        await self.glaceon.wait_until_ready()


def setup(glaceon):
    glaceon.add_cog(UnCog(glaceon))
