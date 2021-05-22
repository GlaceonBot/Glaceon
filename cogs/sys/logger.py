# TODO make the code website-compatible, somehow

import datetime
import os
import pathlib

import emoji
import mysql.connector
from discord.ext import commands

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

    def is_logging_enabled(self, message):
        with mysql.connector.connect(host=os.getenv('SQLserverhost'),
                                     user=os.getenv('SQLname'),
                                     password=os.getenv('SQLpassword'),
                                     database=os.getenv('SQLdatabase')
                                     ) as sql_server_connection:
            db = sql_server_connection.cursor()
            db.execute("""CREATE TABLE IF NOT EXISTS settingslogging 
                (serverid BIGINT, setto BIGINT)""")
            try:
                db.execute(f'''SELECT setto FROM settingslogging WHERE serverid = {message.guild.id}''')
            except AttributeError:
                return 1
            settings = db.fetchone()
            if settings:
                return settings[0]
            else:
                return 1

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.is_logging_enabled(message) == 1:
            # logs
            if message.guild is None:  # For DMs set the guild ID to one
                guildid = -1
            else:
                guildid = message.guild.id  # otherwise use the guild ID
            pathlib.Path(path / f'logs/{guildid}/{emoji.demojize(str(message.channel))}').mkdir(parents=True,
                                                                                                exist_ok=True)  # Make the server folder
            day = datetime.datetime.today().strftime('%Y-%m-%d')  # get current date for logging
            logfile = open(path / f'logs/{guildid}/{emoji.demojize(str(message.channel))}/{day}.txt', 'a+',
                           encoding='utf-16')  # set the system to log to a specific file in a specific place
            logfile.write(
                f"{message.author} said: {emoji.demojize(message.content)} {await getattachments(message)}\n"
            )  # write the output demojized

            logfile.close()  # close the log file

    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message):
        if self.is_logging_enabled(message) == 1:
            # logs
            if message.guild is None:  # For DMs set the guild ID to one
                guildid = -1
            else:
                guildid = message.guild.id  # otherwise use the guild ID
            pathlib.Path(path / f'logs/{guildid}/{emoji.demojize(str(message.channel))}').mkdir(parents=True,
                                                                                                exist_ok=True)  # make
            # the folder for that server
            day = datetime.datetime.today().strftime('%Y-%m-%d')  # get current date for logging
            logfile = open(path / f'logs/{guildid}/{emoji.demojize(str(message.channel))}/{day}.txt', 'a+',
                           encoding='utf-16')  # set the system to log to a specific file in a specific place
            logfile.write(
                f"{message.author} edited their message from: {emoji.demojize(message_before.content)}"
                f"{await getattachments(message_before)} to: {emoji.demojize(message.content)} {await getattachments(message)}\n"
            )  # write the output demojized
            logfile.close()  # close logfile


def setup(glaceon):  # setup function for dpy
    glaceon.add_cog(Logger(glaceon))
