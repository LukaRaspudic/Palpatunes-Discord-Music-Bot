import discord
from discord.ext import commands
import yt_dlp
from collections import deque

intents = discord.Intents.all()

token = 'ADD YOUR TOKEN'
prefix = '!'

bot = commands.Bot(command_prefix=prefix, intents=intents)
queues = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(name='play')
async def play(ctx, *, query):
    voice_client = ctx.voice_client

    # Check if the user is in a voice channel
    if not ctx.author.voice:
        await ctx.send("You are not connected to a voice channel.")
        return

    # Check if the bot is not already connected to a voice channel
    if not voice_client:
        channel = ctx.author.voice.channel
        print(f'Attempting to join channel: {channel}')
        voice_client = await channel.connect()

    # Search for the song based on the provided query
    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'default_search': 'auto',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_results = ydl.extract_info(query, download=False)
        if 'entries' in search_results:
            # If multiple search results are returned, choose the first one
            url = search_results['entries'][0]['webpage_url']
        else:
            url = search_results['webpage_url']

    # Add the selected song to the queue
    if not queues.get(ctx.guild.id):
        queues[ctx.guild.id] = deque()
    queues[ctx.guild.id].append(url)

    # Check if the bot is not playing any song
    if not voice_client.is_playing():
        # If not, start playing the first song in the queue
        await play_next(ctx.guild.id, voice_client)

@bot.command(name='skip')
async def skip(ctx):
    # Get the voice client associated with the guild
    voice_client = ctx.voice_client

    if voice_client and voice_client.is_playing():
        # Stop the currently playing song
        voice_client.stop()
    else:
        await ctx.send("There is no song currently playing.")

    # If there are more songs in the queue, play the next one
    if queues.get(ctx.guild.id):
        await play_next(ctx.guild.id, voice_client)

@bot.command(name='stop')
async def stop(ctx):
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice_channel.stop()
    queues[ctx.guild.id].clear()
    await ctx.send("Music stopped and playlist cleared.")

@bot.command(name='pause')
async def pause(ctx):
    voice_client = ctx.voice_client

    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Playback paused.")
    else:
        await ctx.send("No song is currently playing.")

@bot.command(name='resume')
async def resume(ctx):
    voice_client = ctx.voice_client

    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Playback resumed.")
    else:
        await ctx.send("No paused song to resume.")

@bot.command(name='queue')
async def queue(ctx):
    if queues.get(ctx.guild.id):
        queue_list = "\n".join(queues[ctx.guild.id])
        await ctx.send(f"Music Queue:\n{queue_list}")
    else:
        await ctx.send("The queue is empty.")

async def play_next(guild_id, voice_channel):
    if queues.get(guild_id):
        url = queues[guild_id].popleft()

        ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info.get('url')

            if audio_url:
                # Use discord.PCMVolumeTransformer instead of discord.FFmpegPCMAudio
                voice_channel.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(audio_url)), after=lambda e: print('done', e))
                await bot.get_channel(voice_channel.channel.id).send(f'Now playing: {info["title"]}')

                # Check if there are more songs in the queue
                if queues[guild_id]:
                    await play_next(guild_id, voice_channel)
            else:
                await bot.get_channel(voice_channel.channel.id).send(f'Error: No audio stream found for {info["title"]}')

@bot.event
async def on_voice_state_update(member, before, after):
    if not member.bot and after.channel is None:
        voice_channel = discord.utils.get(bot.voice_clients, guild=member.guild)
        if voice_channel and not voice_channel.is_playing():
            await play_next(member.guild.id, voice_channel)

bot.run(token)