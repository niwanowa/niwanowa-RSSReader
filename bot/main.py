import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

import feedparser
from datetime import datetime,timedelta,timezone
import time


load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
RSS_URL = os.getenv('RSS_URL')
os.environ['TZ'] = "UTC"

intents = discord.Intents.default()
intents.guilds = True  # サーバーに関するイベントを取得できるようにする
intents.message_content = True # メッセージの内容を取得する権限

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    # 参加しているサーバーのID一覧を取得
    guild_ids = [guild.id for guild in bot.guilds]
    print(f'Bot is in the following guilds: {guild_ids}')

    # サーバーIDを指定して、サーバーのオブジェクトを取得
    guild = bot.get_guild(guild_ids[0])
    print(f'Bot is in the following guild: {guild}')

    # サーバーのオブジェクトから、チャンネルのオブジェクトを取得
    await bot.get_channel(CHANNEL_ID).send('Bot has started.')

    # 5分おきに実行する
    while True:
        # RSSの取得
        feed = feedparser.parse(RSS_URL)
        print(f'Get RSS')
        await bot.loop.create_task(rss_task(feed))

        await asyncio.sleep(60)


    

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

@bot.event
async def on_message(message):
    print(f'Message received: {message}')
    await bot.process_commands(message)

# RSSの取得と送信
async def rss_task(feed):
        # RSSのentryを表示
    for entry in feed.entries:
        # updated_parsedが1分以内の場合はdiscordに送信
        pubdate=datetime.fromtimestamp(time.mktime(entry.updated_parsed), timezone.utc)
        five_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=1)

        print(f'pubdate: {pubdate}, five_minutes_ago: {five_minutes_ago}, pubdate > five_minutes_ago: {pubdate > five_minutes_ago}')
        if pubdate > five_minutes_ago:
            await bot.get_channel(CHANNEL_ID).send(entry.link)

bot.run(TOKEN)

