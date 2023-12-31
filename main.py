import discord
import os
import logging
from discord import Embed
from discord.ext import commands, ipc
import asyncio
import psycopg
from discord.ext.ipc.server import Server
from discord.ext.ipc.objects import ClientPayload


#------------------------------ VARIABLES ------------------------#
TOKEN = os.getenv("TOKEN")
DB_URI = os.getenv("DB_URI")

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.ipc = ipc.Server(self, host='0.0.0.0' ,secret_key="Bodyy")
        
        
        async def on_ipc_error(self, endpoint, error):
            print(endpoint, "raised a", error)

        @Server.route()
        async def get_user_data(self, data: ClientPayload) -> dict:
            user = self.get_user(data.user_id)
            return user._to_minimal_user_json()

        @Server.route(name = "get_guilds")
        async def get_bot_guilds(self, data: ClientPayload) -> dict:
            guilds = [guild.id for guild in self.guilds]
            response = {"data":guilds}
            return response

        @Server.route(name="get_numbers")
        async def get_users_guilds_num(self, data: ClientPayload) -> dict:
            users_num = 0
            guilds_num = 0
            channels_num = 0
            for guild in self.guilds:
                guilds_num += 1
                for member in guild.members:
                    users_num += 1
                for channel in guild.channels:
                    channels_num += 1
            new_data = {"users":users_num, "guilds":guilds_num , "channels":channels_num}
            return new_data

        @Server.route(name="get_commands")
        async def get_cog_commands(self, data: ClientPayload) -> dict:
            cogs = ['Interactions', 'Moderation', 'Music', 'Utility']
            response = {cog_name:[] for cog_name in cogs}
            for cog_name in cogs:
                cog = self.get_cog(cog_name)
                for command in cog.get_commands():
                    response[cog_name] += [[command.name, command.description]]
            return response
    
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def get_prefix(client, ctx):
    async with await psycopg.AsyncConnection.connect(DB_URI) as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT GUILD_PREFIX FROM GUILD WHERE GUILD_ID = %s", (ctx.guild.id,))
            results = await cursor.fetchone()
            return results[0].strip(" ")
        
        
default_prefix = "#"
prefix = get_prefix
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
owner_id = 757387358621532164
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
    await bot.ipc.start()
    print(f"We have logged in as {bot.user}. ")
    async with await psycopg.AsyncConnection.connect(DB_URI) as db:
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
            
    async with await psycopg.AsyncConnection.connect(DB_URI) as db:
        async with db.cursor() as cursor:
            table_query = """CREATE TABLE IF NOT EXISTS USERS(
                                    USER_ID bigserial NOT NULL UNIQUE,
                                    USER_LVL BIGINT NOT NULL) 
                                    """
            
            await cursor.execute(table_query)
            for guild in bot.guilds:
                members = [user for user in guild.members]
                for member in members:
                    await cursor.execute("SELECT count(*) FROM USERS where USER_ID = %s", (member.id,))
                    db_result = await cursor.fetchone()
                    if db_result[0] == 0:
                        if member.id == owner_id:
                            await cursor.execute(f"INSERT INTO USERS VALUES (%s ,%s)", (member.id, 99)) 
                        else:
                            await cursor.execute(f"INSERT INTO USERS VALUES (%s ,%s)", (member.id, 0))    
            await db.commit()
    

@bot.event
async def on_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    error_channel = await bot.fetch_channel(1130150210195165237)
    embed = Embed(title="Error", color=ctx.author.color, timestamp=ctx.message.created_at)
    embed.add_field(name=f"Error occured at `{ctx.channel.name}`, `{ctx.channel.id}`\n where guild id is `{ctx.guild.id}` and name `{ctx.guild.name}`",
                    value=f"Error:```py\n{str(error)}```\nThe command used is: ```\n{ctx.message.content}```",
                    inline=False)
    await error_channel.send(embed=embed)      
    

@bot.event
async def on_member_join(member):
    async with await psycopg.AsyncConnection.connect(DB_URI) as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT count(*) FROM USERS where USER_ID = %s", (member.id,))
            db_result = await cursor.fetchone()
            if db_result[0] == 0:
                await cursor.execute(f"INSERT INTO USERS VALUES (%s, %s)", (member.id, 0))
            await db.commit()
    
@bot.event
async def on_guild_join(guild):
    async with await psycopg.AsyncConnection.connect(DB_URI) as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT count(*) FROM GUILD where GUILD_ID = %s", (guild.id,))
            error_logs = "none"
            db_result = await cursor.fetchone()
            if db_result[0] == 0:
                await cursor.execute(f"INSERT INTO GUILD VALUES (%s , %s, %s, %s)", (guild.name, guild.id, default_prefix, error_logs))
            await db.commit()
    async with await psycopg.AsyncConnection.connect(DB_URI) as db:
        async with db.cursor() as cursor:
            for member in guild.members:
                await cursor.execute("SELECT count(*) FROM USERS where USER_ID = %s", (member.id,))
                db_result = await cursor.fetchone()
                if db_result[0] == 0:
                    await cursor.execute(f"INSERT INTO USERS VALUES (%s, %s)", (member.id, 0))
            await db.commit()
    
     


bot.load_extension('cogs.interactions')
bot.load_extension('cogs.moderation')
bot.load_extension('cogs.utility')
bot.load_extension('cogs.music')
#bot.load_extension('cogs.IpcRoutes')
bot.load_extension('cogs.admin')
bot.load_extension('cogs.pages-commands')
bot.run(TOKEN)

 
