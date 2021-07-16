# TODO make the code website-compatible, somehow

import datetime
import pathlib

import emoji
from discord.ext import commands

import utils

path = pathlib.PurePath()  # get path


async def getattachments(message):  # this was good as a function so i could use it in fstrings
    if message.attachments is not None:  # check if there are attachments
        for attachment in message.attachments:  # loop through all the attachments
            return '\n' + attachment.url  # add the attachment URL on a new line
        else:  # if there arent any attachments send an empty string
            return ""


class Logger(commands.Cog):  # Logger class
    def __init__(self, glaceon):  # initializes Glaceon
        self.glaceon = glaceon

    async def is_logging_enabled(self, message):
        connection = await self.glaceon.sql_server_pool.acquire()
        db = await connection.cursor()
        try:
            await db.execute(f'''SELECT serverid FROM settings WHERE serverid = %s AND setting = %s''',
                             (message.guild.id, "message_logging"))
        except AttributeError:
            return 1
        settings = await db.fetchone()
        await db.close()
        connection.close()
        self.glaceon.sql_server_pool.release(connection)
        if settings:
            return settings[0]
        else:
            return 1

    @commands.Cog.listener()
    async def on_message(self, message):
        if await self.is_logging_enabled(message) == 1:
            # logs
            if message.guild is None:  # For DMs set the guild ID to one
                guildid = "DirectMessages"
            else:
                guildid = message.guild.id  # otherwise use the guild ID
            if message.channel is None:
                channelid = message.author.id
            else:
                channelid = message.channel.id
            pathlib.Path(path / f'logs/{guildid}/{channelid}').mkdir(parents=True,
                                                                     exist_ok=True)  # Make the server folder
            day = datetime.datetime.today().strftime('%Y-%m-%d')  # get current date for logging
            logfile = open(path / f'logs/{guildid}/{channelid}/{day}.txt', 'a+',
                           encoding='utf-16')  # set the system to log to a specific file in a specific place
            logfile.write(
                f"{message.author} said: {emoji.demojize(message.content)} {await getattachments(message)}\n"
            )  # write the output demojized

            logfile.close()  # close the log file

    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message):
        if await self.is_logging_enabled(message) == 1:
            # logs
            if message.guild is None:  # For DMs set the guild ID to one
                guildid = "DirectMessages"
            else:
                guildid = message.guild.id  # otherwise use the guild ID
            if message.channel is None:
                channelid = message.author.id
            else:
                channelid = message.channel.id
            pathlib.Path(path / f'logs/{guildid}/{channelid}').mkdir(parents=True,
                                                                     exist_ok=True)  # make the folder for that server
            day = datetime.datetime.today().strftime('%Y-%m-%d')  # get current date for logging
            logfile = open(path / f'logs/{guildid}/{channelid}/{day}.txt', 'a+',
                           encoding='utf-16')  # set the system to log to a specific file in a specific place
            logfile.write(
                f"{message.author} edited their message from: {emoji.demojize(message_before.content)}"
                f"{await getattachments(message_before)} to: {emoji.demojize(message.content)} {await getattachments(message)}\n"
            )  # write the output demojized
            logfile.close()  # close logfile


def setup(glaceon):  # setup function for dpy
    glaceon.add_cog(Logger(glaceon))
