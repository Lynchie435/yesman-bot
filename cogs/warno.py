import os
import discord
from discord import option
from discord.ext import commands
import logging
from raw import sql, functions as fu

logger = logging.getLogger('logger')
data = []

class WARNO(commands.Cog):
    ctx_parse = discord.ApplicationContext

    def __init__(self, bot: discord.Bot):
        self.bot = bot.user

    # Set slashcommand group and sub groups
    grp = discord.SlashCommandGroup("warno", "This is a collection of commands related to WARNO")
    leaderboardgrp = grp.create_subgroup("leaderboard", "A list of leaderboard commands")

    @staticmethod
    def usernameAutocomplete(ctx: discord.AutocompleteContext):
        try:
            global data

            if not data:
                data = sql.get_whois()

            userlist = [f"{sub['userid']} | {sub['username']}" for sub in data if ctx.value.lower() in str(sub['username']).lower()]
            return list(set(userlist))

        except Exception as e:
            logger.error(f"{e}")

    @grp.command(
        guild_ids=["601387976370683906"],
        description="Returns the last 5 nicknames of the user and also some basic profile statistics.")
    @option("username", description="",
            autocomplete=usernameAutocomplete)
    @commands.has_any_role('WARYES DEVELOPER', 'MEMBER')
    async def whois(self, ctx: ctx_parse, username: str):
        try:

            userid = username.split('|')[0].strip()
            filtered_data = [d for d in data if d.get("userid") == userid and d.get("is_current") == 1]
            username = ', '.join([d["username"] for d in filtered_data])

            json_data = fu.get_data_from_api(str(os.getenv('EUGSTATSAPI')) + userid)

            # Create a Discord embed for displaying the replay information.
            embed = discord.Embed(
                title=f"**{username}**",
                colour=discord.Colour.dark_gold()
            )

            embed.add_field(name="UserID", value=f"{userid}", inline="True")
            embed.add_field(name="Level", value=f"{json_data['@level']}", inline="True")
            embed.add_field(name="", value="Leaderboard", inline=False)
            embed.add_field(name="ELO", value=f"{int(float(json_data['ELO']))}", inline="True")
            embed.add_field(name="Rank", value=f"{json_data['ELO_LB_rank']}", inline="True")
            embed.add_field(name="", value="Ranked", inline=False)
            embed.add_field(name="Won", value=f"{json_data['ranked_win']}", inline="True") if 'ranked_win' in json_data else None
            embed.add_field(name="Lost", value=json_data['ranked_loss'], inline="True") if 'ranked_loss' in json_data else None
            embed.add_field(name="Draw", value=json_data['ranked_draw'], inline="True") if 'ranked_draw' in json_data else None

            # Filter the data based on userid and is_current
            filtered_data = [d for d in data if d.get("userid") == userid and d.get("is_current") == 0]

            # Sort the filtered data based on the start_date field

            sorted_data = sorted(filtered_data, key=lambda x: x["start_date"])

            # Extract the usernames from the sorted data
            usernames = [d["username"] for d in sorted_data]

            # Join the usernames into a single string with newline characters
            names = '\n'.join(usernames) if len(usernames)>0 else "None"

            embed.add_field(name="Last 5 nicknames", value=f"{names}", inline="False")

            # Return the known as
            known_as = str(sorted_data[0]["known_as"]) if sorted_data and sorted_data[0].get("known_as") is not None else ''

            embed.set_footer(text=f"Known As: {known_as} ")

            await ctx.respond(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"{e}")

    # @grp.command(
    #     guild_ids=["601387976370683906"],
    #     description="Get personal stats for WARNO")
    # @option("userid", description="Your must enter your Eugen userId")
    # @commands.has_any_role('WARYES DEVELOPER')
    #
    # async def getrankedstats(self, ctx: ctx_parse, userid: str):
    #     try:
    #
    #
    #         # Create a Discord embed
    #         embed = discord.Embed(title="Player Statistics")
    #
    #         # List of most commonly named fields to include in the embed
    #         fields_to_include = [
    #             "_id", "_rev", "ELO", "ELO_LB_value", "ELO_LB_rank", "ELO_LB_delta_value",
    #             "ELO_LB_delta_rank", "@level", "@xp_multi", "@xp_ranked", "@xp_skirmish",
    #             "@skirmish_played", "@skirmish_win", "@skirmish_loss", "@skirmish_last_game",
    #             "@multi_played", "@multi_win", "@multi_loss", "@multi_draw", "@multi_last_game",
    #             "@nb_tank_bought", "@nb_inf_bought", "@nb_air_bought", "@nb_at_bought",
    #             "@nb_sup_bought", "@nb_reco_bought", "@total_unit_bought", "@deployment_conquest",
    #             "@deployment_closequarter_conquest", "@time_skirmish_played", "@time_multi_played",
    #             "@time_ranked_played", "@time_menu_played", "@time_armory_played",
    #             "ranked_win", "ranked_loss", "ranked_nation_0", "ranked_nation_1", "ranked_last_game",
    #             "@skirmish_nato", "@skirmish_pact", "@multi_nato", "@multi_pact"
    #         ]
    #
    #         # Add fields to the embed
    #         for field_name in fields_to_include:
    #             if field_name in json_data:
    #                 embed.add_field(name=field_name, value=json_data[field_name], inline=False)
    #
    #         # Display the embed
    #         await ctx.respond(embed=embed)
    #         #print(embed.to_dict())
    #
    #     except Exception as e:
    #         logger.error(f"{e}")


def setup(bot):
    bot.add_cog(WARNO(bot))
