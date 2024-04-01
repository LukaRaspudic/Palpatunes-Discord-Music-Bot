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
async def play(ctx, url):
    # Get the voice client associated with the guild
    voice_client = ctx.voice_client

    # Check if the bot is not already connected to a voice channel
    if not voice_client:
        # Bot is not in a voice channel, attempt to join the author's voice channel
        channel = ctx.author.voice.channel
        print(f'Attempting to join channel: {channel}')
        voice_client = await channel.connect()

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
                voice_channel.play(discord.FFmpegPCMAudio(audio_url), after=lambda e: print('done', e))
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