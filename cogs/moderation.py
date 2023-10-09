import discord
import os
from discord.ext import commands
import psycopg
import time


DB_URI = os.getenv("DB_URI")


class Moderation(commands.Cog): 
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(description="""Changes current server's prefix
                      Ex:
                      #setprefix `!`""")
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self, ctx: commands.Context, *, new_prefix: str):
        async with await psycopg.AsyncConnection.connect(DB_URI) as db:
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE GUILD set GUILD_PREFIX = %s WHERE GUILD_ID = %s", (new_prefix, ctx.guild.id))
                await db.commit()
                await ctx.send("Prefix updated to `{}`".format(new_prefix))
                
                
    @commands.command(description="""Clears the chat.
                      Ex:
                      #clear
                      #clear all
                      #clear 100""")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, input = None):
        def is_me(m):
            m = True
            return m
        try:
            if input.lower() == "all":
                input = 250
        except Exception as e:
            if input == None:
                input = 10
        finally:
            deleted = await ctx.channel.purge(limit=input, check=is_me)
            message = await ctx.send(f'Deleted {len(deleted)} message(s) `This message will disappear after 3 seconds.`')
            time.sleep(3)
            await message.delete()
        
    @commands.command(description="""kicks a user.
                      Ex:
                      #kick 
                      #kick `user name`
                      #kick `user id`
                      #kick `user mention`""")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, *, member: discord.Member):
        await member.kick()
        await ctx.reply("**{0.name} has been kicked successfully**".format(member))
        
    @commands.command(description="""bans a user.
                      Ex:
                      #ban 
                      #ban `user name`
                      #ban `user id`
                      #ban `user mention`""")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member,*,reason: str = "Banned."):
        await member.ban(delete_message_days=7, reason="Fuck off! ~banned by {0}~ for reason: {1}".format(ctx.author, reason))
        await ctx.reply("**{0.name} has been banned successfully**".format(member))
        
        
#------------------------- ERRORS --------------------#
    @setprefix.error
    async def setprefix_error(self, ctx, error):
        await ctx.send("You don't have the permission to implement this command.")
        
    @clear.error
    async def clear_error(self, ctx, error):
        await ctx.send("You don't have the permission to implement this command.")
        
    @kick.error
    async def kick_error(self, ctx, error):
        await ctx.send("You don't have the permission to implement this command.")
    
    @ban.error
    async def ban_error(self, ctx, error):
        await ctx.send("You don't have the permission to implement this command.")
        
        
def setup(bot):
    bot.add_cog(Moderation(bot)) 