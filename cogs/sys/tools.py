import asyncio
import os

from discord.ext import commands

class Tools(commands.Cog):
    """Bot administrator tools"""

    def __init__(self, glaceon):
        self.glaceon = glaceon

    @commands.command(aliases=['exec', 'ssh', 'rsh', 'sh'])
    @commands.is_owner()
    async def shell(self, ctx, *, args):
        """This command is used to execute shell commands on Glaceon's host server. Only <@!788222689126776832> and <@!545463550802395146> can use it."""
        MAX_MSG_LENGTH = 1988

        proc = await asyncio.create_subprocess_shell(
            '/bin/bash -c  \'' + args + '\'',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await proc.communicate()

        stdout = stdout.decode('utf-8')
        stderr = stderr.decode('utf-8')

        stdout_chunks = [stdout[i:i + MAX_MSG_LENGTH] for i in range(0, len(stdout), MAX_MSG_LENGTH)]
        await ctx.send("[stdout]")
        if not stdout:
            await ctx.send("None")
        for stdout_part in stdout_chunks:
            await ctx.send("```\n" + stdout_part + "\n```")
        stderr_chunks = [stderr[i:i + MAX_MSG_LENGTH] for i in range(0, len(stderr), MAX_MSG_LENGTH)]
        await ctx.send("[stderr]")
        if not stderr:
            await ctx.send("None")
        for stderr_part in stderr_chunks:
            await ctx.send("```\n" + stderr_part + "\n```")
        await ctx.send(f"Exit code: {proc.returncode}\nCommand: {args}")

    @commands.command()
    @commands.is_owner()
    async def update(self, ctx):
        """Pull from git and restart the bot"""
        await ctx.send("Updating bot!")
        os.system("./update.sh")


def setup(glaceon):
    glaceon.add_cog(Tools(glaceon))
