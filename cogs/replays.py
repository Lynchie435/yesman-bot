# Import necessary libraries and modules
import json
import math
import urllib.parse
import raw.lookups as lkp
import discord
import parsers.replayParser as rp
import raw.sql as sql
from raw.functions import calculate_md5_hash
from parsers import deckParser
import logging

logger = logging.getLogger('logger')

def append_winlose_list(player, replayPlayer, listA, listB):
    if replayPlayer == int(player['PlayerAlliance']):
        listA.append(player)
    else:
        listB.append(player)

# Define a function called processReplay that takes three parameters: filename, filecontent, and message.
def processReplay(filename, filecontent, message):
    try:
        # Initialize an empty list to store player data.
        playersdata = []

        # Parse the file content using a replay parser and store it in parsedfile.
        parsedfile = rp.parse_file(filecontent)

        # Extract and parse game data from parsedfile.
        game = json.dumps(parsedfile[0].get('game'), indent=2)
        gamedata = json.loads(game)

        # Extract and parse player data from the parsedfile.
        jsondata = json.dumps(parsedfile[0])
        data = json.loads(jsondata)
        playersdata = {key: value for key, value in data.items() if key.startswith("player_")}

        # Extract and parse result data from parsedfile.
        result = json.dumps(parsedfile[1].get('result'), indent=2)
        resultdata = json.loads(result)
        resultdata['OwnerAlliance'] = parsedfile[0].get('ingamePlayerId', '9')

        # Create a Discord embed for displaying the replay information.
        embedvar = discord.Embed(
            title=f"WARNO Replay",
            colour=discord.Colour.dark_gold()
        )

        # Initialize lists for winners and losers of the game.
        winnerlist = []
        loserlist = []

        # Get the alliance and victory data for the replay owner.
        owneralliance = int(resultdata.get("OwnerAlliance", 0))
        ownervictory = int(resultdata.get('Victory', 0))

        if ownervictory < 3:
            listA = loserlist
            listB = winnerlist
        else:
            listA = winnerlist
            listB = loserlist

        for player_key, players_data in playersdata.items():
            if player_key.startswith('player_') and isinstance(players_data, dict):
                player_data = players_data
                if len(playersdata) == 2:
                    replayPlayer = owneralliance
                elif len(playersdata) == 4:
                    replayPlayer = 1 if owneralliance in [2, 3] else 0
                elif len(playersdata) == 6:
                    replayPlayer = 1 if owneralliance in [3, 4] else 0
                elif len(playersdata) == 8:
                    replayPlayer = 1 if owneralliance in [4, 5, 6, 7] else 0
                append_winlose_list(player_data, replayPlayer, listA, listB)

        # Concatenate winner and loser names for embedding.
        winners = "".join(["||" + winners.get("PlayerName", "") + "||\n" for winners in winnerlist])
        losers = "".join(["||" + losers.get("PlayerName", "") + "||\n" for losers in loserlist])

        # Add winner and loser fields to the embed.
        embedvar.add_field(name="Winner(s)", value=f"{winners}")
        embedvar.add_field(name="Loser(s)", value=f"{losers}")
        embedvar.add_field(name="Victory Type", value=f"||{lkp.victory.get(ownervictory, 9)}||")

        # Calculate and add the game duration to the embed.
        minutes, seconds = divmod(int(resultdata.get('Duration')), 60)
        hours, minutes = divmod(minutes, 60)
        time_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        embedvar.add_field(name="Game Duration", value=f"||{time_formatted}||")

        # Read map data from a JSON file and map Eugen names to human-readable map names.
        with open('./resources/maps.json') as file:
            json_data = file.read()

        original_map_name = gamedata.get("Map")
        maps_list = json.loads(json_data)
        eugen_name_to_name = {map_data['EugenName']: map_data['Name'] for map_data in maps_list}
        map_name = eugen_name_to_name.get(gamedata.get("Map"))

        # Add the map name to the embed.
        embedvar.add_field(name="Map", value=f"{map_name or original_map_name}")

        # Iterate through player data and add details to the embed.
        for player_key, players_data in playersdata.items():
            if player_key.startswith('player_') and isinstance(players_data, dict):
                player_data = players_data
                embedvar.add_field(name="------------------------------------", value=f"", inline=False)
                link_label = "View on WarYes"
                link_url = f"https://war-yes.com/deck-builder?code={urllib.parse.quote(player_data.get('PlayerDeckContent'))}"
                formatted_link = f"[{link_label}]({link_url})"
                embedvar.add_field(
                    name="Player",
                    value=f"{player_data.get('PlayerName')} (UID: {player_data.get('PlayerUserId')})",
                    inline=False
                )
                embedvar.add_field(name="ELO", value=f"{math.ceil(float(player_data.get('PlayerElo')))}")
                embedvar.add_field(name="Division", value=f"{deckParser.getDivision(player_data.get('PlayerDeckContent'))}")
                embedvar.add_field(name="Deck", value=f"{formatted_link}")

        # Add replay data to a SQL database.
        md5 = calculate_md5_hash(filecontent)
        sql.add_replay_to_db(filename, gamedata, json.dumps(playersdata), resultdata, "Replay Upload", message.author.name, md5)

        logger.info(f'Processed replay {filename} that was submitted by {message.author.name}')
        # Return the Discord embed containing the replay information.
        return embedvar
    except Exception as e:
        logger.error(f"{e}")
