from discord.ext import commands, ipc
from discord.ext.ipc.server import Server
from discord.ext.ipc.server import ClientPayload


class IpcRoutes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, "ipc"):
            bot.ipc = ipc.Server(self.bot, host='0.0.0.0' ,secret_key="Bodyy")
    async def cog_load(self) -> None:
        await self.bot.ipc.start()

    async def cog_unload(self) -> None:
        await self.bot.ipc.stop()
        self.bot.ipc = None
        
    @Server.route(name = "get_guilds")
    async def get_bot_guilds(self, data) -> list:
        guilds = [guild.id for guild in self.bot.guilds]  
        return guilds

    @Server.route()
    async def get_user_data(self, data: ClientPayload) -> dict:
        user = self.get_user(data.user_id)
        return user._to_minimal_user_json()

def setup(bot):
    bot.add_cog(IpcRoutes(bot))
