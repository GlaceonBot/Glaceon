# TODO TensorFlow AntiSpam
import re

import discord
from discord.ext import commands

import utils


class Antispam(commands.Cog):
    """Antispam coming soon :D"""

    def __init__(self, glaceon):
        self.glaceon = glaceon

    async def is_invite_link_filtering_enabled(self, ctx):
        db = await utils.get_sql_cursor(self.glaceon.sql_server_connection)
        await db.execute(f'''SELECT setto FROM settings WHERE serverid = %s AND setting = %s''',
                         (ctx.guild.id, "whitelisted_invites"))  # get the current setting
        if await db.fetchone():
            try:
                await db.execute(f'''SELECT setto FROM settings WHERE serverid = %s AND setting = %s''',
                                 (ctx.guild.id, "whitelisted_invites"))
            except AttributeError:
                return 0
            settings = await db.fetchone()
            if settings:
                del db
                return settings[0]
            else:
                del db
                return 0
        else:
            del db
            return 0

    @commands.Cog.listener()
    async def on_message(self, message):
        if await self.is_invite_link_filtering_enabled(message):
            invite_links = re.findall("(?:https?://)?discord(?:app)?\.(?:com/invite|gg)/[a-zA-Z0-9]+/?",
                                      message.content)
            for invite_link in invite_links:
                try:
                    db = await utils.get_sql_cursor(self.glaceon.sql_server_connection)
                    invite = await self.glaceon.fetch_invite(invite_link)
                    db.execute(f'''SELECT inviteguild FROM whitelisted_invites WHERE hostguild = {message.guild.id}''')
                    whitelisted_invites = db.fetchall()
                    if not any(invite.guild.id in whitelisted_invite for whitelisted_invite in whitelisted_invites):
                        await message.delete()
                    del db
                except discord.Forbidden or discord.HTTPException:
                    await message.delete()


def setup(glaceon):
    glaceon.add_cog(Antispam(glaceon))
