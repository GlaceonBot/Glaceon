"""This is a collection of helper functions for the Glaceon discord bot"""


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
    db = await get_sql_cursor(glaceon.sql_server_connection)
    # make sure everything is set up correctly
    await db.execute('''CREATE TABLE IF NOT EXISTS prefixes
                   (serverid BIGINT, prefix TEXT)''')
    # find which prefix matches this specific server id
    await db.execute(f'''SELECT prefix FROM prefixes WHERE serverid = {sid}''')
    # fetch the prefix
    custom_prefix = await db.fetchone()
    # if the custom prefix exists, then send it back, otherwise return the default one
    if custom_prefix:
        return str(custom_prefix[0]), *ping_prefixes
    else:
        return default_prefix, *ping_prefixes
