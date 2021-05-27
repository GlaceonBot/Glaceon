import pathlib

import discord
from discord.ext import commands

path = pathlib.PurePath()


class TagSystem(commands.Cog):
    """Glaceon tag system"""

    def __init__(self, glaceon):
        self.glaceon = glaceon

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
                db = self.glaceon.sql_server_connection.cursor()

                db.execute('''CREATE TABLE IF NOT EXISTS tags
                                    (serverid BIGINT, tagname TEXT, tagcontent TEXT)''')
                db.execute("""SELECT tagcontent FROM tags WHERE serverid = %s AND tagname = %s""", (sid, t))
                factoid = db.fetchone()
                if factoid:
                    factoids.append(factoid[0])
                else:
                    await ctx.send(f"tag `{t}` not found!", delete_after=15)
                    errors = True
                    break
            else:
                pings.append(t.mention)
        if errors is False:
            if factoids is not []:
                embed = discord.Embed(colour=self.glaceon.embedcolor, description="\n\n".join(factoids))
                embed.set_footer(text=f"I am a bot, i will not respond to you | Request by {ctx.author}")
                await ctx.send("Please refer to the below information:" + " ".join(pings), embed=embed)
            else:
                await ctx.send("You need to specify a tag!", delete_after=5)

    @commands.command(aliases=["tmanage", "tagmanage", "tadd", "tm", "ta"])
    @commands.has_permissions(manage_messages=True)
    async def tagadd(self, ctx, name, *, contents):
        """add or edit tags"""
        await ctx.message.delete()
        serverid = ctx.guild.id
        db = self.glaceon.sql_server_connection.cursor()
        if len(contents) > 1900:
            await ctx.send("That factoid is too long!")
        else:
            db.execute('''CREATE TABLE IF NOT EXISTS tags
                                    (serverid BIGINT, tagname TEXT, tagcontent TEXT)''')
            db.execute(f'''SELECT serverid FROM tags WHERE serverid = %s AND tagname = %s''', (serverid, name))
            if db.fetchone():
                db.execute("""UPDATE tags SET tagcontent = %s WHERE serverid = %s AND tagname = %s""",
                           (contents, serverid, name))
            else:
                db.execute("""INSERT INTO tags(serverid, tagname, tagcontent) VALUES (%s,%s,%s)""",
                           (serverid, name, contents))
            self.glaceon.sql_server_connection.commit()
            await ctx.send(f"Tag added with name `{name}` and contents `{contents}`", delete_after=10)

    @commands.command(aliases=["trm", "tagremove"])
    @commands.has_permissions(manage_messages=True)
    async def tagdelete(self, ctx, name):
        """Remove a tag"""
        await ctx.message.delete()
        sid = ctx.guild.id
        db = self.glaceon.sql_server_connection.cursor()

        db.execute('''CREATE TABLE IF NOT EXISTS tags
                                    (serverid BIGINT, tagname TEXT, tagcontent TEXT)''')
        db.execute("""DELETE FROM tags WHERE serverid = %s AND tagname = %s""", (sid, name))
        self.glaceon.sql_server_connection.commit()
        await ctx.send(f"tag `{name}` deleted", delete_after=10)

    @commands.command(aliases=["tlist", "tl", "taglist"])
    async def tagslist(self, ctx):
        """list the tags on this server"""
        await ctx.message.delete()
        sid = ctx.guild.id
        db = self.glaceon.sql_server_connection.cursor()

        db.execute('''CREATE TABLE IF NOT EXISTS tags
                                    (serverid BIGINT, tagname TEXT, tagcontent TEXT)''')
        db.execute("""SELECT tagname FROM tags WHERE serverid = %s""", (sid,))
        factoids = db.fetchall()
        if factoids:
            await ctx.send('`' + "`, `".join([i for (i,) in factoids]) + '`')
        else:
            await ctx.send(f"This guild has no tags!")


def setup(glaceon):
    glaceon.add_cog(TagSystem(glaceon))
