##############
# Music.py
##############

from Errors import Errors as error
from discord.ext import commands
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL
import discord
import asyncio
import itertools
import sys
import traceback

ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = YoutubeDL(ytdlopts)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester
        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

    def __getitem__(self, item: str):
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()
        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        await ctx.send(f'```ini\n[Added {data["title"]} to the Queue.]\n```')
        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}
        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']
        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)
        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)


class MusicPlayer:
    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog
        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        self.np = None
        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                async with timeout(300):
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                if self in self._cog.players.values():
                    return self.destroy(self._guild)
                return

            if not isinstance(source, YTDLSource):
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            self.np = await self._channel.send(f'**Now Playing:** `{source.title}` requested by `{source.requester}`')
            await self.next.wait()
            source.cleanup()
            self.current = None

            try:
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):
    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:  
            for entry in self.players[guild.id].queue._queue:
                if isinstance(entry, YTDLSource): 
                    entry.cleanup()
            self.players[guild.id].queue._queue.clear()
        except KeyError:
            pass                        
                       
        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            return await ctx.send(embed=error.default_error('Error connecting to Voice Channel. Please make sure you are in a valid channel or provide me with one'))

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name='connect', aliases=['join'])
    # todo fix handling
    async def connect_(self, ctx):
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            return await ctx.send(embed=error.default_error('You have to be in a voice channel to use this command.'))

        vc = ctx.voice_client
        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                return await ctx.send(embed=error.voice_timeout_error(f'Moving to channel: <{channel}> timed out'))
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                return await ctx.send(embed=error.default_error(f'Connecting to channel: <{channel}> timed out'))
            except Exception as Ex:
                return await ctx.send(embed=error.default_error(Ex))
                
        await ctx.send(f'Connected to: **{channel}**')

    @commands.command(name='play', aliases=['p'])
    async def play_(self, ctx, *, search=None):
        if search == None:  return await ctx.send(embed=error.invalid_command_usage(self.bot, 'play [name]/[link]'))
        await ctx.trigger_typing()
        vc = ctx.voice_client
        if not vc:
            await ctx.invoke(self.connect_)

        player = self.get_player(ctx)
        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=False)
        await player.queue.put(source)

    @commands.command(name='pause')
    async def pause_(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send('I am not currently playing anything!')
        elif vc.is_paused():
            return
        vc.pause()
        await ctx.send(f'**`{ctx.author}`**: Paused the song!')

    @commands.command(name='resume')
    async def resume_(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!')
        elif not vc.is_paused():
            return
        vc.resume()
        await ctx.send(f'**`{ctx.author}`**: Resumed the song!')

    @commands.command(name='skip', aliases=['s'])
    async def skip_(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!')
        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.send(f'**`{ctx.author}`**: Skipped the song!')

    @commands.command(name='queue', aliases=['q', 'playlist'])
    async def queue_info(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send(embed=error.default_error('I am not connected to a voice channel'))
        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('There are currently no more queued songs.')
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = '\n'.join(f'**`{_["title"]}`**' for _ in upcoming)
        embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}', description=fmt)

        await ctx.send(embed=embed)

    @commands.command(name='np', aliases=['nowplaying', 'current', 'currentsong', 'playing'])
    async def now_playing_(self, ctx):
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(embed=error.default_error('I am not connected to a voice channel'))

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send('I am not currently playing anything!')

        try:
            await player.np.delete()
        except discord.HTTPException:
            pass

        player.np = await ctx.send(f'**Now Playing:** `{vc.source.title}` '
                                   f'requested by `{vc.source.requester}`')

    @commands.command(name='volume', aliases=['vol'])
    async def change_volume(self, ctx, *, vol: float):
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(embed=error.default_error('I am not connected to a voice channel'))

        if not 0 < vol < 101:
            return await ctx.send(embed=error.default_error('Please enter a value between 1 and 100.'))

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        await ctx.send(f'**`{ctx.author}`**: Set the volume to **{vol}%**')

    @commands.command(name='stop')
    async def stop_(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!')
        await self.cleanup(ctx.guild)

def setup(bot):
    bot.add_cog(Music(bot))