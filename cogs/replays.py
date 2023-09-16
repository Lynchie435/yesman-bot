import json
import raw.lookups as lkp
import discord
import parsers.replayParser as rp
import raw.sql as sql

from parsers import deckParser


def processReplay(filename, filecontent, message):
    try:

        playersdata = []

        parsedfile = rp.parse_file(filecontent)

        # parse out the game data
        game = json.dumps(parsedfile[0].get('game'), indent=2)
        gamedata = json.loads(game)  # initialise the json into a dict object

        # parse the player data, looped 20 times in case of team games. Inefficient way of doing this at present
        # but works.
        for i in range(20):
            playerjson = json.dumps(parsedfile[0].get(f'player_{i}'), indent=2)
            playerdata = json.loads(playerjson)
            if playerjson != 'null':
                playersdata.append(playerdata)  # initialise the json into a dict object

        # parse out the result data
        result = json.dumps(parsedfile[1].get('result'), indent=2)
        resultdata = json.loads(result)  # initialise the json into a dict object
        resultdata['OwnerAlliance'] = parsedfile[0].get('ingamePlayerId',
                                                        '9')  # Add the playeringameid to the result dict, ingamePlayerID is the alliance of the replay owner

        embedvar = discord.Embed(
            title=f"WARNO Replay",
            colour=discord.Colour.dark_gold())

        winnerlist = []
        loserlist = []
        owneralliance = int(resultdata.get("OwnerAlliance", 9))  # Gets the alliance of the replay owner
        ownervictory = int(
            resultdata.get('Victory', 0))  # Gets the victory value of the replay owner (default to 0 if not found)

        if len(playersdata) == 4 and owneralliance in [2,3]:
            owneralliance = 1
        elif len(playersdata) == 6 and owneralliance in [3,4,5]:
            owneralliance = 1
        elif len(playersdata) == 8 and owneralliance in [4,5,6,7]:
            owneralliance = 1

        for player_data in playersdata:
            player_alliance = int(player_data.get("PlayerAlliance", 9))  # Gets the alliance of the current player

            if player_alliance == owneralliance:
                if ownervictory >= 3:
                    winnerlist.append(player_data)
                else:
                    loserlist.append(player_data)
            else:
                if ownervictory < 3:
                    winnerlist.append(player_data)
                else:
                    loserlist.append(player_data)

        # Concat winner names and loser names for the embed.
        winners = "".join(["||" + winners.get("PlayerName", "") + "||\n" for winners in winnerlist])
        losers = "".join(["||" + losers.get("PlayerName", "") + "||\n" for losers in loserlist])

        # Add Winners and Losers to the Embed
        embedvar.add_field(name="Winner(s)", value=f"{winners}")
        embedvar.add_field(name="Loser(s)", value=f"{losers}")
        embedvar.add_field(name="Victory Type", value=f"||{lkp.victory.get(ownervictory, 9)}||")

        # Add Duration of Game
        minutes, seconds = divmod(int(resultdata.get('Duration')), 60)
        hours, minutes = divmod(minutes, 60)
        time_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        embedvar.add_field(name="Game Duration", value=f"||{time_formatted}||")

        with open('./resources/maps.json') as file:
            json_data = file.read()

        # Parse JSON data into a Python list of dictionaries
        maps_list = json.loads(json_data)

        # Create a dictionary mapping 'EugenName' to 'Name'
        eugen_name_to_name = {map_data['EugenName']: map_data['Name'] for map_data in maps_list}
        map_name = eugen_name_to_name.get(gamedata.get("Map"))

        # Use the map_name in the embed
        embedvar.add_field(name="Map", value=f"{map_name or 'Unknown'}")

        # Now list all the players and their details
        for player_data in playersdata:
            # Add seperator for each player
            embedvar.add_field(name="------------------------------------", value=f"", inline=False)

            # Get the Deck Label
            link_label = "View on WarYes"
            link_url = f"https://war-yes.com/deck-builder?code={player_data.get('PlayerDeckContent')}"
            formatted_link = f"[{link_label}]({link_url})"

            embedvar.add_field(name="Player",
                               value=f"{player_data.get('PlayerName')} (UID: {player_data.get('PlayerUserId')})",
                               inline=False)
            embedvar.add_field(name="ELO", value=f"{player_data.get('PlayerElo')}")
            embedvar.add_field(name="Division", value=f"{deckParser.getDivision(player_data.get('PlayerDeckContent'))}")
            embedvar.add_field(name="Deck", value=f"{formatted_link}")

        sql.add_replay_to_db(filename, gamedata, playersdata, resultdata, "Replay Upload", message.author.name)

        return embedvar
    except Exception as e:
        print(e)