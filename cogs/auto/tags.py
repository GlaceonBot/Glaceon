import pathlib

import mysql.connector
import discord
from discord.ext import commands

path = pathlib.PurePath()
embedcolor = 0xadd8e6


class TagSystem(commands.Cog):
    """Glaceon tag system"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["t"])
    async def tag(self, ctx, *tags):
        """Call a tag. (or two, or ten)"""
        await ctx.message.delete()
        errors = False
        factoids = []
        pings = []
        sid = ctx.guild.id
        for t in tags:
            id = None
            if t != id:
                db = await mysql.connector.connect(path / "system/tags.db")
                cur = await db.execute("""SELECT tagcontent FROM tags WHERE serverid = %s AND tagname = %s""", (sid, t))
                factoid = await cur.fetchone()
                if factoid is not None:
                    factoids.append(factoid[0])
                else:
                    await ctx.send(f"tag `{t}` not found!")
                    errors = True
                    break
            else:
                pings.append(t.mention)
        if errors is False:
            embed = discord.Embed(colour=embedcolor, description="\n\n".join(factoids))
            embed.set_footer(text=f"I am a bot, i will not respond to you | Request by {ctx.author}")
            await ctx.send("Please refer to the below information" + " ".join(pings), embed=embed)

    @commands.command(aliases=["tmanage", "tagmanage", "tadd", "tm", "ta"])
    @commands.has_permissions(manage_messages=True)
    async def tagadd(self, ctx, name, *, contents):
        """add or edit tags"""
        await ctx.message.delete()
        serverid = ctx.guild.id
        async with mysql.connector.connect(path / "system/tags.db") as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS tags
                                   (serverid INTEGER, tagname TEXT, tagcontent TEXT)''')
        db = await mysql.connector.connect(path / "system/tags.db")
        cur = await db.execute(f'''SELECT serverid FROM tags WHERE serverid = %s AND tagname = %s''', (serverid, name))
        if await cur.fetchone() is not None:
            await db.execute("""UPDATE tags SET tagcontent = %s WHERE serverid = %s AND tagname = %s""",
                             (contents, serverid, name))
        else:
            await db.execute("""INSERT INTO tags(serverid, tagname, tagcontent) VALUES (%s,%s,%s)""",
                             (serverid, name, contents))
        await db.commit()
        await db.close()
        await ctx.send(f"Tag added with name `{name}` and contents `{contents}`", delete_after=10)

    @commands.command(aliases=["trm", "tagremove"])
    @commands.has_permissions(manage_messages=True)
    async def tagdelete(self, ctx, name):
        """Remove a tag"""
        await ctx.message.delete()
        sid = ctx.guild.id
        async with mysql.connector.connect(path / "system/tags.db") as db:
            await db.execute("""DELETE FROM tags WHERE serverid = %s AND tagname = %s""", (sid, name))
            await db.commit()
            await ctx.send(f"tag `{name}` deleted", delete_after=10)

    @commands.command(aliases=["tlist", "tl", "taglist"])
    async def tagslist(self, ctx):
        """list the tags on this server"""
        await ctx.message.delete()
        sid = ctx.guild.id
        db = await mysql.connector.connect(path / "system/tags.db")
        cur = await db.execute("""SELECT tagname FROM tags WHERE serverid = %s""", (sid,))
        factoids = await cur.fetchall()
        try:
            await ctx.send('`' + "`, `".join([i for (i,) in factoids]) + '`')
        except discord.HTTPException:
            await ctx.send(f"This guild has no tags!")


def setup(glaceon):
    glaceon.add_cog(TagSystem(glaceon))
