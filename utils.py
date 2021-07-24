"""This is a collection of helper functions for the Glaceon discord bot"""
import asyncio
import os

import aiomysql
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


async def connect_to_sql_server():
    sql_server_pool = await aiomysql.create_pool(host=os.getenv('SQLserverhost'),
                                                 user=os.getenv('SQLusername'),
                                                 password=os.getenv('SQLpassword'),
                                                 db=os.getenv('SQLdatabase'),
                                                 autocommit=True)
    return sql_server_pool


loop = asyncio.get_event_loop()
sql_server_pool = loop.run_until_complete(connect_to_sql_server())


# function to return the prefix based on a message and a bot instance
async def prefixgetter(glaceon, message):
    # set default prefix
    default_prefix = "%"
    # list of pings so that they can be used as prefixes
    ping_prefixes = [glaceon.user.mention, glaceon.user.mention.replace('@', '@!')]
    # try to get the guild id. if there isn't one, then it's a DM and uses the default prefix.
    try:
        sid = message.guild.id
    except AttributeError:
        return default_prefix
    async with sql_server_pool.acquire() as connection:
        async with connection.cursor() as db:
            # find which prefix matches this specific server id
            await db.execute(f'''SELECT prefix FROM prefixes WHERE serverid = {sid}''')
            # fetch the prefix
            custom_prefix = await db.fetchone()
    # deletes database object
    # if the custom prefix exists, then send it back, otherwise return the default one
    if custom_prefix:
        return str(custom_prefix[0]), *ping_prefixes
    else:
        return default_prefix, *ping_prefixes


class CommandDisabled(commands.CheckFailure):
    pass


def disableable():
    async def predicate(ctx):
        async with sql_server_pool.acquire() as connection:
            async with connection.cursor() as db:
                await db.execute("""SELECT state FROM disabled_commands WHERE command = %s AND guildid = %s""",
                                     (ctx.command.qualified_name, ctx.guild.id))
                state = await db.fetchone()
        if state:
            pass
        else:
            state = 1
        # deletes database object
        if state[0] == 0:
            raise CommandDisabled("This command is disabled.")
        else:
            return True

    return commands.check(predicate)
