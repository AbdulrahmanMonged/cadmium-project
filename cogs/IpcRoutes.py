from discord.ext import commands, ipc


class IpcRoutes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ipc.server.route(name = "get_guilds")
    async def get_bot_guilds(self, data):
        guilds = [guild.id for guild in self.bot.guilds]  
        return guilds


def setup(bot):
    bot.add_cog(IpcRoutes(bot))