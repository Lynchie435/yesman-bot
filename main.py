import discord
import os
import dotenv
from discord.ext import commands

# initialisation commands
bot = discord.Bot()
dotenv.load_dotenv()

# loads cogs
cogs_list = ['maintenance', 'waryes']
for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')


@bot.event
async def on_ready():
    try:
        print(f'We have logged in as {bot.user}')
    except Exception as e:
        print(e)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    #await message.channel.send("Herro!")\


# Starts the bot
bot.run(str(os.getenv('DEVTOKEN')))