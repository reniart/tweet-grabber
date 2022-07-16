import requests
import os
import json
import discord

from discord.ext import commands
from typing import FrozenSet

# setting twitterDev project token
bearer_token = os.environ.get("BEARER_TOKEN")

# setting up discordBot 
client = discord.Client()
bot_id = os.environ.get("TWEET_GRABBER")

#discord command set
commands: FrozenSet[str] = frozenset((
    "ping",
    "grab",
))

def create_url():
    # additional fields include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    tweet_fields = "tweet.fields="
    # additional ids can be added with comma spacing
    id = os.environ.get("TWITTER_ID")

    url = "https://api.twitter.com/2/users/{}/liked_tweets".format(id)
    return url, tweet_fields

def bearer_ouath(request):
    # twitterDev project authentication
    request.headers["Authorization"] = f"Bearer {bearer_token}"
    request.headers["User-Agent"] = "liked_twt_grabber"
    return request

def connect_endpoint(url, tweet_fields):
    response = requests.request(
        "GET", url, auth=bearer_ouath, params=tweet_fields)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def grab_tweets():
    url, tweet_fields = create_url()
    json_response = connect_endpoint(url, tweet_fields)

    grabbed_tweets = open("liked_tweets.json", 'w')    
    grabbed_tweets.write(json.dumps(json_response, indent=4, sort_keys=True))
    grabbed_tweets.close()

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



