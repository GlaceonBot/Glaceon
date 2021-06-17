# TODO configurable regex antiswear

import pathlib
import re

from discord.ext import commands

lax_regex = [

]

normal_regex = [

]

tough_regex = [

]

path = pathlib.PurePath()
embed_color = 0xadd8e6


class AntiSwear(commands.Cog):

    @commands.Cog.listener()
    async def on_message(self, message):
        pass
        re.search("", "")


def setup(glaceon):
    glaceon.add_cog(AntiSwear(glaceon))
