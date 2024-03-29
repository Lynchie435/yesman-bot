# Placeholder for match arranging system
import random

import discord
from discord import option
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class match(commands.Cog):
    ctx_parse = discord.ApplicationContext

    def __init__(self, bot: discord.Bot):
        self.bot = bot.user

    grp = discord.SlashCommandGroup("match", "This is a collection of commands relating to games/matches.")

    @grp.command(
        guild_ids=["601387976370683906"],
        description="Flip A Coin for Heads or Tails")
    @commands.has_any_role('WARYES DEVELOPER')
    async def flip(self, ctx: ctx_parse):
        try:
            # List of possible outcomes (heads and tails)
            outcomes = ["Heads", "Tails"]

            # Perform the coin flip
            coin_flip_result = random.choice(outcomes)

            # Print the result
            await ctx.respond(f"{ctx.author.mention} {coin_flip_result}!")
        except Exception as e:
            logger.error(f"{e}")

def setup(bot):
    bot.add_cog(match(bot))
