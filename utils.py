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
                                                 autocommit=True,
                                                 echo=True)
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
    connection = await glaceon.sql_server_pool.acquire()
    db = await connection.cursor()
    # find which prefix matches this specific server id
    await db.execute(f'''SELECT prefix FROM prefixes WHERE serverid = {sid}''')
    # fetch the prefix
    custom_prefix = await db.fetchone()
    # deletes database object
    await db.close()
    connection.close()
    glaceon.sql_server_pool.release(connection)
    # if the custom prefix exists, then send it back, otherwise return the default one
    if custom_prefix:
        return str(custom_prefix[0]), *ping_prefixes
    else:
        return default_prefix, *ping_prefixes


class CommandDisabled(commands.CheckFailure):
    pass


def disableable():
    async def predicate(ctx):
        connection = await sql_server_pool.acquire()
        db = await connection.cursor()
        state = await db.execute("""SELECT state FROM disabled_commands WHERE commandname = %s AND serverid = %s""",
                                 (ctx.command.qualified_name, ctx.guild.id))
        if state is None:
            state = 1
        if state == 0:
            raise CommandDisabled("This command is disabled.")
        # deletes database object
        await db.close()
        connection.close()
        sql_server_pool.release(connection)
        if state == 0:
            return False
        else:
            return True

    return commands.check(predicate)
