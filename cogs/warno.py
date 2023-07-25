import json

import discord
import raw.functions as fu
from discord import option
from discord.ext import commands
from discord.utils import basic_autocomplete



class WARNO(commands.Cog):
    ctx_parse = discord.ApplicationContext

    def __init__(self, bot: discord.Bot):
        self.bot = bot.user

    # Set slashcommand group and sub groups
    grp = discord.SlashCommandGroup("warno", "This is a collection of commands related to WARNO")
    leaderboardgrp = grp.create_subgroup("leaderboard", "A list of leaderboard commands")
    #mapgrp = grp.create_subgroup("maps", "A list of map commands")

    @grp.command(
        guild_ids=["601387976370683906"],
        description="Get personal stats for WARNO")
    @option("userid", description="Your must enter your Eugen userId")
    @commands.has_any_role('WARYES DEVELOPER')

    async def getrankedstats(self, ctx: ctx_parse, userid: str):
        try:
            json_data = fu.get_data_from_api(f"http://178.32.126.73:8080/stats/u29_{userid}") #684602

            # Create a Discord embed
            embed = discord.Embed(title="Player Statistics")

            # List of most commonly named fields to include in the embed
            fields_to_include = [
                "_id", "_rev", "ELO", "ELO_LB_value", "ELO_LB_rank", "ELO_LB_delta_value",
                "ELO_LB_delta_rank", "@level", "@xp_multi", "@xp_ranked", "@xp_skirmish",
                "@skirmish_played", "@skirmish_win", "@skirmish_loss", "@skirmish_last_game",
                "@multi_played", "@multi_win", "@multi_loss", "@multi_draw", "@multi_last_game",
                "@nb_tank_bought", "@nb_inf_bought", "@nb_air_bought", "@nb_at_bought",
                "@nb_sup_bought", "@nb_reco_bought", "@total_unit_bought", "@deployment_conquest",
                "@deployment_closequarter_conquest", "@time_skirmish_played", "@time_multi_played",
                "@time_ranked_played", "@time_menu_played", "@time_armory_played",
                "ranked_win", "ranked_loss", "ranked_nation_0", "ranked_nation_1", "ranked_last_game",
                "@skirmish_nato", "@skirmish_pact", "@multi_nato", "@multi_pact",
                "@skirmish_nato", "@skirmish_pact"
            ]

            # Add fields to the embed
            for field_name in fields_to_include:
                if field_name in json_data:
                    embed.add_field(name=field_name, value=json_data[field_name], inline=False)

            # Display the embed
            await ctx.respond(embed=embed)
            #print(embed.to_dict())

        except Exception as e:
            print(e)

def setup(bot):
    bot.add_cog(WARNO(bot))
