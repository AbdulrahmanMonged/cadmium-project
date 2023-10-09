import discord
from discord.ext import commands
from wavelink.ext import spotify
import wavelink
import datetime
import os


ID = os.getenv("ID")
KEY = os.getenv("KEY")

class ControlPanel(discord.ui.View):
    def __init__(self, vc, ctx, messages):
        super().__init__()
        self.vc = vc
        self.ctx: discord.ApplicationContext = ctx
        self.main_messages = messages
    
    @discord.ui.button(label="Resume/Pause", style=discord.ButtonStyle.blurple)
    async def resume_and_pause(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user == self.ctx.author:
            return await interaction.response.send_message("You can't do that. run the command yourself to use these buttons", ephemeral=True)
        for child in self.children:
            child.disabled = False
        if self.vc.is_paused():
            await self.vc.resume()
            await interaction.response.edit_message(content="Resumed", view=self)
        else:
            await self.vc.pause()
            await interaction.response.edit_message(content="Paused", view=self)

    @discord.ui.button(label="Queue", style=discord.ButtonStyle.blurple)
    async def queue(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user == self.ctx.author:
            return await interaction.response.send_message("You can't do that. run the command yourself to use these buttons", ephemeral=True)
        for child in self.children:
            child.disabled = False
        if self.vc.queue.is_empty:
            return await interaction.response.send_message("the queue is empty smh", ephemeral=True)
    
        embed = discord.Embed(title="Queue", color=self.ctx.author.color, timestamp=self.ctx.message.created_at)
        embed.set_footer(text="Cadmium", icon_url="https://i.ibb.co/ypybNCS/image-1.png")
        if self.ctx.author.avatar != None:
            embed.set_author(name=self.ctx.author, icon_url=self.ctx.author.avatar)
        else:
            embed.set_author(name=self.ctx.author)
        queue = self.vc.queue.copy()
        songCount = 0
        
        for song in queue:
            songCount += 1
            embed.add_field(name=f"Song Num {str(songCount)}", value=f"`{song}`")
        await interaction.response.send_message(embed=embed)
    
    @discord.ui.button(label="Skip", style=discord.ButtonStyle.blurple)
    async def skip(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user == self.ctx.author:
            return await interaction.response.send_message("You can't do that. run the command yourself to use these buttons", ephemeral=True)
        for child in self.children:
            child.disabled = False
        if self.vc.queue.is_empty:
            return await interaction.response.send_message("the queue is empty smh", ephemeral=True)

        try:
            next_song = self.vc.queue.get()
            await self.vc.play(next_song)
            await interaction.response.send_message(f"Now playing: {next_song.title}")
            message = None
            for id in self.main_messages:
                if id == self.ctx.guild.id:
                    message = self.main_messages[id]
            if message != None:
                embed = message.embeds[0]
                embed.description= f"{self.vc.current.title}"
                embed.set_image(url=f"{self.vc.current.thumbnail}")
                embed.set_field_at(0, name="Duration", value=f"`{str(datetime.timedelta(milliseconds=self.vc.current.length))}`")
                embed.set_field_at(1, name="URL: ", value=f"[Click me!]({str(self.vc.current.uri)})", inline=True)
                try:
                    embed.set_field_at(2, name="Next Song: ", value=f"`{self.vc.queue.get()}`", inline=False )
                except Exception as e:
                    embed.set_field_at(2, name="Next Song: ", value=f"`{None}`", inline=False )
                await message.edit(embed=embed)
            await interaction.response.edit_message(content="SKIPPED", view=self)

        except Exception as e:
            return await interaction.response.send_message("The queue is empty!", ephemeral=True)
        
    
    @discord.ui.button(label="Disconnect", style=discord.ButtonStyle.red)
    async def disconnect(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user == self.ctx.author:
            return await interaction.response.send_message("You can't do that. run the command yourself to use these buttons", ephemeral=True)
        for child in self.children:
            child.disabled = True
        await self.vc.disconnect()
        await interaction.response.edit_message(content="Disconnect :P", view=self)

class Music(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.nodes : list[wavelink.Node] = [wavelink.Node(uri='lavalink.ordinaryender.my.eu.org:443', password='ordinarylavalink', secure=True),
                                            wavelink.Node(uri='lava1.horizxon.tech:443', password='horizxon.tech', secure=True),
                                            wavelink.Node(uri='lava2.horizxon.tech:443', password='horizxon.tech', secure=True),
                                            wavelink.Node(uri='lava3.horizxon.tech:443', password='horizxon.tech', secure=True),
                                            wavelink.Node(uri='lavalink.lexnet.cc:443', password='lexn3tl@val!nk', secure=True),
                                            wavelink.Node(uri='eu-lavalink.lexnet.cc:443', password='lexn3tl@val!nk', secure=True),
                                            wavelink.Node(uri='suki.nathan.to:443', password='adowbongmanacc', secure=True),
                                            wavelink.Node(uri='oce-lavalink.lexnet.cc:443', password='lexn3tl@val!nk', secure=True),
                                            wavelink.Node(uri='lavalink.justapie.net:443', password='pieajust12@XyZ', secure=True),
                                            wavelink.Node(uri='210.246.215.110:5269', password='sygsys-lavalink_v3', secure=False),
                                            wavelink.Node(uri='54.38.198.24:88', password='stonemusicgay', secure=False),
                                            wavelink.Node(uri='54.38.198.23:88', password='stonemusicgay', secure=False),]
        bot.loop.create_task(self.node_connect())
        self.main_messages = {}
        self.main_channels = {}

    async def node_connect(self):
        await self.bot.wait_until_ready()
        await wavelink.NodePool.connect(client=self.bot,nodes=self.nodes, spotify=spotify.SpotifyClient(client_id=ID, client_secret=KEY))
        best_node =wavelink.NodePool.get_connected_node()
        print(best_node)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f'Node <{node.id}> is ready!')


    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
        vc: payload.player = payload.player
        message = None
        for id in self.main_messages:
            if id == vc.guild.id:
                message = self.main_messages[id]
        channel = self.main_channels[vc.guild.id]

        if vc.loop:
            return await vc.play(payload.track)
        
        try:
            next_song = vc.queue.get()
        except Exception as e:
            next_song = None
        
        if not vc.queue.is_empty and not vc.is_playing() and next_song != None:
            await vc.play(next_song)
            await channel.send(f"Now playing: {next_song.title}")
            if message != None:
                embed = message.embeds[0]
                embed.description= f"{vc.current.title}"
                embed.set_image(url=f"{vc.current.thumbnail}")
                embed.set_field_at(0, name="Duration", value=f"`{str(datetime.timedelta(milliseconds=vc.current.length))}`")
                embed.set_field_at(1, name="URL: ", value=f"[Click me!]({str(vc.current.uri)})", inline=True)
                try:
                    embed.set_field_at(2, name="Next Song: ", value=f"`{vc.queue.get()}`", inline=False )
                except Exception as e:
                    embed.set_field_at(2, name="Next Song: ", value=f"`{None}`", inline=False )
                await message.edit(embed=embed)

    @commands.command(description="""Plays music From Youtube
        Ex:
        1- #play `song_name`
        2- #play `song url`
        3- #play `youtube Playlist url`
        """)
    async def play(self, ctx: commands.Context, *, search: str):
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first")
        else:
            vc: wavelink.Player = ctx.voice_client
        
        if vc.queue.is_empty and not vc.is_playing():
            try:
                tracks : wavelink.YouTubeTrack = await wavelink.YouTubeTrack.search(search)
                if len(tracks) >= 5 and len(search) >= 60:
                    message = await ctx.send(content=f"```\nADDING {len(tracks)} SONGS TO QUEUE\n```")
                    for track in tracks:
                        await vc.queue.put_wait(track)
                        if not vc.is_playing() and len(vc.queue) < 2:
                            playing = vc.queue.get()
                            await vc.play(playing)
                            await ctx.send(f'Playing `{playing.title}`')
                        await message.edit(f'```\nADDING {len(tracks)} SONGS TO QUEUE \n{len(tracks) - tracks.index(track)} SONGS LEFT TO BE ADDED\n\nAdded {track.title} to the queue...\n```')
                    await message.edit(f'```\nSUCCESSFULLY ADDED {len(tracks)} TO QUEUE \nIN: {datetime.timedelta(seconds=len(tracks))}\n\nThe Number of Songs in QUEUE {len(vc.queue)} to the queue...```')
                else:
                    await vc.queue.put_wait(tracks[0])
                    playing = vc.queue.get()
                    await vc.play(playing)
                    await ctx.send(f'Playing `{playing.title}`')
            except TypeError:
                tracks_yt : wavelink.YouTubePlaylist = await wavelink.YouTubePlaylist.search(search)
                playlist = tracks_yt.tracks
                message = await ctx.send(content=f"```\nADDING {len(playlist)} SONGS TO QUEUE\n```")
                for track in playlist:
                    await vc.queue.put_wait(track)
                    if not vc.is_playing() and len(vc.queue) < 2:
                        playing = vc.queue.get()
                        await vc.play(playing)
                        await ctx.send(f'Playing `{playing.title}`')
                    await message.edit(f'```\nADDING {len(playlist)} SONGS TO QUEUE \n{len(playlist) - playlist.index(track)} SONGS LEFT TO BE ADDED\n\nAdded {track.title} to the queue...\n```')
                await message.edit(f'```\nSUCCESSFULLY ADDED {len(playlist)} TO QUEUE \nIN: {datetime.timedelta(seconds=len(playlist))}\n\nThe Number of Songs in QUEUE {len(vc.queue)} to the queue...```')
            except Exception as e:
                ctx.send("PLEASE USE A VALID URL!")
                print(e)
        else:
            try:
                tracks : wavelink.YouTubeTrack = await wavelink.YouTubeTrack.search(search)
                if len(tracks) >= 5 and len(search) >= 60:
                    message = await ctx.send(content=f"```\nADDING {len(tracks)} SONGS TO QUEUE\n```")
                    for track in tracks:
                        await vc.queue.put_wait(track)
                        await message.edit(f'```\nADDING {len(tracks)} SONGS TO QUEUE \n{len(tracks) - tracks.index(track)} SONGS LEFT TO BE ADDED\n\nAdded {track.title} to the queue...\n```')
                else:
                    await vc.queue.put_wait(tracks[0])
                    await ctx.send(f'Added `{tracks[0].title}` to the queue...')
            except TypeError:
                tracks_yt : wavelink.YouTubePlaylist = await wavelink.YouTubePlaylist.search(search)
                playlist = tracks_yt.tracks
                message = await ctx.send(content=f"```\nADDING {len(playlist)} SONGS TO QUEUE\n```")
                for track in playlist:
                    await vc.queue.put_wait(track)
                    if not vc.is_playing() and len(vc.queue) < 2:
                        playing = vc.queue.get()
                        await vc.play(playing)
                        await ctx.send(f'Playing `{playing.title}`')
                    await message.edit(f'```\nADDING {len(playlist)} SONGS TO QUEUE \n{len(playlist) - playlist.index(track)} SONGS LEFT TO BE ADDED\n\nAdded {track.title} to the queue...\n```')
                await message.edit(f'```\nSUCCESSFULLY ADDED {len(playlist)} TO QUEUE \nIN: {datetime.timedelta(seconds=len(playlist))}\n\nThe Number of Songs in QUEUE {len(vc.queue)} to the queue...```')
            except Exception as e:
                ctx.send("PLEASE USE A VALID URL!")
                print(e)
        self.main_channels[ctx.guild.id] = ctx.channel
        try:
            if vc.loop: return
        except Exception:
            setattr(vc, "loop", False)
        
    @commands.command(description="Panel to control your musuc")
    async def panel(self, ctx: commands.Context):
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("The Bot hasn't joined any channel yet.")
        else:
            vc: wavelink.Player = ctx.voice_client
        if not vc.is_playing():
            return await ctx.send("First Play some music.")
        
        embed = discord.Embed(title="Currently Playing: ", description=f"{vc.current.title}", color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_image(url=f"{vc.current.thumbnail}")
        embed.add_field(name="Duration", value=f"`{str(datetime.timedelta(milliseconds=vc.current.length))}`")
        embed.add_field(name="URL: ", value=f"[Click me!]({str(vc.current.uri)})", inline=True)
        try:
            embed.add_field(name="Next Song: ", value=f"`{vc.queue.get()}`", inline=False )
        except Exception:
            embed.add_field(name="Next Song: ", value="`NONE`", inline=False )
        embed.set_footer(text="Cadmium", icon_url="https://i.ibb.co/ypybNCS/image-1.png")
        if ctx.author.avatar != None:
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
        else:
            embed.set_author(name=ctx.author)
        view = ControlPanel(vc, ctx, self.main_messages)
        message = await ctx.send(embed=embed, view=view)
        print(self.main_messages)
        self.main_messages[message.guild.id] = message

    @commands.command(description="Pauses current Song")
    async def pause(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("The Bot isn't in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first")
        else:
            vc: wavelink.Player = ctx.voice_client
        if not vc.is_playing():
            return await ctx.send("first play some music")

        await vc.pause()
        await ctx.send("paused your music.")
        
    @commands.command(description="Resumes current paused Song")
    async def resume(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("The Bot isn't in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first")
        else:
            vc: wavelink.Player = ctx.voice_client
        if vc.is_playing():
            return await ctx.send("music is already playing!")

        await vc.resume()
        await ctx.send("the music is back on!")
        
    @commands.command(description="Skips current song")
    async def skip(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("The Bot isn't in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first.")
        else:
            vc: wavelink.Player = ctx.voice_client
        if not vc.is_playing():
            return await ctx.send("first play some music")
        
        try:
            next_song = vc.queue.get()
            await vc.play(next_song)
            await ctx.send(f"Now playing: {next_song.title}")
            message = None
            for id in self.main_messages:
                if id == ctx.guild.id:
                    message = self.main_messages[id]
            if message != None:
                embed = message.embeds[0]
                embed.description= f"{vc.current.title}"
                embed.set_image(url=f"{vc.current.thumbnail}")
                embed.set_field_at(0, name="Duration", value=f"`{str(datetime.timedelta(milliseconds=vc.current.length))}`")
                embed.set_field_at(1, name="URL: ", value=f"[Click me!]({str(vc.current.uri)})", inline=True)
                try:
                    embed.set_field_at(2, name="Next Song: ", value=f"`{vc.queue.get()}`", inline=False )
                except Exception as e:
                    embed.set_field_at(2, name="Next Song: ", value=f"`{None}`", inline=False )
                await message.edit(embed=embed)
        except Exception:
            return await ctx.send("The queue is empty!")
        
        
    @commands.command(description="Disconnect the bot from current channel")
    async def disconnect(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("The Bot isn't in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first")
        else:
            vc: wavelink.Player = ctx.voice_client
        
        await vc.disconnect()
        await ctx.send("DISCONNECTED")
        
    @commands.command(description="Loop current song")
    async def loop(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("The Bot isn't in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first.")
        vc: wavelink.Player = ctx.voice_client
        if not vc.is_playing():
            return await ctx.send("first play some music.")
        try: 
            vc.loop = True
        except:
            setattr(vc, "loop", False)
        if vc.loop:
            return await ctx.send("looping.")
        else:
            return await ctx.send("no more loop time.")

    @commands.command(description="Gets current queue")
    async def queue(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("The Bot isn't in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first.")
        vc: wavelink.Player = ctx.voice_client

        if vc.queue.is_empty:
            return await ctx.send("the queue is empty.")
        
        embed = discord.Embed(title="Queue", color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_footer(text="Cadmium", icon_url="https://i.ibb.co/ypybNCS/image-1.png")
        if ctx.author.avatar != None:
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
        else:
            embed.set_author(name=ctx.author)
        
        queue = vc.queue.copy()
        songCount = 0
        for song in queue:
            songCount += 1
            embed.add_field(name=f"Song Num {str(songCount)}", value=f"`{song}`")
            
        await ctx.send(embed=embed)

    @commands.command(description="Control volume")
    async def volume(self, ctx: commands.Context, volume: int):
        if not ctx.voice_client:
            return await ctx.send("The Bot isn't in a voice channel.")
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
    
    @commands.command(description="""Play from spotify
                      Ex:
                      #splay `spotify_song_url`
                      #splay `spotify_playlist_url`
                      Note That the spotify version isn't stable yet and it's still Under development""")
    async def splay(self, ctx: commands.Context, *, search: str):
        if not ctx.voice_client:
                vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first.")
        else:
            vc: wavelink.Player = ctx.voice_client
        
        if vc.queue.is_empty and not vc.is_playing():
            try:
                tracks : list[spotify.SpotifyTrack] = await spotify.SpotifyTrack.search(query=search)
                if len(tracks) >= 5:
                    message = await ctx.send(content=f"```\nADDING {len(tracks)} SONGS TO QUEUE\n```")
                    for track in tracks:
                        await vc.queue.put_wait(track)
                        if not vc.is_playing():
                            playing = vc.queue.get()
                            await vc.play(playing)
                            await ctx.send(f'Playing `{playing.title}`')
                        await message.edit(f'```\nADDING {len(tracks)} SONGS TO QUEUE \n{len(tracks) - tracks.index(track)} SONGS LEFT TO BE ADDED\n\nAdded {track.title} to the queue...\n```')
                    await message.edit(f'```\nSUCCESSFULLY ADDED {len(tracks)} TO QUEUE \nIN: {datetime.timedelta(seconds=len(tracks))}\n\nThe Number of Songs in QUEUE {len(vc.queue)} to the queue...```')
                else:
                    await vc.queue.put_wait(tracks[0])
                    playing = vc.queue.get()
                    await vc.play(playing)
                    await ctx.send(f'Playing `{playing.title}`')
                
            except Exception as e:
                await ctx.send("Please enter a spotify **song url**.")
                return print(e)
        else:
            tracks : list[spotify.SpotifyTrack] = await spotify.SpotifyTrack.search(query=search)
            if len(tracks) >= 5:
                    for track in tracks:
                        await vc.queue.put_wait(track)
                        await ctx.send(f'Added `{track.title}` to the queue...')
            else:
                await vc.queue.put_wait(tracks[0])
                await ctx.send(f'Added `{tracks[0].title}` to the queue...')
        self.main_channels[ctx.guild.id] = ctx.channel
        try:
            if vc.loop: return
        except Exception:
            setattr(vc, "loop", False)    
        
def setup(bot):
    bot.add_cog(Music(bot))
    
