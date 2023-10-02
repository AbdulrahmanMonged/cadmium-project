import discord
import os
import logging
from discord import Embed
from discord.ext import commands, pages, ipc
from urllib.parse import urlparse
import asyncio
import aiosqlite
import psycopg


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.ipc = ipc.Server(self, secret_key = "Bodyy")
        
        async def on_ipc_error(self, endpoint, error):
            print(endpoint, "raised", error)

#------------------------------ VARIABLES ------------------------#
TOKEN = os.getenv("TOKEN")

DB_URI = os.getenv("DB_URI")
db_uri = urlparse(DB_URI)

host = db_uri.hostname
database = db_uri.path[1:]
user = db_uri.username
password = db_uri.password
port= db_uri.port

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def get_prefix(client, ctx):
    async with await psycopg.AsyncConnection.connect(host=host, dbname=database, user=user, password=password, port=port) as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT GUILD_PREFIX FROM GUILD WHERE GUILD_ID = %s", (ctx.guild.id,))
            results = await cursor.fetchone()
            return results[0].strip(" ")
        
        
default_prefix = "#"
prefix = get_prefix
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = Bot(command_prefix=prefix,
                   help_command=None,
                   intents=intents,
                   activity=discord.Activity(name="/help",
                                             type=discord.ActivityType.watching))

#------------------------- LOGGING -------------------------#

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


#------------------------- APP -------------------------#

    
@bot.event
async def on_ready():
    print(f"We have logged in {bot.user}. ")
    async with await psycopg.AsyncConnection.connect(host=host, dbname=database, user=user, password=password, port=port) as db:
        async with db.cursor() as cursor:
            table_query = """CREATE TABLE IF NOT EXISTS GUILD(
                                    GUILD_NAME CHAR(255) NOT NULL ,
                                    GUILD_ID bigserial NOT NULL UNIQUE,
                                    GUILD_PREFIX CHAR(255) NOT NULL,
                                    ERROR_LOGS TEXT) 
                                    """
                                
            error_logs = "none"
            await cursor.execute(table_query)
            async for guild in bot.fetch_guilds(limit=150):
                await cursor.execute("SELECT count(*) FROM GUILD where GUILD_ID = %s", (guild.id,))
                db_result = await cursor.fetchone()
                if db_result[0] == 0:
                    await cursor.execute(f"INSERT INTO GUILD VALUES (%s ,%s ,%s , %s)", (guild.name, guild.id, default_prefix ,error_logs))
            await db.commit()
            
    async with await psycopg.AsyncConnection.connect(host=host, dbname=database, user=user, password=password, port=port) as db:
        async with db.cursor() as cursor:
            table_query = """CREATE TABLE IF NOT EXISTS USERS(
                                    USER_ID bigserial NOT NULL UNIQUE,
                                    USER_LVL BIGINT NOT NULL) 
                                    """
                                
            await cursor.execute(table_query)
            async for guild in bot.fetch_guilds():
                members = [user for user in guild.members]
                for member in members:
                    await cursor.execute("SELECT count(*) FROM USERS where USER_ID = %s", (member.id,))
                    db_result = await cursor.fetchone()
                    if db_result[0] == 0:
                        await cursor.execute(f"INSERT INTO USERS VALUES (%s ,%s)", (member.id, 0))    
            await db.commit()
    
    async with await psycopg.AsyncConnection.connect(host=host, dbname=database, user=user, password=password, port=port) as db:
        async with db.cursor() as cursor:
            table_query = """CREATE TABLE IF NOT EXISTS COMMANDS(
                                    COMMAND_NAME CHAR(255) NOT NULL,
                                    COMMAND_DESCRIPTION CHAR(255) NOT NULL) 
                                    """
                                
            await cursor.execute(table_query)
            commands = [command for command in bot.walk_commands()]
            for command in commands:
                await cursor.execute("SELECT count(*) FROM COMMANDS where COMMAND_NAME = %s", (command.name,))
                db_result = await cursor.fetchone()
                if db_result[0] == 0:
                    await cursor.execute(f"INSERT INTO COMMANDS VALUES (%s ,%s)", (command.name, command.description.title()))    
            await db.commit()

@bot.event
async def on_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    error_channel = await bot.fetch_channel(1130150210195165237)
    embed = Embed(title="Error", color=ctx.author.color, timestamp=ctx.message.created_at)
    embed.add_field(name=f"Error occured at `{ctx.channel.name}`, `{ctx.channel.id}`\n where guild id is `{ctx.guild.id}` and name `{ctx.guild.name}`", value=f"Error:```py\n{str(error)}```\nThe command used is: ```\n{ctx.message.content}```", inline=False)
    await error_channel.send(embed=embed)      
    

@bot.event
async def on_member_join(member):
    async with await psycopg.AsyncConnection.connect(host=host, dbname=database, user=user, password=password, port=port) as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT count(*) FROM USERS where USER_ID = %s", (member.id,))
            db_result = await cursor.fetchone()
            if db_result[0] == 0:
                await cursor.execute(f"INSERT INTO USERS VALUES (%s, %s)", (member.id, 0))
            await db.commit()
    


@bot.event
async def on_guild_join(guild):
    async with await psycopg.AsyncConnection.connect(host=host, dbname=database, user=user, password=password, port=port) as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT count(*) FROM GUILD where GUILD_ID = %s", (guild.id,))
            db_result = await cursor.fetchone()
            if db_result[0] == 0:
                await cursor.execute(f"INSERT INTO GUILD VALUES (%s , %s, %s, %s)", (guild.name, guild.id, default_prefix))
            await db.commit()
    
     
    
@bot.slash_command(description="Help command")
async def help(ctx: discord.ApplicationContext):
    async with await psycopg.AsyncConnection.connect(host=host, dbname=database, user=user, password=password, port=port) as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT guild_prefix FROM GUILD where GUILD_ID = %s", (ctx.guild.id,))
            results = await cursor.fetchone()
            current_prefix = results[0].strip(" ")
    list1 = []
    commands = [command for command in bot.walk_commands()]
    n = len(commands)
    x1 = n/6 - n//6
    z2=0
    for num in range(1,(n//6)+1):
        x = num*6
        list2 = [m for m in commands[z2:x]]
        z2 = x
        list1.append(list2)
    if x1 > 0:
        list2 = [item for item in commands[int((n-(x1*6))):]]
        list1.append(list2)  
    help_command = [Embed(title=f"Page {num+1}") for num in range(len(list1))] 
    for embed in help_command:
        for command in list1[help_command.index(embed)]:
            embed.add_field(name=f"{current_prefix}{str(command.name)}", value=str(command.description).title(), inline=True)
            if ctx.author.avatar != None:
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
            else:
                embed.set_author(name=ctx.author.name)

    """Demonstrates using the paginator with the default options."""
    paginator = pages.Paginator(pages=help_command)
    await paginator.respond(ctx.interaction, ephemeral=False)
    
@bot.ipc.route()
async def get_guild_count(data):
    return len(bot.guilds)

#######
bot.ipc.start()
bot.load_extension('cogs.interactions')
bot.load_extension('cogs.moderation')
bot.load_extension('cogs.utility')
bot.load_extension('cogs.music')
bot.run(TOKEN)

 
