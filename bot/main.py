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
        keys= tuple(row[c] for c in columns)
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

@tasks.loop(hours = 6.0)
async def send_new_tweets():
    channel_id = int(os.environ.get('CHANNEL_ID'))
    channel = client.get_channel(channel_id)

    #updating db of liked tweets from twitter
    grabbed_tweets = grab_tweets()
    update_db('liked_tweets.db', grabbed_tweets)

    #connecting to sqlite db
    connection_liked = sqlite3.connect('liked_tweets.db')
    cursor_liked = connection_liked.cursor()

    connection_sent = sqlite3.connect('sent_tweets.db')
    cursor_sent= connection_sent.cursor()

    cursor_liked.execute('SELECT * FROM tweets')
    cursor_sent.execute('SELECT * FROM tweets')

    sent_table = cursor_sent.fetchall()

    #sending new tweets
    for i in cursor_liked:
        previously_sent = False
        for j in sent_table:
            if i[0] == j[0]:
                previously_sent = True
                break
        if not previously_sent:
            cursor_sent.execute('INSERT INTO tweets (id) VALUES (?)', (i[0],))
            await channel.send(f'https://twitter.com/twitter/status/{i[0]}')

    #closing and commit db connections
    connection_liked.commit()
    connection_liked.close()
    connection_sent.commit()
    connection_sent.close()
 
    await channel.send(f'in {round(client.latency * 1000)}ms')

client.run(bot_id)