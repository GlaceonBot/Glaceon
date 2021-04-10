from discord.ext import commands


class Antispam(commands.Cog):
    def __init__(self, glaceon):
        self.glaceon = glaceon

    @commands.Cog.listener()
    async def on_message(self, ctx):
        
        whoSent = ctx.author



def setup(glaceon):
    glaceon.add_cog(Antispam(glaceon))
