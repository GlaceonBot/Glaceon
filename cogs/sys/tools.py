import subprocess
import discord
from discord.ext import commands

class Tools(commands.Cog):
  def __init__(self, glaceon):
    self.glaceon = glaceon
  
  @commands.command(aliases=['exec', 'eval', 'ssh', 'rsh', 'sh'])
  @commands.is_owner()
  async def shell(self, ctx, *args):
    process = subprocess.run([args, capture_output=True)
    await ctx.send(f"stdout: ```{process.stdout}```,\n stderr: ```{process.stderr}```, exitcode: `{subprocess.returncode}`")
    

def setup(glaceon):
    glaceon.add_cog(BotSystem(glaceon))
