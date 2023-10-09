import discord
import os
from discord.ext import commands
import psycopg
import time


DB_URI = os.getenv("DB_URI")


class Moderation(commands.Cog): 
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(help="""Changes current server's prefix
                      Permissions Required: `Manage Server`
                      
                      Ex:
                      {0}setprefix `!`""",
                      description="Changes Current server's Prefix")
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self, ctx: commands.Context, *, new_prefix: str):
        async with await psycopg.AsyncConnection.connect(DB_URI) as db:
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE GUILD set GUILD_PREFIX = %s WHERE GUILD_ID = %s", (new_prefix, ctx.guild.id))
                await db.commit()
                await ctx.send("Prefix updated to `{0}`".format(new_prefix))
                
                
    @commands.command(help="""Clears the chat.
                      Permissions Required: `Manage Messages`
                      
                      Ex:
                      {0}clear
                      {0}clear all
                      {0}clear 100""",
                      description="Clears the chat")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, input = None):
        def is_me(m):
            m = True
            return m
        if input == None:
            input = 10
        elif not input.isdigit():
            if input.lower() == "all":
                input = 250
        else:
            input = int(input)
        deleted = await ctx.channel.purge(limit=input, check=is_me)
        message = await ctx.send(f'Deleted {len(deleted)} message(s) `This message will disappear after 3 seconds.`')
        time.sleep(3)
        await message.delete()
        
    @commands.command(help="""kicks a user.
                      Permissions Required: `Kick Members`
                      It can kick Many Members
                      The preferred way is using Mention
                      
                      Ex:
                      {0}kick `user id`
                      {0}kick `user mention`""", description="Kicks a member or Many Members")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, members: commands.Greedy[discord.Member], *, reason:str = None):
        for member in members:
            await member.kick(reason=reason)
        if reason != None:
            await ctx.reply("**{0} has been kicked successfully For reason: {1}**".format(", ".join(member.name for member in members),reason))
        else:
            await ctx.reply("**{0} has been kicked successfully**".format(", ".join(member.name for member in members)))

        
    @commands.command(help="""bans a user.
                      Permissions Required: `Ban Members`
                      It can Ban Many Members
                      The preferred way is using Mention
                      
                      Ex:
                      {0}ban `user id`
                      {0}ban `user mention`""", description="Bans a member or Many Members")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, members: commands.Greedy[discord.Member],*,reason: str = None):
        for member in members:
            if reason != None:
                await member.ban(delete_message_days=7, reason="banned by {0}\n for reason: {1}".format(ctx.author, "No Reason provided"))
            else:
                await member.ban(delete_message_days=7, reason="banned by {0}\n for reason: {1}".format(ctx.author, reason))     
        if reason == None:       
            await ctx.reply("**{0} has been banned successfully**".format(", ".join(member.name for member in members)))
        else:
            await ctx.reply("**{0} has been banned successfully for reason: {1}**".format(", ".join(member.name for member in members)), reason)
        
        
#------------------------- ERROR HANDLING --------------------#
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