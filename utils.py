"""This is a collection of helper functions for the Glaceon discord bot"""


async def get_sql_cursor(pool):
    connection = await pool.acquire()
    cursor = await connection.cursor()
    return cursor
