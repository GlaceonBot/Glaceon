from discord.ext import tasks, commands


class UnCog(commands.Cog):
    def __init__(self, bot):
        self.index = 0
        self.bot = bot

    def cog_unload(self):
        self.unbanner.cancel()

    @tasks.loop(seconds=5.0)
    async def unbanner(self):
        pass

    @tasks.loop(seconds=5.0)
    async def unmuter(self):
        pass


def setup(glaceon):
    glaceon.add_cog(UnCog(glaceon))
