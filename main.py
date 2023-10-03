import discord
import os
import dotenv
import cogs.replays as rpl

# set intents
intents = discord.Intents.default()  # Create a default intent object
intents.message_content = True  # Enable message content intent

# initialisation commands
bot = discord.Bot(intents=intents)
dotenv.load_dotenv()

# loads cogs
cogs_list = ['maintenance', 'waryes', 'warno', 'match']
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
    try:
        if message.author == bot.user:
            return

        if message.attachments:
            for attachment in message.attachments:
                # Check if the message contains any attachments (files)
                if attachment.filename.endswith(".rpl3"):
                    # Read the contents of the file as binary data
                    file_content = await attachment.read()
                    embed = rpl.processReplay(attachment.filename, file_content, message)
                    await message.channel.send(embed=embed)
    except Exception as e:
        print(e)
    #await message.channel.send("Herro!")\


# Starts the bot
bot.run(str(os.getenv('TOKEN')))