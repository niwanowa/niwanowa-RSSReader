import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

import feedparser
from datetime import datetime, timedelta, timezone
import time

import boto3

load_dotenv()

# Discordの認証情報を.envから取得
TOKEN = os.getenv("DISCORD_TOKEN")

# サービスヘルスチェック用のチャンネルIDを.envから取得
NOTIFICATION_CHANNEL_ID = int(os.getenv("NOTIFICATION_CHANNEL_ID"))

# RSSのURLを.envから取得
RSS_URL = os.getenv("RSS_URL")
os.environ["TZ"] = "UTC"

# AWS認証情報を.envから取得
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SEACRET_ACCESS_KEY")
DynamoDB_Table = os.getenv("DynamoDB_TABLE")

# AWSのDynamoDB接続
dynamodb = boto3.resource(
    "dynamodb",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name="ap-northeast-1",
)
table = dynamodb.Table(DynamoDB_Table)

print(f"AWS DynamoDB Table: {DynamoDB_Table}")
print(f"Item Count: {table.item_count}")

# DiscordのBotの設定
intents = discord.Intents.default()
intents.guilds = True  # サーバーに関するイベントを取得できるようにする
intents.message_content = True  # メッセージの内容を取得する権限

bot = commands.Bot(command_prefix="fffffffffffffffffffffffffffffffffffffffff!", intents=intents)


@bot.event
async def on_ready():
    """
    DiscordのBotが接続したときに実行されるイベントハンドラ。
    """
    print(f"{bot.user} has connected to Discord!")

    # 参加しているサーバーのID一覧を取得
    guild_ids = [guild.id for guild in bot.guilds]
    print(f"Bot is in the following guilds: {guild_ids}")

    # サーバーIDを指定して、サーバーのオブジェクトを取得
    guild = bot.get_guild(guild_ids[0])
    print(f"Bot is in the following guild: {guild}")

    # サーバーのオブジェクトから、チャンネル名とIDの一覧を取得
    channels = guild.channels
    print(f"Channels in the guild: {channels}")

    # サーバーのオブジェクトから、チャンネルのオブジェクトを取得
    await bot.get_channel(NOTIFICATION_CHANNEL_ID).send("Bot has started.")

    # 1分おきに実行する
    while True:
        # DynamoDBから全項目を取得
        response = table.scan()
        print(f"DynamoDB Scan: {response}")

        CHANNEL_ID = int(response["Items"][0]["channelId"])
        RSS_URL = response["Items"][0]["url"]

        for item in response["Items"]:
            print(f"Item: {item}")
            CHANNEL_ID = int(item["channelId"])
            RSS_URL = item["url"]
            # RSSの取得
            feeds = feedparser.parse(RSS_URL)
            print(f"Get RSS")
            await bot.loop.create_task(rss_task(CHANNEL_ID, feeds))

        await asyncio.sleep(60)


@bot.command()
async def test(ctx, arg):
    """
    テストコマンド。引数を受け取り、それをメッセージとして送信する。
    """
    await ctx.send(arg)


@bot.event
async def on_message(message):
    """
    メッセージが受信されたときに実行されるイベントハンドラ。
    """
    print(f"Message received: {message}")
    await bot.process_commands(message)


async def rss_task(CHANNEL_ID, feeds):
    """
    RSSの取得と送信を行う非同期タスク。
    """
    # RSSのentryを表示
    for entry in feeds.entries[-5:]:
        # updated_parsedが1分以内の場合はdiscordに送信
        pubdate = datetime.fromtimestamp(time.mktime(entry.updated_parsed), timezone.utc)
        five_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=1)

        print(
            f"pubdate: {pubdate}, five_minutes_ago: {five_minutes_ago}, pubdate > five_minutes_ago: {pubdate > five_minutes_ago}"
        )
        if pubdate > five_minutes_ago:
            await bot.get_channel(CHANNEL_ID).send(entry.link)


bot.run(TOKEN)
