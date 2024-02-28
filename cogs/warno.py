import json, math, os, random, re, time, requests
import discord
from bs4 import BeautifulSoup
from discord import option
from discord.ext import commands
import logging
import asyncio
from raw import sql

logger = logging.getLogger('logger')

# Reuse the same session for multiple requests
session = requests.Session()

async def get_leaderboard():
    try:
        url = str(os.getenv('EUGLBAPI'))
        response = requests.get(url)

        if response.status_code == 200:
            json_data = response.json()

            output_file = "./resources/leaderboard.json"
            with open(output_file, 'w') as file:
                json.dump(json_data, file, indent=2)
            logging.info('Downloaded leaderboard to JSON')
    except Exception as e:
        logger.error(f"{e}")

def get_username(gameid_url):
    response = session.get(gameid_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        b_tags = soup.find_all('b')
        for b_tag in b_tags:
            return b_tag.text
    return None

def extract_unix_timestamp(input_string):
    pattern = r'new Date\((\d+\.\d+)\);'
    match = re.search(pattern, input_string)
    return float(match.group(1)) if match else None

def get_gamehistory(userid):
    try:
        # Generate a random delay between 3 and 6 seconds done to make the calls not look so.....
        delay_seconds = random.uniform(3, 6)
        time.sleep(delay_seconds)

        url = str(os.getenv('EUGNETGHAPI'))
        url = f'{url}{userid}'
        response = session.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            game_rows = soup.find_all('tr')
            for row in game_rows:
                columns = row.find_all('td')
                if len(columns) == 3:
                    game_name = columns[0].text.strip()
                    if game_name != 'fulda':
                        return 'No Gamehistory Data'

                    link_element = columns[2].find('a')
                    if link_element is not None and 'href' in link_element.attrs:
                        game_link = link_element['href']
                        username = get_username(game_link)
                        return str(username)
                    else:
                        return "Username Error"
        return None
    except Exception as e:
        logger.error(f"{e}")
async def processUsernames():
    try:
        data = load_json_file('./resources/leaderboard.json')

        if data and 'rows' in data and isinstance(data['rows'], list):
            rows = data["rows"]

            # Combine API request and parsing logic
            modified_rows = [{'position': i + 1,
                              'userid': str(row["id"]).replace('u29_', ''),
                              'username': f"{get_gamehistory(str(row['id']).replace('u29_', ''))}" or None,
                              'rank': str(row["key"]),
                              'elo': math.ceil(float(row["value"]))
                              }
                             for i, row in enumerate(rows[:300])]

            sql.add_usernames_to_db(modified_rows)
        else:
            logger.warning("Invalid JSON structure or 'rows' list not found.")
    except Exception as e:
        logger.error(f"{e}")

def load_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
async def startProcessing():

    while True:

        await get_leaderboard()
        logger.debug('Downloading Leaderboard...')
        logger.debug('Processing Usernames...')
        await processUsernames()
        logger.debug('Processing Finished...')

        sleeptimer = 60 * 60 * 24
        logger.debug(f'Sleeping for {sleeptimer} seconds')

        await asyncio.sleep(sleeptimer)


class WARNO(commands.Cog):
    ctx_parse = discord.ApplicationContext

    def __init__(self, bot: discord.Bot):
        self.bot = bot.user

    # Set slashcommand group and sub groups
    grp = discord.SlashCommandGroup("warno", "This is a collection of commands related to WARNO")
    leaderboardgrp = grp.create_subgroup("leaderboard", "A list of leaderboard commands")

    @grp.command(
        guild_ids=["601387976370683906"],
        description="Get details of a Eugen username, including last 5 nicknames.")
    @option("username", description="Enter the ingame Eugen username")
    @commands.has_any_role('WARYES DEVELOPER')

    async def whois(self, ctx: ctx_parse, username: str):
        try:
            return
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
    #         json_data = fu.get_data_from_api(self.apilist + userid) #684602
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
