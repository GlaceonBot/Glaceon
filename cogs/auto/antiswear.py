#TODO configurable regex antiswear

import pathlib
from discord.ext import commands

path = pathlib.PurePath()
embedcolor = 0xadd8e6


class AntiSwear(commands.Cog):
    pass

def setup(glaceon):
    glaceon.add_cog(AntiSwear(glaceon))
