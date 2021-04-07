import datetime
import pathlib

from discord.ext import commands

path = pathlib.PurePath()


class Logger(commands.Cog):
    def __init__(self, glaceon):
        self.glaceon = glaceon

    @commands.Cog.listener()
    async def on_message(self, message):
        # logs
        pathlib.Path(path / f'logs/{message.guild}/{message.channel}').mkdir(parents=True, exist_ok=True)
        day = datetime.datetime.today().strftime('%Y-%m-%d')
        logfile = open(path / f'logs/{message.guild}/{message.channel}/{day}.txt', 'a+', encoding='utf-32')
        try: logfile.write(
            f"{message.author} said: {message.content}\n"
        )
        except UnicodeEncodeError:
            logfile.write(
                "The above message also contained a Discord emote that could not be translated to ASCII.  Sorry for the inconvinence.\n")

        logfile.close()

    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message):
        # logs
        pathlib.Path(path / f'logs/{message.guild}/{message.channel}').mkdir(parents=True, exist_ok=True)
        day = datetime.datetime.today().strftime('%Y-%m-%d')
        logfile = open(path / f'logs/{message.guild}/{message.channel}/{day}.txt', 'a+', encoding='utf-32')
        try:
            logfile.write(
                f"{message.author} edited their message from: {message_before.content} to: {message.content}\n"
            )
        except UnicodeEncodeError:
            logfile.write(
                "The above message also contained a Discord emote that could not be translated to ASCII.  Sorry for the inconvinence.\n")
        logfile.close()


def setup(glaceon):
    glaceon.add_cog(Logger(glaceon))
