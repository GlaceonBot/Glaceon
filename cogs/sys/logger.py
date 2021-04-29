import datetime
import pathlib

import emoji
from discord.ext import commands

path = pathlib.PurePath()


async def getattachments(message):
    if message.attachments is not None:
        for attachment in message.attachments:
            return '\n' + attachment.url
        else:
            return " "


class Logger(commands.Cog):
    def __init__(self, glaceon):
        self.glaceon = glaceon

    @commands.Cog.listener()
    async def on_message(self, message):
        # logs
        if message.guild is None:
            guildid = -1
        else:
            guildid = message.guild.id
        pathlib.Path(path / f'logs/{guildid}/{emoji.demojize(str(message.channel))}').mkdir(parents=True, exist_ok=True)
        day = datetime.datetime.today().strftime('%Y-%m-%d')
        logfile = open(path / f'logs/{guildid}/{emoji.demojize(str(message.channel))}/{day}.txt', 'a+', encoding='utf-16')
        logfile.write(
            f"{message.author} said: {emoji.demojize(message.content)} {await getattachments(message)}\n"
        )

        logfile.close()

    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message):
        # logs
        if message.guild is None:
            guildid = -1
        else:
            guildid = message.guild.id
        pathlib.Path(path / f'logs/{guildid}/{emoji.demojize(str(message.channel))}').mkdir(parents=True, exist_ok=True)
        day = datetime.datetime.today().strftime('%Y-%m-%d')
        logfile = open(path / f'logs/{guildid}/{emoji.demojize(str(message.channel))}/{day}.txt', 'a+', encoding='utf-16')
        logfile.write(
            f"{message.author} edited their message from: {emoji.demojize(message_before.content)}" 
        f"{getattachments(message_before)} to: {emoji.demojize(message.content)} {await getattachments(message)}\n"
        )
        logfile.close()


def setup(glaceon):
    glaceon.add_cog(Logger(glaceon))
