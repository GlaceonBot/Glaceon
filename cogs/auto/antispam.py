from discord.ext import commands


class Antispam(commands.Cog):
    """Antispam coming soon :D"""
    def __init__(self, glaceon):
        self.glaceon = glaceon

    @commands.Cog.listener()
    async def on_message(self, ctx):
        sender = ctx.author.id
        pass


def setup(glaceon):
    glaceon.add_cog(Antispam(glaceon))
