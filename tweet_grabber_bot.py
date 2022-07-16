import discord
import os
import json

from discord.ext import commands
from liked_tweets_grabber import *
from typing import FrozenSet

# setting up discordBot 
client = discord.Client()
bot_id = os.environ.get("TWEET_GRABBER")

#discord command set
commands: FrozenSet[str] = frozenset((
    "ping",
    "grab",
))

@client.event
async def on_ready():
    print("Bot is logged in as {0.user}".format(client))

@client.event
async def on_message(msg: discord.Message):
    if msg.author == client.user:
        return

    if msg.content[0] == "!" and len(msg.content) > 1:
        args: List[str] = msg.content[1:].lower().split()

        if args[0] not in commands:
            await msg.channel.send("Unknown command")
            return
        
        if args[0] == "ping":
            await msg.channel.send(f'Pong! {round(client.latency * 1000)}ms')

        if args[0] == "grab":
            grab_tweets()
            await msg.channel.send("Tweets grabbed")



client.run(bot_id)