from urllib import response
import discord
from discord.ext import commands
from discord.ext.commands import MemberConverter
import berserk
from datetime import datetime
from berserk import utils
import random
import openai
import os
import time
from pytube import YouTube as youtube
from pytube import Playlist
import ffmpy
import requests
from riotwatcher import *


# ^ - libraries


RIOT_API_KEY = "RGAPI-c7613589-8874-450d-bd3d-2693736514f3"
OPENAI_KEY = "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"
lichess_api_key = "lip_93MXLSRM3pjbRZPsuJv3"
Discord_api_key = (
    "OTg2NzcxOTQ2Mjg3MDA1NzE2.Ghh-BL.u2UvpEzQmm3N0XQv7wfaJPWnyU0WbUbk5WwmzY"
)

lol_watcher = LolWatcher(RIOT_API_KEY)

MY_DISCORD_ID = "344435071610126336"
openai.api_key = OPENAI_KEY

brsrk_session = berserk.TokenSession(lichess_api_key)
brsrk_client = berserk.Client(brsrk_session)


# bot = discord.Client() # instance of a "discord.Client()" class

# ^ - api keys and auth.variables

intents = discord.Intents.default()
intents.messages = True
intents.presences = True


bot = commands.Bot(command_prefix="!", intents=intents)

# ^ - discord bot perms/ instance of class "commands.Bot" with prefix "!"

# chatgpt things

start_sequence = "\nAI:"
restart_sequence = "\nHuman:"

# ^ - event on bot startup

@bot.event  # EVENT
async def on_ready():  # ON LOGIN
    print(
        "We have logged in as {0.user}".format(bot)
    )  # PRINTS OUT A MESSAGE IN THE TERMINAL



@bot.event
async def on_message(message):    
    if message.author == bot.user:
        return
    
    if isinstance(message.channel, discord.DMChannel):
        user = await bot.fetch_user(MY_DISCORD_ID)
        await user.send(f"Received message from: {message.author} \n Message: {message.content}")



# msg me if bot gets msg





# get  user id and send dm to said user id

@bot.command()
async def send_dm(ctx, message: str, user_name: str):
    try:
        member = await MemberConverter().convert(ctx, user_name)

        #     Get the user ID from the Member object
        user_id = member.id

        #      Fetch the user object from the user ID
        user_obj = await bot.fetch_user(user_id)

        #      Send the DM to the user
        
        await user_obj.send(message)

        #     #Send a confirmation message to the chat
        await ctx.send(f"Sent DM to {user_name}")
    except:
         await ctx.send(f"Could not send DM to user {user_name}.")


# get weather for any lithuanian city

@bot.command()
async def getweather(ctx, message: str):
    requestlink = (
        "https://api.meteo.lt/v1/places/" + str(message) + "/forecasts/long-term"
    )
    response = requests.get(requestlink)
    f = response.json()
    await ctx.send(
        "Weather for: "
        + str(message)
        + "\n Time of forecast: "
        + str(f["forecastTimestamps"][0]["forecastTimeUtc"])
        + "\n Air temperature: "
        + str(f["forecastTimestamps"][0]["airTemperature"])
        + " degrees C. \n Wind speed: "
        + str(f["forecastTimestamps"][0]["windSpeed"])
        + " m/s."
    )


# get lichess account


@bot.command()
async def lichessacc(ctx):
    await ctx.send("Lichess account:" + str(brsrk_client.account.get()))


# get PGN info about lichess game using game id


@bot.command()
async def getpgn(ctx, arg):
    message = str(arg).replace("!getpgn", "")
    print(message)
    gameLink = "https://lichess.org/game/export/" + str(message)
    try:
        pgn = brsrk_client.games.export(message, as_pgn=True)
    except:
        await ctx.send(
            f"Game ({gameLink}) does not exist, you probably got the wrong game ID, please try again!"
        )
    pgnLength = len(pgn)

    if pgnLength % 2 == 0:
        firstHalf, secondHalf = pgn[0 : pgnLength // 2], pgn[pgnLength // 2 :]

        print(firstHalf)
        print(secondHalf)
        await ctx.send(f"First half: {firstHalf}")
        await ctx.send(f"Second half: {secondHalf}")
    else:
        firstHalf, secondHalf = pgn[0 : pgnLength // 2 + 1], pgn[(pgnLength // 2 + 1) :]
        await ctx.send(f"First half: {firstHalf}")
        await ctx.send(f"Second half: {secondHalf}")


# get lichess user info by username


@bot.command()
async def getinfo(ctx, arg):
    message = str(arg).replace("!getinfo", "")
    userInfo = dict(brsrk_client.users.get_public_data(str(message)))
    await ctx.send(
        "Username: "
        + str(userInfo["id"])
        + "\n"
        + "Bullet Rating: "
        + str(userInfo["perfs"]["bullet"]["rating"])
        + "\n"
        + "Blitz Rating: "
        + str(userInfo["perfs"]["blitz"]["rating"])
        + "\n"
        + "Rapid Rating: "
        + str(userInfo["perfs"]["rapid"]["rating"])
        + "\n"
        + "Classical Rating: "
        + str(userInfo["perfs"]["classical"]["rating"])
        + "\n"
        + "Puzzle Rating: "
        + str(userInfo["perfs"]["puzzle"]["rating"])
        + "\n"
        + "Profile Link: "
        + str(userInfo["url"])
    )


# get a list of certain games using username, and info abt game (start/end)


@bot.command()
async def getgames(
    ctx,
    userName: str,
    startYear: int,
    startMonth: int,
    startDay: int,
    endYear: int,
    endMonth: int,
    endDay: int,
):
    startDate, endDate = (startYear, startMonth, startDay), (endYear, endMonth, endDay)
    lichessUsername = userName
    gameExportStart = berserk.utils.to_millis(
        datetime(int(startYear), int(startMonth), int(startDay))
    )
    gameExportEnd = berserk.utils.to_millis(
        datetime(int(endYear), int(endMonth), int(endDay))
    )
    print(
        brsrk_client.games.export_by_player(
            lichessUsername, since=gameExportStart, until=gameExportEnd, max=300
        )
    )
    exportedGames = list(
        brsrk_client.games.export_by_player(
            lichessUsername, since=gameExportStart, until=gameExportEnd, max=300
        )
    )
    await ctx.send(
        "--------------" + "\n"
        "Game ID: " + exportedGames[0]["id"] + "\n"
        "Game link: https://lichess.org/" + exportedGames[0]["id"] + "\n"
        "Game speed: " + exportedGames[0]["speed"] + "\n"
        "Player and color: "
        + exportedGames[0]["players"]["white"]["user"]["id"]
        + ", white"
        + "\n"
        "Player and color: "
        + exportedGames[0]["players"]["black"]["user"]["id"]
        + ", black"
        + "\n"
        "Moves: " + exportedGames[0]["moves"] + "\n"
        "Winner of the game: " + exportedGames[0]["winner"] + "\n"
        "--------------"
    )


# rock paper scissors !!!


@bot.command()
async def rps(ctx, arg):
    arg = arg.strip().lower()
    if arg not in ["rock", "paper", "scissors"]:
        await ctx.send("Invalid input. Please choose 'rock', 'paper', or 'scissors'.")
        return

    winning_moves = {"rock": "scissors", "paper": "rock", "scissors": "paper"}

    cpu_choice = random.choice(list(winning_moves.keys()))

    if arg == cpu_choice:
        game_winner = "Draw!"

    elif winning_moves[arg] == cpu_choice:
        game_winner = "Player"

    else:
        game_winner = "CPU"

    await ctx.send(
        "Player picked: "
        + arg.capitalize()
        + "\nCPU picked: "
        + cpu_choice.capitalize()
        + "\nWinner: "
        + game_winner
    )


# generate image based on user prompt, amount of images and image resolution


@bot.command()
async def genimg(ctx):
    message = ctx.message.content.replace("!genimg", "").split("|")
    imgPrompt = message[0]
    imgCount = message[1]
    imgRes = message[2]

    await ctx.send(f"Generating: {imgPrompt}")

    response = openai.Image.create(prompt=imgPrompt, n=int(imgCount), size=imgRes)
    imageUrl = response["data"][0]["url"]
    imgUrl = ""

    for i in response["data"]:
        time.sleep(0.2)
        await ctx.send(i["url"])


# download youtube video


@bot.command()
async def getvid(ctx, link: str, format: str):
    yt = youtube(link)
    if "audio_only" in format:
        yt.streams.filter(only_audio=True).last().download()
    else:
        yt.streams.filter(progressive=True).order_by("resolution").last().download()
    await ctx.send("Video downloaded.")


# download youtube playlist


@bot.command()
async def getplaylist(ctx, link: str, format: str):
    print(link)
    playlist = Playlist(link)
    playlistUrls = list(playlist.video_urls)
    if format == "only_audio":
        for url in playlistUrls:
            yt = youtube(url)
            print(f"Downloading: {yt.title}")
            yt.streams.filter(only_audio=True).last().download()
            print(f"{yt.title} has finished downloading!")
    elif format == "with_video":
        for url in playlistUrls:
            yt = youtube(url)
            print(f"Downloading: {yt.title}")
            yt.streams.filter(progressive=True).order_by("resolution").last().download()
            print(f"{yt.title} has finished downloading!")
    await ctx.send("Playlist downloaded!")


# get video thumbnail in discord


@bot.command()
async def getthumbnail(ctx, link: str):
    thumbnailUrl = thumbnail_url_string = youtube(link).thumbnail_url
    await ctx.send("Thumnbail: " + str(thumbnailUrl))


# convert mp4 to mp3 using ffmpeg


@bot.command()
async def getmp3(ctx, startName: str, endName: str):
    inputName = startName + ".mp4"
    outputName = endName + ".mp3"
    ff = ffmpy.FFmpeg(inputs={inputName: None}, outputs={outputName: None})
    ff.run()
    await ctx.send(inputName + " was converted to: " + str(outputName) + " !")


# get league info (name, rank, LP, etc) using region and summonerName


@bot.command()
async def getleagueinfo(ctx, region: str, userName: str):
    lolRegion = region
    lolUsername = userName
    lolID = lol_watcher.summoner.by_name(str(lolRegion), str(lolUsername))
    lolRankedStats = lol_watcher.league.by_summoner(lolRegion, lolID["id"])
    await ctx.send(
        "Stats for "
        + str(lolUsername)
        + " : \n Username: "
        + lolRankedStats[0]["summonerName"]
        + "\n Rank: "
        + lolRankedStats[0]["tier"]
        + " "
        + lolRankedStats[0]["rank"]
    )

@bot.command()
async def chat(ctx):
    response = openai.Completion.create(
        model = "text-davinci-003",
        prompt = ctx.message.content,
        temperature = 0.9,
        max_tokens = 150,
        top_p = 1,
        frequency_penalty =0,
        presence_penalty = 0.6,
        stop = ["Human:", "AI:"]
    )
    message = response.choices[0].text
    await ctx.send(message)


# run bot

bot.run(Discord_api_key)  # DISCORD BOT API KEY
