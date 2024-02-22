import discord
import os
import dotenv
import logging
from logging.handlers import TimedRotatingFileHandler
import cogs.replays as rpl

def setup_logging():
    log_folder = "logs"
    log_filename = "yesman.log"

    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    log_filepath = os.path.join(log_folder, log_filename)
    handler = TimedRotatingFileHandler(log_filepath, when="D", interval=1, backupCount=7)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger

def setup_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = discord.Bot(intents=intents)
    dotenv.load_dotenv()

    cogs_list = ['maintenance', 'waryes', 'warno', 'match']
    for cog in cogs_list:
        bot.load_extension(f'cogs.{cog}')

    return bot

logger = setup_logging()
bot = setup_bot()

@bot.event
async def on_ready():
    try:
        logger.info(f'Bot is logged in as {bot.user}')
    except Exception as e:
        logger.error(f"{e}")

@bot.event
async def on_message(message):
    try:
        if message.author == bot.user:
            return

        if message.attachments:
            for attachment in message.attachments:
                # Check if the message contains any attachments (files)
                if attachment.filename.endswith(".rpl3"):
                    # Read the contents of the file as binary data
                    file_content = await attachment.read()
                    logger.info(f'Processing replay file: {attachment.filename}')
                    embed = rpl.processReplay(attachment.filename, file_content, message)
                    await message.channel.send(embed=embed)
    except Exception as e:
        logger.error(f"{e}")
    #await message.channel.send("Herro!")\


# Starts the bot
bot.run(str(os.getenv('DEVTOKEN')))