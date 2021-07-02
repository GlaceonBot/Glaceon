import subprocess
import discord
from discord.ext import commands

class Tools(commands.Cog):
  def __init__(self, glaceon):
    self.glaceon = glaceon
  
  @commands.command(aliases=['exec', 'eval', 'ssh', 'rsh', 'sh'])
  @commands.is_owner()
  async def shell(self, ctx, *, args):
    """This command is used to execute shell commands on Glaceon's host server. Only <@!788222689126776832> and <@!545463550802395146> can use it."""
    maxmsglength = 1988
    process = subprocess.run(['bash', '-c', args], capture_output=True)
    stdout = process.stdout.decode('utf16')
    stderr = process.stderr.decode('utf16')
    if process.returncode == 0:
      stdout_chunks = [stdout[i:i + maxmsglength] for i in range(0, len(stdout), maxmsglength)]
      for stdout_part in stdout_chunks:
       await ctx.send("```\n" + stdout_part + "\n```")
      await ctx.send(f"Exit code: {process.returncode}\nCommand: {' '.join(args).replace('bash -c ', ' ', 1)}")
    else:
      stderr_chunks = [stderr[i:i + maxmsglength] for i in range(0, len(stderr), maxmsglength)]
      for stderr_part in stderr_chunks:
       await ctx.send("```\n" + stderr_part + "\n```")
      await ctx.send(f"Exit code: {process.returncode}\nCommand: {' '.join(args).replace('bash -c ', ' ', 1)}")
    
    @commands.command()
    @commands.is_owner()
    async def update(self, ctx):
      ctx.send("Updating bot!")
      os.system("./update.sh")
      
def setup(glaceon):
    glaceon.add_cog(Tools(glaceon))
