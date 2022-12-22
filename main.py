import json
import tweepy
import discord
from discord.ext import tasks

token = ''
consumer_key = ''
consumer_secret = ''
bearer_token = ''
channel_id = -1

keywords = ['pokémon scarlet &amp; violet', 'tera raid']

# Load sensitive info from file
with open('creds.json', 'r') as fp:
    data = json.load(fp)
    token = data['discord_token']
    consumer_key = data['twitter_api_key']
    consumer_secret = data['twitter_api_secret']
    bearer_token = data['twitter_bearer_token']
    channel_id = data['channel_id']

intents = discord.Intents.default()
bot = discord.Client(command_prefix="~", intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    if not on_tweet.is_running():
        on_tweet.start()


def has_been_posted(link):
    with open('recent_tweets.txt', 'a+') as fp:
        fp.seek(0)
        links = [link.strip() for link in fp.readlines()]
        if link not in links:
            fp.write(link + '\n')
            return False
        return True


@tasks.loop(minutes=30)
async def on_tweet():
    await bot.wait_until_ready()
    # Get tweets from @SerebiiNet
    client = tweepy.Client(bearer_token=bearer_token)
    tweets = client.get_users_tweets(38857814, max_results=5)

    recent_tweets = []

    for tweet in tweets.data:
        for key in keywords:
            if key in tweet.text.lower():
                delimited = tweet.text.split(' ')
                # Link to actual tweet appears to always be the last word
                link = delimited[len(delimited) - 1]
                if link not in recent_tweets:
                    recent_tweets.append(link)
                    string = tweet.text
                    # Tweets in form "Serebii Update: (Title). (Desc)"
                    title = string[string.index(': ') + 1: string.index('.')]
                    if not has_been_posted(link):
                        print("Posting tweet " + link)
                        await bot.get_channel(channel_id).send(f'{title}\n{link}')

bot.run(token)
