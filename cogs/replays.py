import json
import parsers.replayParser as rp

class GameData(object):
    def __init__(self, arg1):
        self.__dict__ = json.loads(arg1)


class PlayerData(object):
    def __init__(self, arg1):
        self.__dict__ = json.loads(arg1)


class ResultData(object):
    def __init__(self, arg1):
        self.__dict__ = json.loads(arg1)

def processReplay(file):
    try:

        playersdata = []

        with open(file, "rb") as f:
            # read replay file as binary
            file = f.read()
            parsedfile = rp.parse_file(file)

            # parse out the game data
            game = json.dumps(parsedfile[0].get('game'), indent=2)
            gamedata = GameData(game)  # initialise the json into a dict object

            # parse the player data, looped 20 times in case of team games. Inefficient way of doing this at present
            # but works.
            for i in range(20):
                playerjson = json.dumps(parsedfile[0].get(f'player_{i}'), indent=2)
                if playerjson != 'null':
                    playersdata.append(PlayerData(playerjson))  # initialise the json into a dict object

            # parse out the result data
            result = json.dumps(parsedfile[1].get('result'), indent=2)
            resultdata = ResultData(result)  # initialise the json into a dict object


    except Exception as e:
        print(e)

processReplay("rpl/Tonnoman_vs_SGT_Angel_g1.rpl3")
