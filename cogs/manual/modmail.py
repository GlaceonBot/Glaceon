import asyncio
import pathlib

from utils import prefixgetter
import discord
from discord.ext import commands

path = pathlib.PurePath()


class ModCommmunications(commands.Cog):
    """Communicate with the mods and for the mods"""

    def __init__(self, glaceon):
        self.glaceon = glaceon
        self._last_member = None

    async def wait_for_DM(self, ctx, dm_channel, mod_channel):
        last_message = ctx.message
        prefixes = await prefixgetter(self.glaceon, ctx.message)

        def dm_check(message):
            return message.channel == dm_channel

        while last_message.content.lower() != prefixes[0] + "close":
            last_message = await self.glaceon.wait_for('message', timeout=None, check=dm_check)
            if last_message.author != ctx.me and not last_message.content.lower().startswith(prefixes[0] + "close"):
                try:
                    await mod_channel.send(str(last_message.author) + ": " +
                                           last_message.content.replace("@everyone", "@ everyone").replace("@here",
                                                                                                           "@ here"))
                except discord.HTTPException:
                    await dm_channel.send("The modmail channel in the server was deleted. Report closed.")
                    return

    async def wait_for_moderator_message(self, ctx, dm_channel, mod_channel):
        last_message = ctx.message
        prefixes = await prefixgetter(self.glaceon, ctx.message)

        def moderator_send_check(message):
            return message.channel == mod_channel

        while last_message.content.lower() != prefixes[0] + "close":
            last_message = await self.glaceon.wait_for('message', timeout=None, check=moderator_send_check)
            if last_message.author != ctx.me and not last_message.content.lower().startswith(prefixes[0] + "close"):
                await dm_channel.send(f"**{last_message.author.top_role}**: " +
                                      last_message.content.replace("@everyone", "@ everyone").replace("@here",
                                                                                                      "@ here"))
        await mod_channel.delete()
        await dm_channel.send("Report closed!")

    @commands.command(aliases=['report'])
    @commands.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    async def modmail(self, ctx, *, message=None):
        """Sends a message TO the moderators"""
        global modmail_category
        modmail_category = None
        await ctx.message.delete()
        modmail_dm = await ctx.message.author.create_dm()
        for category in ctx.guild.categories:
            if category.name == 'modmail' or category.name == 'mail':
                modmail_category = category
        if modmail_category is None:
            modmail_category_overwrites = {
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True,
                                                          read_message_history=True),
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False)
            }
            modmail_category = await ctx.guild.create_category("modmail", overwrites=modmail_category_overwrites)
        modmail_channel = await ctx.guild.create_text_channel(f"{ctx.author.name}-{ctx.author.discriminator}",
                                                              category=modmail_category)
        if message:
            await modmail_dm.send("You: " + message)
            await modmail_channel.send(str(ctx.author) + ": " + message)
        await modmail_dm.send("Thank you for reporting this, we should respond shortly!")
        from_dm_task = asyncio.create_task(self.wait_for_DM(ctx, modmail_dm, modmail_channel))
        from_channel_task = asyncio.create_task(self.wait_for_moderator_message(ctx, modmail_dm, modmail_channel))

        await from_dm_task
        await from_channel_task


def setup(glaceon):
    glaceon.add_cog(ModCommmunications(glaceon))
