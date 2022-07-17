import discord
import json
import datetime

from discord.ext import commands
from discord.ext import tasks
from liked_tweets_grabber import grab_tweets
from configparser import ConfigParser
from typing import FrozenSet

# setting up discordBot 
client = discord.Client()
conf = ConfigParser(interpolation=None)
conf.read('config.ini')
bot_id = conf['token']['bot_token']

#discord command set
commands: FrozenSet[str] = frozenset((
    "ping",
    "grab",
))

@client.event
async def on_ready():
    print("Bot is logged in as {0.user}".format(client))
    send_new_tweets.start()

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

@tasks.loop(minutes=1.0)
async def send_new_tweets():
    channel = client.get_channel(998034366737436692)
    #grabbing id of the newest tweet from the last grab cycle
    with open("liked_tweets.json") as json_file:
        data = json.load(json_file)
        tweet_data = data["data"]
        last_tweet = tweet_data[0]["id"]

    #updating json of liked tweets from twitter
    grab_tweets()

    #posts all new tweets to discord
    with open("liked_tweets.json") as new_json:
        data = json.load(new_json)
        new_data = data["data"]
        for tweet in new_data:
            if tweet["id"] == last_tweet:
                break

            else:
                await channel.send(f'https://twitter.com/twitter/status/{tweet["id"]}')

    await channel.send(f'in {round(client.latency * 1000)}ms')



client.run(bot_id)