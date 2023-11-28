import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

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

    # サーバーのオブジェクトから、チャンネルの一覧を取得
    channels = guild.channels
    print(f'Channels in the guild: {channels}')

    # チャンネルの一覧を表示
    for channel in channels:
        print(f'Channel: {channel.name}, ID: {channel.id}')


@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

@bot.event
async def on_message(message):
    print(f'Message received: {message}')
    await bot.process_commands(message)


bot.run(TOKEN)
