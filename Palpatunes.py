import discord
from discord.ext import commands
import youtube_dl
from collections import deque

intents = discord.Intents.default()
intents.all()

token = # Add your own discord bot token here instead
prefix = '!'

bot = commands.Bot(command_prefix=prefix, intents=intents)
queues = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(name='play')
async def play(ctx, url):
    channel = ctx.message.author.voice.channel
    voice_channel = await channel.connect()

    if not queues.get(ctx.guild.id):
        queues[ctx.guild.id] = deque()

    queues[ctx.guild.id].append(url)

    if not voice_channel.is_playing():
        await play_next(ctx.guild.id, voice_channel)

@bot.command(name='skip')
async def skip(ctx):
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice_channel.stop()

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
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            voice_channel.play(discord.FFmpegPCMAudio(url2), after=lambda e: print('done', e))
        await bot.get_channel(voice_channel.channel.id).send(f'Now playing: {info["title"]}')

@bot.event
async def on_voice_state_update(member, before, after):
    if not member.bot and after.channel is None:
        voice_channel = discord.utils.get(bot.voice_clients, guild=member.guild)
        if voice_channel and not voice_channel.is_playing():
            await play_next(member.guild.id, voice_channel)

bot.run(token)