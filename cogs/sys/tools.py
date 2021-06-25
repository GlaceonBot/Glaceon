import subprocess
import discord
from discord.ext import commands

class Tools(commands.Cog):
  def __init__(self, glaceon):
    self.glaceon = glaceon
  
  @commands.command(aliases=['exec', 'eval', 'ssh', 'rsh', 'sh'])
  @commands.is_owner()
  async def shell(self, ctx, *args):
    maxmsglength = 3994
    process = subprocess.run(args, capture_output=True)
    stdout = process.stdout.decode('utf8')
    stderr = proccess.stderr.decode('utf8')
    if process.returncode == 0:
      stdout_chunks = [stdout[i:i + maxmsglength] for i in range(0, len(stdout), maxmsglength)]
        for stdout_part in stdout_chunks:
            await ctx.send("```\n" + stdout_part + "\n```")
        await ctx.send(f"Exit code: {process.returncode}\n Command: {' '.join(process.args)}")
    else:
      stderr_chunks = [stderr[i:i + maxmsglength] for i in range(0, len(stderr), maxmsglength)]
        for stderr_part in stderr_chunks:
            await ctx.send("```\n" + stderr_part + "\n```")
        await ctx.send(f"Exit code: {process.returncode}\n Command: {' '.join(process.args)}")
    for output_discord_ified in outputs:
      await ctx.send(output_discord_ified)
    

def setup(glaceon):
    glaceon.add_cog(Tools(glaceon))
