import discord
import json
import os
import sqlite3

from discord.ext import commands
from discord.ext import tasks
from liked_tweets_grabber import grab_tweets

# setting up discordBot 
client = discord.Client()
bot_id = os.environ.get('BOT_ID')

#updates db file with json response
def update_db(db_file, json_response):

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute('Create Table if not exists tweets (id Text)')
    cursor.execute('DELETE FROM tweets')

    columns = ['id']
    for row in json_response["data"]:
        keys = tuple(row[c] for c in columns)
        cursor.execute('insert into tweets values(?)',keys)
    
    connection.commit()
    connection.close()

@client.event
async def on_ready():
    print("Bot is logged in as {0.user}".format(client))
    update_db('sent_tweets.db', grab_tweets())
    send_new_tweets.start()

@client.event
async def on_message(msg: discord.Message):
    if msg.author == client.user:
        return

@tasks.loop(hours = 4.0)
async def send_new_tweets():
    channel_id = int(os.environ.get('CHANNEL_ID'))
    channel = client.get_channel(channel_id)

    #initializing sqlite db

    connection_sent = sqlite3.connect('sent_tweets.db')
    cursor_sent= connection_sent.cursor()
    cursor_sent.execute('SELECT * FROM tweets')
    sent_table = cursor_sent.fetchall()

    grabbed_tweets = grab_tweets()
    columns = ['id']
    tweet_ids = []
    for row in grabbed_tweets["data"]:
        keys = tuple(row[c] for c in columns)
        tweet_ids.append(keys)

    #sending new tweets
    for i in tweet_ids:
        previously_sent = False
        for j in sent_table:
            if i == j:
                previously_sent = True
                break
        if not previously_sent:
            cursor_sent.execute('INSERT INTO tweets (id) VALUES (?)', (i[0],))
            await channel.send(f'https://twitter.com/twitter/status/{i[0]}')

    #closing and commit db connections
    connection_sent.commit()
    connection_sent.close()

client.run(bot_id)