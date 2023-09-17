import discord
from discord.ext import commands
from wavelink.ext import spotify
import wavelink
import datetime
import os

ID = os.getenv("ID")
KEY = os.getenv("KEY")

class ControlPanel(discord.ui.View):
    def __init__(self, vc, ctx):
        super().__init__()
        self.vc = vc
        self.ctx = ctx
    
    @discord.ui.button(label="Resume/Pause", style=discord.ButtonStyle.blurple)
    async def resume_and_pause(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user == self.ctx.author:
            return await interaction.response.send_message("You can't do that. run the command yourself to use these buttons", ephemeral=True)
        for child in self.children:
            child.disabled = False
        if self.vc.is_paused():
            await self.vc.resume()
            await interaction.message.edit(content="Resumed", view=self)
        else:
            await self.vc.pause()
            await interaction.message.edit(content="Paused", view=self)

    @discord.ui.button(label="Queue", style=discord.ButtonStyle.blurple)
    async def queue(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user == self.ctx.author:
            return await interaction.response.send_message("You can't do that. run the command yourself to use these buttons", ephemeral=True)
        for child in self.children:
            child.disabled = False
        button.disabled = True
        if self.vc.queue.is_empty:
            return await interaction.response.send_message("the queue is empty smh", ephemeral=True)
    
        em = discord.Embed(title="Queue")
        queue = self.vc.queue.copy()
        songCount = 0

        for song in queue:
            songCount += 1
            em.add_field(name=f"Song Num {str(songCount)}", value=f"`{song}`")
        await interaction.message.edit(embed=em, view=self)
    
    @discord.ui.button(label="Skip", style=discord.ButtonStyle.blurple)
    async def skip(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user == self.ctx.author:
            return await interaction.response.send_message("You can't do that. run the command yourself to use these buttons", ephemeral=True)
        for child in self.children:
            child.disabled = False
        button.disabled = True
        if self.vc.queue.is_empty:
            return await interaction.response.send_message("the queue is empty smh", ephemeral=True)

        try:
            next_song = self.vc.queue.get()
            await self.vc.play(next_song)
            await interaction.message.edit(content=f"Now Playing `{next_song}`", view=self)
        except Exception:
            return await interaction.response.send_message("The queue is empty!", ephemeral=True)
    
    @discord.ui.button(label="Disconnect", style=discord.ButtonStyle.red)
    async def disconnect(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user == self.ctx.author:
            return await interaction.response.send_message("You can't do that. run the command yourself to use these buttons", ephemeral=True)
        for child in self.children:
            child.disabled = True
        await self.vc.disconnect()
        await interaction.message.edit(content="Disconnect :P", view=self)

class Music(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.loop.create_task(self.node_connect())

    async def node_connect(self):
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.bot, host='lavalink.ordinaryender.my.eu.org', port=443, password='ordinarylavalink', https=True, spotify_client=spotify.SpotifyClient(client_id=ID, client_secret=KEY))

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f'Node <{node.identifier}> is ready!')

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.YouTubeTrack, reason):
        try:
            ctx = player.ctx
            vc: player = ctx.voice_client
            
        except discord.HTTPException:
            interaction = player.interaction
            vc: player = interaction.guild.voice_client
        
        if vc.loop:
            return await vc.play(track)
        
        if vc.queue.is_empty:
            return await vc.disconnect()

        next_song = vc.queue.get()
        await vc.play(next_song)
        try:
            await ctx.send(f"Now playing: {next_song.title}")
        except discord.HTTPException:
            await interaction.send(f"Now playing: {next_song.title}")

    @commands.command(description="plays some music")
    async def play(self, ctx: commands.Context, *, search: wavelink.YouTubeTrack):
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first")
        else:
            vc: wavelink.Player = ctx.voice_client
            
        if vc.queue.is_empty and not vc.is_playing():
            await vc.play(search)
            await ctx.send(f'Playing `{search.title}`')          
        else:
            await vc.queue.put_wait(search)
            await ctx.send(f'Added `{search.title}` to the queue...')
        vc.ctx = ctx
        try:
            if vc.loop: return
        except Exception:
            setattr(vc, "loop", False)
        
    @commands.command(description="Panel to control your musuc")
    async def panel(self, ctx: commands.Context):
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first")
        else:
            vc: wavelink.Player = ctx.voice_client
        if not vc.is_playing():
            return await ctx.send("first play some music")
        
        em = discord.Embed(title="Music Panel", description="control the bot by clicking on the buttons below")
        view = ControlPanel(vc, ctx)
        await ctx.send(embed=em, view=view)
        
    
    @commands.command(description="pauses current playing")
    async def pause(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("im not even in a vc.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first")
        else:
            vc: wavelink.Player = ctx.voice_client
        if not vc.is_playing():
            return await ctx.send("first play some music")

        await vc.pause()
        await ctx.send("paused your music.")
        
    @commands.command(description="resumes music")
    async def resume(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("im not even in a vc.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first")
        else:
            vc: wavelink.Player = ctx.voice_client
        if vc.is_playing():
            return await ctx.send("music is already playing!")

        await vc.resume()
        await ctx.send("the music is back on!")
        
    @commands.command(description="skips current song")
    async def skip(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("im not even in a vc.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first.")
        else:
            vc: wavelink.Player = ctx.voice_client
        if not vc.is_playing():
            return await ctx.send("first play some music")
        
        try:
            next_song = vc.queue.get()
            await vc.play(next_song)
            await ctx.send(content=f"Now Playing `{next_song}`")
        except Exception:
            return await ctx.send("The queue is empty!")
        
        await vc.stop()
        await ctx.send("stopped the song")
        
    @commands.command(description="Disconnect from current channel")
    async def disconnect(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("im not even in a vc.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first")
        else:
            vc: wavelink.Player = ctx.voice_client
        
        await vc.disconnect()
        await ctx.send("cya laterr")
        
    @commands.command(description="loop current song")
    async def loop(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("im not even in a vc.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first.")
        vc: wavelink.Player = ctx.voice_client
        if not vc.is_playing():
            return await ctx.send("first play some music.")
        try: 
            vc.loop ^= True
        except:
            setattr(vc, "loop", False)
        if vc.loop:
            return await ctx.send("looping.")
        else:
            return await ctx.send("no more loop time.")

    @commands.command(description="gets current queue")
    async def queue(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("im not even in a vc...")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first.")
        vc: wavelink.Player = ctx.voice_client

        if vc.queue.is_empty:
            return await ctx.send("the queue is empty.")
        
        em = discord.Embed(title="Queue")
        
        queue = vc.queue.copy()
        songCount = 0
        for song in queue:
            songCount += 1
            em.add_field(name=f"Song Num {str(songCount)}", value=f"`{song}`")
            
        await ctx.send(embed=em)

    @commands.command(description="Control volume")
    async def volume(self, ctx: commands.Context, volume: int):
        if not ctx.voice_client:
            return await ctx.send("im not even in a vc...")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first.")
        else:
            vc: wavelink.Player = ctx.voice_client
        if not vc.is_playing():
            return await ctx.send("first play some music.")
        
        if volume > 100:
            return await ctx.send('thats way to high')
        elif volume < 0:
            return await ctx.send("thats way to low")
        await ctx.send(f"Set the volume to `{volume}%`")
        return await vc.set_volume(volume)

    @commands.command(description="Shows now playing")
    async def nowplaying(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("im not even in a vc...")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first")
        else:
            vc: wavelink.Player = ctx.voice_client
        
        if not vc.is_playing(): 
            return await ctx.send("nothing is playing")

        em = discord.Embed(title=f"Now Playing {vc.track.title}", description=f"Artist: {vc.track.author}")
        em.add_field(name="Duration", value=f"`{str(datetime.timedelta(seconds=vc.track.length))}`")
        em.add_field(name="Extra Info", value=f"Song URL: [Click Me]({str(vc.track.uri)})")
        return await ctx.send(embed=em)

    @commands.command(description="Play from spotify, url is required")
    async def splay(self, ctx: commands.Context, *, search: str):
        if not ctx.voice_client:
                vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first.")
        else:
            vc: wavelink.Player = ctx.voice_client
            
        if vc.queue.is_empty and not vc.is_playing():
            try:
                track = await spotify.SpotifyTrack.search(query=search, return_first=True)
                await vc.play(track)
                await ctx.send(f'Playing `{track.title}`')
            except Exception as e:
                await ctx.send("Please enter a spotify **song url**.")
                return print(e)
        else:
            await vc.queue.put_wait(search)
            await ctx.send(f'Added `{search.title}` to the queue...')
        vc.ctx = ctx
        try:
            if vc.loop: return
        except Exception:
            setattr(vc, "loop", False)    
        
def setup(bot):
    bot.add_cog(Music(bot))
    
