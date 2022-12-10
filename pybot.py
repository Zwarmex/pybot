# Avec l'objet Bot de discord
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import youtube_dl
import asyncio
import giphy_client
from giphy_client.rest import ApiException
import random

load_dotenv(dotenv_path=".env")
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
prefix = "$"
bot = commands.Bot(command_prefix=prefix, intents=intents)


@bot.event
async def on_ready():
    print(f"The bot is connected to the following server : {GUILD}")


@bot.command()
async def gif(ctx, *, q="Happy"):

    api_key = "pvLLZRHXazRKxMYEfCzrpDcmgiaoVHrw"
    api_instance = giphy_client.DefaultApi()

    try:
        api_response = api_instance.gifs_search_get(api_key, q, limit=5, rating='g')
        lst = list(api_response.data)
        gif_select = random.choice(lst)
        embed = discord.Embed(title=q)
        embed.set_image(url=f"https://media.giphy.com/media/{gif_select.id}/giphy.gif")
        await ctx.channel.send(embed=embed)
    except ApiException as r:
        print("Exception for the api")


# Pour supprimer un nombre 'n' de message(s)


@bot.command(name="del", help="Permet de supprimer un nombre 'n' de message(s).")
async def delete(ctx, number: int):
    messages = await ctx.channel.history(limit=number + 1).flatten()
    for message in messages:
        await message.delete()


# Pour jouer de la musique
musics = {}
ytdl = youtube_dl.YoutubeDL()


class Video:
    def __init__(self, link):
        video = ytdl.extract_info(link, download=False)
        video_format = video["formats"][0]
        self.url = video["webpage_url"]
        self.stream_url = video_format["url"]


@bot.command()
async def leave(ctx):
    client = ctx.guild.voice_client
    await client.disconnect()
    musics[ctx.guild] = []


@bot.command()
async def resume(ctx):
    client = ctx.guild.voice_client
    if client.is_paused():
        client.resume()


@bot.command()
async def pause(ctx):
    client = ctx.guild.voice_client
    if not client.is_paused():
        client.pause()


@bot.command()
async def skip(ctx):
    client = ctx.guild.voice_client
    client.stop()


def play_song(client, queue, song):
    source = discord.PCMVolumeTransformer(
        discord.FFmpegPCMAudio(song.stream_url, before_options="-reconnect 1 -reconnect_streamed 1 "
                                                               "-reconnect_delay_max 5"))

    def next(_):
        if len(queue) > 0:
            new_song = queue[0]
            del queue[0]
            play_song(client, queue, new_song)
        else:
            asyncio.run_coroutine_threadsafe(client.disconnect(), bot.loop)

    client.play(source, after=next)


@bot.command()
async def play(ctx, url):
    print("play")
    client = ctx.guild.voice_client

    if client and client.channel:
        video = Video(url)
        musics[ctx.guild].append(video)
    else:
        channel = ctx.author.voice.channel
        video = Video(url)
        musics[ctx.guild] = []
        client = await channel.connect()
        await ctx.send(f"Je lance : {video.url}")
        play_song(client, musics[ctx.guild], video)


bot.run(TOKEN)
