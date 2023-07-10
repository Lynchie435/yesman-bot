# Placeholder for match arranging system
import discord
from discord.ext import commands


class Game(commands.Cog):
    ctx_parse = discord.ApplicationContext

    def __init__(self, bot: discord.Bot):
        self.bot = bot.user

    grp = discord.SlashCommandGroup("match", "This is a collection of commands relating to games/matches.")