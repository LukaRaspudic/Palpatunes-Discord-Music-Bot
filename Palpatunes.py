import discord
from discord.ext import commands
import yt_dlp
from collections import deque
import asyncio
import os

intents = discord.Intents.all()

token = 'add token'
prefix = '!'
MAX_RETRIES = 9999999999
DELAY_SECONDS = 1

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
    
    # If no song is currently playing, start playback
    if not voice_client.is_playing():
        await play_next(ctx, voice_client)

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

@bot.command(name='queue')
async def queue(ctx):
    if queues.get(ctx.guild.id):
        queue_list = "\n".join(queues[ctx.guild.id])
        await ctx.send(f"Music Queue:\n{queue_list}")
    else:
        await ctx.send("The queue is empty.")

async def download_audio(url, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if 'entries' in info:
            filename = info['entries'][0]['title'] + '.' + info['entries'][0]['ext']
        else:
            filename = info['title'] + '.' + info['ext']
        
        return filename
    
async def play_next(ctx, voice_client):
    if queues.get(ctx.guild.id):
        url = queues[ctx.guild.id].popleft()

        ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info.get('url')

            if audio_url:
                # Download the audio file
                await download_audio(url, ydl_opts)

                # Play the downloaded file
                file_path = f'downloads/{info["title"]}.{info["ext"]}'
                voice_client.play(discord.FFmpegPCMAudio(file_path), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx, voice_client), bot.loop))
                await ctx.send(f'Now playing: {info["title"]}')
                
                # Delete the file after playback
                os.remove(file_path)
            else:
                await ctx.send(f'Error: No audio stream found for {info["title"]}')

# Run the bot
bot.run(token)