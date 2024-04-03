import discord
from discord.ext import commands
import yt_dlp
from collections import deque
import asyncio
import os
import re

intents = discord.Intents.all()

token = 'your token'
prefix = '!'
MAX_RETRIES = 60
DELAY_SECONDS = 1

bot = commands.Bot(command_prefix=prefix, intents=intents)
queues = {}
last_ctx = None

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

    # Start downloading the next song in the queue
    await download_next_song(ctx.guild.id)

    # Check if the bot is not playing any song
    if not voice_client.is_playing():
        # If not, start playing the first song in the queue
        await play_next(ctx.guild.id, voice_client)

@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user and after.channel is None and before.channel is not None:
        # Bot has disconnected from a voice channel
        guild_id = before.channel.guild.id
        if queues.get(guild_id):
            # If there are songs in the queue, play the next one
            voice_channel = discord.utils.get(bot.voice_clients, guild=before.channel.guild)
            if not voice_channel.is_playing():
                await play_next(guild_id, voice_channel)

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

async def play_next(guild_id, voice_channel, retries=MAX_RETRIES):
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
                # Download the audio file
                filename = await download_audio(url, ydl_opts)
                
                if filename:
                    
                    try:
                        # Play the downloaded file
                        file_path = f'downloads/{filename}'
                        voice_channel.play(discord.FFmpegPCMAudio(file_path))
                        await bot.get_channel(voice_channel.channel.id).send(f'Now playing: {info["title"]}')
                        
                        # Delete the file after playback
                        os.remove(file_path)
                        
                        # Start downloading the next song in the queue
                        await download_next_song(guild_id)
                    except Exception as e:
                        if retries > 0:
                            print(f"Error during playback: {e}. Retrying...")
                            await asyncio.sleep(DELAY_SECONDS)
                            await play_next(guild_id, voice_channel, retries=retries - 1)
                        else:
                            print("Max retries exceeded. Skipping song.")
                            await play_next(guild_id, voice_channel)
            else:
                await bot.get_channel(voice_channel.channel.id).send(f'Error: No audio stream found for {info["title"]}')

async def download_audio(url, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if 'entries' in info:
            filename = info['entries'][0]['title'] + '.' + info['entries'][0]['ext']
        else:
            filename = info['title'] + '.' + info['ext']
        
        return filename

async def download_next_song(guild_id):
    if queues.get(guild_id):
        next_url = queues[guild_id][0]

        ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }

        await download_audio(next_url, ydl_opts)

# Run the bot
async def start_bot():
    await bot.start(token)

asyncio.run(start_bot())