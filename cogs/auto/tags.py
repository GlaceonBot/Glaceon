import pathlib

import aiosqlite
from discord.ext import commands

path = pathlib.PurePath()


class TagSystem(commands.Cog):
    """Glaceon tag system"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["tmanage", "tagmanage"])
    @commands.has_permissions(manage_messages=True)
    async def tm(self, ctx, name, *, contents=None):
        """add or edit tags"""
        await ctx.message.delete()
        serverid = ctx.guild.id
        async with aiosqlite.connect(path / "system/tags.db") as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS tags
                                   (serverid INTEGER, tagname TEXT, tagcontent TEXT)''')
        db = await aiosqlite.connect(path / "system/tags.db")
        if contents is None:
            await db.execute("""DELETE FROM tags WHERE tagname = ?""", (name,))
        cur = await db.execute(f'''SELECT serverid FROM tags WHERE serverid = ? AND tagname = ?''', (serverid, name))
        if await cur.fetchone() is not None:
            await db.execute("""UPDATE tags SET tagcontent = ? WHERE serverid = ? AND tagname = ?""",
                             (contents, serverid, name))
        else:
            await db.execute("""INSERT INTO tags(serverid, tagname, tagcontent) VALUES (?,?,?)""",
                             (serverid, name, contents))
        await db.commit()
        await db.close()
        await ctx.send(f"Tag added with name `{name}` and contents `{contents}`", delete_after=10)

    @commands.command(aliases=["t"])
    async def tag(self, ctx, *tags):
        """Call a tag. (or two, or ten)"""
        await ctx.message.delete()
        errors = False
        factoids = []
        sid = ctx.guild.id
        for t in tags:
            db = await aiosqlite.connect(path / "system/tags.db")
            cur = await db.execute("""SELECT tagcontent FROM tags WHERE serverid = ? AND tagname = ?""", (sid, t))
            factoid = await cur.fetchone()
            if factoid is not None:
                factoids.append(factoid[0])
            else:
                await ctx.send(f"tag `{t}` not found!")
                errors = True
                break
        if errors is False:
            await ctx.send("\n\n".join(factoids))


def setup(glaceon):
    glaceon.add_cog(TagSystem(glaceon))
