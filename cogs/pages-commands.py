import os
import discord
from discord import Embed
from discord.commands import SlashCommandGroup
from discord.ext import commands, pages
import psycopg
DB_URI = os.getenv("DB_URI")


class PageTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_commands(self, cog_name, current_prefix , ctx) -> list:
        cog = self.bot.get_cog(f'{cog_name}')
        emoji = self.bot.get_emoji(1159303926454169680)
        list1 = []
        commands = [command for command in cog.get_commands()]
        n = len(commands)
        x1 = n/3 - n//3
        z2=0
        for num in range(1,(n//3)+1):
            x = num*3
            list2 = [m for m in commands[z2:x]]
            z2 = x
            list1.append(list2)
        if x1 > 0:
            list2 = [item for item in commands[int((n-(x1*3))):]]
            list1.append(list2)  
        help_command = [Embed(title=f"Page {num+1}") for num in range(len(list1))] 
        
        for embed in help_command:
            for command in list1[help_command.index(embed)]:
                embed.add_field(name=f"{current_prefix}{str(command.name)}", value="{0} {1}".format(emoji ,str(command.description).title()), inline=True)
                if ctx.author.avatar != None:
                    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
                else:
                    embed.set_author(name=ctx.author.name)
        return help_command
        
    
    @commands.slash_command(description="Help command")
    async def help(self, ctx: discord.ApplicationContext):
        async with await psycopg.AsyncConnection.connect(DB_URI) as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT guild_prefix FROM GUILD where GUILD_ID = %s", (ctx.guild.id,))
                results = await cursor.fetchone()
                current_prefix = results[0].strip(" ")
        page_buttons = [
            pages.PaginatorButton(
                "first", label="<<-", style=discord.ButtonStyle.green
            ),
            pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.green),
            pages.PaginatorButton(
                "page_indicator", style=discord.ButtonStyle.gray, disabled=True
            ),
            pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.green),
            pages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.green),
        ]
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Invite Bot To the Server!", row=2, style=discord.ButtonStyle.link, url='https://discord.com/api/oauth2/authorize?client_id=1130152470627229858&permissions=18855442771062&scope=bot'))
        cogs = ['Interactions', 'Moderation', 'Music', 'Utility']
        emoji = ['😙', '⚒', '🎶', '⚙' ]
        page_groups = [
            pages.PageGroup(
                pages=self.get_commands(f'{cog}', current_prefix , ctx),
                label=f"{cog} Group page.",
                emoji = emoji[cogs.index(cog)],
                description=f"This page has {cog} Commands.",
                custom_buttons=page_buttons,
                use_default_buttons=False,
                custom_view=view,
            ) for cog in cogs]
        paginator = pages.Paginator(pages=page_groups,
                                    show_menu=True,
                                    show_indicator=True,
                                    use_default_buttons=False,
                                    custom_buttons=page_buttons,
                                    custom_view=view)
        await paginator.respond(ctx.interaction, ephemeral=False)


def setup(bot):
    bot.add_cog(PageTest(bot))