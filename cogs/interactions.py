import discord
import os
from discord.ext import commands
import requests
from discord import Embed
import random
import aiosqlite
from prettytable import PrettyTable

TENOR_API_KEY = os.getenv("TENOR")




class Interactions(commands.Cog): 
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        async with aiosqlite.connect("database.db") as db:
                    async with db.cursor() as cursor:
                        await cursor.execute("""CREATE TABLE IF NOT EXISTS INTERACTIONS(
            USER1_ID BIGINT NOT NULL,
            USER2_ID BIGINT NOT NULL,
            NUM_KISSES BIGINT,
            NUM_HUGS BIGINT,
            NUM_CUDDLES BIGINT,
            NUM_SLAPS BIGINT,
            NUM_PATS BIGINT,
            NUM_LICKS BIGINT)""")
                        
                  
    @commands.command(description="kisses a member")
    async def kiss(self, ctx, *, member: discord.Member):
        async with aiosqlite.connect("database.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT count(*) FROM INTERACTIONS where USER1_ID = ? and USER2_ID = ?", (ctx.author.id, member.id))
                db_result = await cursor.fetchone()
                if db_result[0] == 0:
                    await cursor.execute(f"INSERT INTO INTERACTIONS VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (ctx.author.id, member.id, 0, 0, 0, 0, 0, 0,))
                await db.commit()
                await cursor.execute("SELECT NUM_KISSES FROM INTERACTIONS where USER1_ID = ? and USER2_ID = ?", (ctx.author.id, member.id))
                results = await cursor.fetchone()
                kisses = results[0] + 1
                await cursor.execute("UPDATE INTERACTIONS set NUM_KISSES = NUM_KISSES + 1 where USER1_ID = ? and USER2_ID = ?", (ctx.author.id, member.id))
                await db.commit()
        apikey = TENOR_API_KEY
        lmt = 20
        ckey = "my_test_app"  
        search_term = "anime kiss gif"
        r = requests.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (search_term, apikey, ckey,  lmt))
        random_data = random.choice(r.json()["results"])
        img = random_data["media_formats"]["gif"]["url"]
        embed = Embed(title=f"{ctx.author.name} kisses {member.name} !", color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_image(url=img)
        if ctx.author.avatar != None:
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        else:
            embed.set_author(name=ctx.author.name)
        embed.set_footer(text=f"{kisses} kisses")
        await ctx.send(embed=embed)
        
        
    @commands.command(description="hugs a member")
    async def hug(self, ctx, *, member: discord.Member):
        async with aiosqlite.connect("database.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT count(*) FROM INTERACTIONS where USER1_ID = ? and USER2_ID = ?", (ctx.author.id, member.id))
                db_result = await cursor.fetchone()
                if db_result[0] == 0:
                    await cursor.execute(f"INSERT INTO INTERACTIONS VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (ctx.author.id, member.id, 0, 0, 0, 0, 0, 0,))
                await db.commit()
                await cursor.execute("SELECT NUM_HUGS FROM INTERACTIONS where USER1_ID = ? and USER2_ID = ?", (ctx.author.id, member.id))
                results = await cursor.fetchone()
                hugs = results[0] + 1
                await cursor.execute("UPDATE INTERACTIONS set NUM_HUGS = NUM_HUGS + 1 where USER1_ID = ? and USER2_ID = ?", (ctx.author.id, member.id))
                await db.commit()
        apikey = TENOR_API_KEY
        lmt = 20
        ckey = "my_test_app"  
        search_term = "anime hug gif"
        r = requests.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (search_term, apikey, ckey,  lmt))
        random_data = random.choice(r.json()["results"])
        img = random_data["media_formats"]["gif"]["url"]
        embed = Embed(title=f"{ctx.author.name} hugs {member.name} !", colour=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_image(url=img)
        if ctx.author.avatar != None:
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        else:
            embed.set_author(name=ctx.author.name)
        embed.set_footer(text=f"{hugs} hugs")
        await ctx.send(embed=embed)
        
    @commands.command(description="cuddles a member")
    async def cuddle(self, ctx, *, member: discord.Member):
        async with aiosqlite.connect("database.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT count(*) FROM INTERACTIONS where USER1_ID = ? and USER2_ID = ?", (ctx.author.id, member.id))
                db_result = await cursor.fetchone()
                if db_result[0] == 0:
                    await cursor.execute(f"INSERT INTO INTERACTIONS VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (ctx.author.id, member.id, 0, 0, 0, 0, 0, 0,))
                await db.commit()
                await cursor.execute("SELECT NUM_CUDDLES FROM INTERACTIONS where USER1_ID = ? and USER2_ID = ?", (ctx.author.id, member.id))
                results = await cursor.fetchone()
                cuddles = results[0] + 1
                await cursor.execute("UPDATE INTERACTIONS set NUM_CUDDLES = NUM_CUDDLES + 1 where USER1_ID = ? and USER2_ID = ?", (ctx.author.id, member.id))
                await db.commit()
        apikey = TENOR_API_KEY
        lmt = 20
        ckey = "my_test_app"  
        search_term = "anime cuddle gif"
        r = requests.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (search_term, apikey, ckey,  lmt))
        random_data = random.choice(r.json()["results"])
        img = random_data["media_formats"]["gif"]["url"]
        embed = Embed(title=f"{ctx.author.name} cuddles {member.name} !", colour=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_image(url=img)
        if ctx.author.avatar != None:
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        else:
            embed.set_author(name=ctx.author.name)
        embed.set_footer(text=f"{cuddles} cuddles")
        await ctx.send(embed=embed)
        
    @commands.command(description="slaps a member")
    async def slap(self, ctx, *, member: discord.Member):
        async with aiosqlite.connect("database.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT count(*) FROM INTERACTIONS where USER1_ID = ? and USER2_ID = ?", (ctx.author.id, member.id))
                db_result = await cursor.fetchone()
                if db_result[0] == 0:
                    await cursor.execute(f"INSERT INTO INTERACTIONS VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (ctx.author.id, member.id, 0, 0, 0, 0, 0, 0,))
                await db.commit()
                await cursor.execute("SELECT NUM_SLAPS FROM INTERACTIONS where USER1_ID = ? and USER2_ID = ?", (ctx.author.id, member.id))
                results = await cursor.fetchone()
                slaps = results[0] + 1
                await cursor.execute("UPDATE INTERACTIONS set NUM_SLAPS = NUM_SLAPS + 1 where USER1_ID = ? and USER2_ID = ?", (ctx.author.id, member.id))
                await db.commit()
        apikey = TENOR_API_KEY
        lmt = 20
        ckey = "my_test_app"  
        search_term = "anime slap gif"
        r = requests.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (search_term, apikey, ckey,  lmt))
        random_data = random.choice(r.json()["results"])
        img = random_data["media_formats"]["gif"]["url"]
        embed = Embed(title=f"{ctx.author.name} slaps {member.name} !", colour=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_image(url=img)
        if ctx.author.avatar != None:
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        else:
            embed.set_author(name=ctx.author.name)
        embed.set_footer(text=f"{slaps} slaps")
        await ctx.send(embed=embed)
    
    @commands.command(description="pat a member")
    async def pat(self, ctx, *, member: discord.Member):
        async with aiosqlite.connect("database.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT count(*) FROM INTERACTIONS where USER1_ID = ? and USER2_ID = ?", (ctx.author.id, member.id))
                db_result = await cursor.fetchone()
                if db_result[0] == 0:
                    await cursor.execute(f"INSERT INTO INTERACTIONS VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (ctx.author.id, member.id, 0, 0, 0, 0, 0, 0,))
                await db.commit()
                await cursor.execute("SELECT NUM_PATS FROM INTERACTIONS where USER1_ID = ? and USER2_ID = ?", (ctx.author.id, member.id))
                results = await cursor.fetchone()
                pats = results[0] + 1
                await cursor.execute("UPDATE INTERACTIONS set NUM_PATS = NUM_PATS + 1 where USER1_ID = ? and USER2_ID = ?", (ctx.author.id, member.id))
                await db.commit()
        apikey = TENOR_API_KEY
        lmt = 20
        ckey = "my_test_app"  
        search_term = "anime pat gif"
        r = requests.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (search_term, apikey, ckey,  lmt))
        random_data = random.choice(r.json()["results"])
        img = random_data["media_formats"]["gif"]["url"]
        embed = Embed(title=f"{ctx.author.name} pats {member.name} !", colour=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_image(url=img)
        if ctx.author.avatar != None:
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        else:
            embed.set_author(name=ctx.author.name)
        embed.set_footer(text=f"{pats} pats")
        await ctx.send(embed=embed)
        
    @commands.command(description="licks a member")
    async def lick(self, ctx, *, member: discord.Member):
        async with aiosqlite.connect("database.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT count(*) FROM INTERACTIONS where USER1_ID = ? and USER2_ID = ?", (ctx.author.id, member.id))
                db_result = await cursor.fetchone()
                if db_result[0] == 0:
                    await cursor.execute(f"INSERT INTO INTERACTIONS VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (ctx.author.id, member.id, 0, 0, 0, 0, 0, 0,))
                await db.commit()
                await cursor.execute("SELECT NUM_LICKS FROM INTERACTIONS where USER1_ID = ? and USER2_ID = ?", (ctx.author.id, member.id))
                results = await cursor.fetchone()
                licks = results[0] + 1
                await cursor.execute("UPDATE INTERACTIONS set NUM_LICKS = NUM_LICKS + 1 where USER1_ID = ? and USER2_ID = ?", (ctx.author.id, member.id))
                await db.commit()
        apikey = TENOR_API_KEY
        lmt = 20
        ckey = "my_test_app"  
        search_term = "anime lick someone gif"
        r = requests.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (search_term, apikey, ckey,  lmt))
        random_data = random.choice(r.json()["results"])
        img = random_data["media_formats"]["gif"]["url"]
        embed = Embed(title=f"{ctx.author.name} licks {member.name} !", colour=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_image(url=img)
        if ctx.author.avatar != None:
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        else:
            embed.set_author(name=ctx.author.name)
        embed.set_footer(text=f"{licks} licks")
        await ctx.send(embed=embed)
        
        
    @commands.command(description="Returns back count of kisses")
    async def count_kisses(self, ctx, *, member: discord.Member = None):
        if member == None:
            member = ctx.author
        async with aiosqlite.connect("database.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT NUM_KISSES FROM INTERACTIONS where USER1_ID = ?", (member.id,))
                results = await cursor.fetchall()
                kisses = results
                await cursor.execute("SELECT USER2_ID FROM INTERACTIONS where USER1_ID = ?", (member.id,))
                results = await cursor.fetchall()
                users_ids = results
                x = PrettyTable()
                users = [await self.bot.fetch_user(int(user[0])) for user in users_ids]
                list_of_users = [user.name for user in users if int(kisses[users.index(user)][0]) != 0]
                list_of_kisses = [kiss[0] for kiss in kisses if int(kiss[0]) != 0]
                if len(list_of_kisses) == 0:
                    await ctx.send("{} hasn't kissed anyone yet.".format(member.name))
                else:
                    x.add_column("User", list_of_users)
                    x.add_column("Number of Kisses", list_of_kisses)
                    embed = Embed(colour=ctx.author.color, timestamp=ctx.message.created_at)
                    embed.add_field(name="Kisses", value=x, inline=False)
                    await ctx.send(embed=embed)
                
    @commands.command(description="Returns back count of Hugs")
    async def count_hugs(self, ctx, *, member: discord.Member = None):
        if member == None:
            member = ctx.author
        async with aiosqlite.connect("database.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT NUM_HUGS FROM INTERACTIONS where USER1_ID = ?", (member.id,))
                results = await cursor.fetchall()
                hugs = results
                await cursor.execute("SELECT USER2_ID FROM INTERACTIONS where USER1_ID = ?", (member.id,))
                results = await cursor.fetchall()
                users_ids = results
                x = PrettyTable()
                users = [await self.bot.fetch_user(int(user[0])) for user in users_ids]
                list_of_users = [user.name for user in users if int(hugs[users.index(user)][0]) != 0]
                list_of_hugs = [hug[0] for hug in hugs if int(hug[0]) != 0]
                if len(list_of_hugs) == 0:
                    await ctx.send("{} hasn't hugged anyone yet.".format(member.name))
                else:
                    x.add_column("User", list_of_users)
                    x.add_column("Number of Hugs", list_of_hugs)
                    embed = Embed(colour=ctx.author.color, timestamp=ctx.message.created_at)
                    embed.add_field(name="Hugs", value=x, inline=False)
                    await ctx.send(embed=embed)

    @commands.command(description="Returns back count of cuddles")
    async def count_cuddles(self, ctx, *, member: discord.Member = None):
        if member == None:
            member = ctx.author
        async with aiosqlite.connect("database.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT NUM_CUDDLES FROM INTERACTIONS where USER1_ID = ?", (member.id,))
                results = await cursor.fetchall()
                cuddles = results
                await cursor.execute("SELECT USER2_ID FROM INTERACTIONS where USER1_ID = ?", (member.id,))
                results = await cursor.fetchall()
                users_ids = results
                x = PrettyTable()
                users = [await self.bot.fetch_user(int(user[0])) for user in users_ids]
                list_of_users = [user.name for user in users if int(cuddles[users.index(user)][0]) != 0]
                list_of_cuddles = [cuddle[0] for cuddle in cuddles if int(cuddle[0]) != 0]
                if len(list_of_cuddles) == 0:
                    await ctx.send("{} hasn't cuddled anyone yet.".format(member.name))
                else:
                    x.add_column("User", list_of_users)
                    x.add_column("Number of cuddles", list_of_cuddles)
                    embed = Embed(colour=ctx.author.color, timestamp=ctx.message.created_at)
                    embed.add_field(name="Cuddles", value=x, inline=False)
                    await ctx.send(embed=embed)
    
    @commands.command(description="Returns back count of slaps")
    async def count_slaps(self, ctx, *, member: discord.Member = None):
        if member == None:
            member = ctx.author
        async with aiosqlite.connect("database.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT NUM_SLAPS FROM INTERACTIONS where USER1_ID = ?", (member.id,))
                results = await cursor.fetchall()
                slaps = results
                await cursor.execute("SELECT USER2_ID FROM INTERACTIONS where USER1_ID = ?", (member.id,))
                results = await cursor.fetchall()
                users_ids = results
                x = PrettyTable()
                users = [await self.bot.fetch_user(int(user[0])) for user in users_ids]
                list_of_users = [user.name for user in users if int(slaps[users.index(user)][0]) != 0]
                list_of_slaps = [slap[0] for slap in slaps if int(slap[0]) != 0]
                if len(list_of_slaps) == 0:
                    await ctx.send("{} hasn't slapped anyone yet.".format(member.name))
                else:
                    x.add_column("User", list_of_users)
                    x.add_column("Number of Slaps", list_of_slaps)
                    embed = Embed(colour=ctx.author.color, timestamp=ctx.message.created_at)
                    embed.add_field(name="Slaps", value=x, inline=False)
                    await ctx.send(embed=embed)
    
    @commands.command(description="Returns back count of pats")
    async def count_pats(self, ctx, *, member: discord.Member = None):
        if member == None:
            member = ctx.author
        async with aiosqlite.connect("database.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT NUM_PATS FROM INTERACTIONS where USER1_ID = ?", (member.id,))
                results = await cursor.fetchall()
                pats = results
                await cursor.execute("SELECT USER2_ID FROM INTERACTIONS where USER1_ID = ?", (member.id,))
                results = await cursor.fetchall()
                users_ids = results
                x = PrettyTable()
                users = [await self.bot.fetch_user(int(user[0])) for user in users_ids]
                list_of_users = [user.name for user in users if int(pats[users.index(user)][0]) != 0]
                list_of_pats = [pat[0] for pat in pats if int(pat[0]) != 0]
                if len(list_of_pats) == 0:
                    await ctx.send("{} hasn't patted anyone yet.".format(member.name))
                else:
                    x.add_column("User", list_of_users)
                    x.add_column("Number of Pats", list_of_pats)
                    embed = Embed(colour=ctx.author.color, timestamp=ctx.message.created_at)
                    embed.add_field(name="Pats", value=x, inline=False)
                    await ctx.send(embed=embed)
    
    @commands.command(description="Returns back count of licks")
    async def count_licks(self, ctx, *, member: discord.Member = None):
        if member == None:
            member = ctx.author
        async with aiosqlite.connect("database.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT NUM_LICKS FROM INTERACTIONS where USER1_ID = ?", (member.id,))
                results = await cursor.fetchall()
                licks = results
                await cursor.execute("SELECT USER2_ID FROM INTERACTIONS where USER1_ID = ?", (member.id,))
                results = await cursor.fetchall()
                users_ids = results
                x = PrettyTable()
                users = [await self.bot.fetch_user(int(user[0])) for user in users_ids]
                list_of_users = [user.name for user in users if int(licks[users.index(user)][0]) != 0]
                list_of_licks = [lick[0] for lick in licks if int(lick[0]) != 0]
                if len(list_of_licks) == 0:
                    await ctx.send("{} hasn't licked anyone yet.".format(member.name))
                else:
                    x.add_column("User", list_of_users)
                    x.add_column("Number of licks", list_of_licks)
                    embed = Embed(colour=ctx.author.color, timestamp=ctx.message.created_at)
                    embed.add_field(name="Licks", value=x, inline=False)
                    await ctx.send(embed=embed)
                    
                
        
    ########################################## ERROR SECTION ###############################
    @kiss.error
    async def kiss_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = Embed(title="ERROR!", colour=ctx.author.color, timestamp=ctx.message.created_at)
            embed.add_field(name="KISS ERROR", value="Please mention a specific member to kiss them !")
            await ctx.send(embed=embed)
            

    @hug.error
    async def hug_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = Embed(title="ERROR!", colour=ctx.author.color, timestamp=ctx.message.created_at)
            embed.add_field(name="HUG ERROR", value="Please mention a specific member to hug them !")
            await ctx.send(embed=embed)

    @cuddle.error
    async def cuddle_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = Embed(title="ERROR!", colour=ctx.author.color, timestamp=ctx.message.created_at)
            embed.add_field(name="CUDDLE ERROR!", value="Please mention a specific member to cuddle them !")
            await ctx.send(embed=embed)

    @slap.error
    async def slep_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = Embed(title="ERROR!", colour=ctx.author.color, timestamp=ctx.message.created_at)
            embed.add_field(name="SLAP ERROR!", value="Please mention a specific member to slep them !")
            await ctx.send(embed=embed)
            
    @pat.error
    async def pat_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = Embed(title="ERROR!", colour=ctx.author.color, timestamp=ctx.message.created_at)
            embed.add_field(name="PAT ERROR!", value="Please mention a specific member to pat them !")
            await ctx.send(embed=embed)
    
    @lick.error
    async def lick_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = Embed(title="ERROR!", colour=ctx.author.color, timestamp=ctx.message.created_at)
            embed.add_field(name="LICK ERROR!", value="Please mention a specific member to lick them !")
            await ctx.send(embed=embed)
            
    #################################################
def setup(bot):
    bot.add_cog(Interactions(bot)) 
