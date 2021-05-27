# TODO AntiRaid coming soon :D

from discord.ext import commands


class Antiraid(commands.Cog):
    """Antiraid coming soon :D"""

    def __init__(self, glaceon):
        self.glaceon = glaceon


def setup(glaceon):
    glaceon.add_cog(Antiraid(glaceon))
