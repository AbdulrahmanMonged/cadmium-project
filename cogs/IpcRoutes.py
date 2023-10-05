from typing import Dict
from discord.ext import commands, ipc
from discord.ext.ipc.server import Server
from discord.ext.ipc.objects import ClientPayload


class IpcRoutes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, "ipc"):
            bot.ipc = ipc.Server(self.bot, secret_key="Ahmed")

    async def cog_load(self) -> None:
        await self.bot.ipc.start()

    async def cog_unload(self) -> None:
        await self.bot.ipc.stop()
        self.bot.ipc = None
        
    @Server.route(name = "get_guilds")
    async def get_bot_guilds(self, data) -> dict:
        guilds = [guild.id for guild in self.bot.guilds]  
        return guilds

def setup(bot):
    bot.add_cog(IpcRoutes(bot))