import subprocess
import discord
from discord.ext import commands

class Tools(commands.Cog):
  def __init__(self, glaceon):
    self.glaceon = glaceon
  
  @commands.command(aliases=['exec', 'eval', 'ssh', 'rsh', 'sh'])
  @commands.is_owner()
  async def shell(self, ctx, *args):
    process = subprocess.run(args, capture_output=True)
    await ctx.send(f"stdout: ```{process.stdout.decode('utf8')}```\n stderr: ```{process.stderr.decode('utf8')}```\n exitcode: `{process.returncode}`\n command: `{' '.join(process.args)}` ")
    

def setup(glaceon):
    glaceon.add_cog(Tools(glaceon))
