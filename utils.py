"""This is a collection of helper functions for the Glaceon discord bot"""
import asyncio
import os
from dotenv import load_dotenv

import aiomysql
from discord.ext import commands

load_dotenv()


async def connect_to_sql_server():
    sql_server_connection = await aiomysql.create_pool(host=os.getenv('SQLserverhost'),
                                                       user=os.getenv('SQLusername'),
                                                       password=os.getenv('SQLpassword'),
                                                       db=os.getenv('SQLdatabase'),
                                                       autocommit=True,
                                                       echo=True)
    return sql_server_connection


loop = asyncio.get_event_loop()
sql_server_connection = loop.run_until_complete(connect_to_sql_server())


async def get_sql_cursor(pool):
    connection = await pool.acquire()
    cursor = await connection.cursor()
    return cursor


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
    db = await get_sql_cursor(sql_server_connection)
    # find which prefix matches this specific server id
    await db.execute(f'''SELECT prefix FROM prefixes WHERE serverid = {sid}''')
    # fetch the prefix
    custom_prefix = await db.fetchone()
    # if the custom prefix exists, then send it back, otherwise return the default one
    del db  # deletes database object
    if custom_prefix:
        return str(custom_prefix[0]), *ping_prefixes
    else:
        return default_prefix, *ping_prefixes


class CommandDisabled(commands.CheckFailure):
    pass


def disableable():
    async def predicate(ctx):
        db = await get_sql_cursor(sql_server_connection)
        state = await db.execute("""SELECT state FROM disabled_commands WHERE commandname = %s AND serverid = %s""",
                                 (ctx.command.qualified_name, ctx.guild.id))
        print(state)
        if state is None:
            state = 1
        if state == 0:
            raise CommandDisabled("This command is disabled.")
        del db
        return state == 1

    return commands.check(predicate)
