import io
import json
import random
import re
import requests
from PIL import Image
import discord
from discord import option
from discord.ext import commands
from discord.utils import basic_autocomplete
import pandas as pd
from raw import lookups as lkp, functions as fu

units = []


class WarYes(commands.Cog):
    ctx_parse = discord.ApplicationContext

    def __init__(self, bot: discord.Bot):
        self.bot = bot.user

    # Set slashcommand group and sub groups
    grp = discord.SlashCommandGroup("waryes", "This is a collection of waryes commands")
    unitgrp = grp.create_subgroup("units", "A list of unit commands")
    mapgrp = grp.create_subgroup("maps", "A list of map commands")

    @staticmethod
    def gametypeAutocomplete(self: discord.AutocompleteContext):
        try:
            mapdf = pd.read_json('./resources/maps.json')
            df = mapdf
            gametypelist = list(df["Type"].drop_duplicates())
            return gametypelist
        except Exception as e:
            print(e)

    @staticmethod
    def playerNoAutocomplete(self: discord.AutocompleteContext):
        try:
            chosen_game_type = self.options.get('gametype')

            mapdf = pd.read_json('./resources/maps.json')
            df = mapdf
            df = df.loc[df['Type'] == f'{chosen_game_type}']

            playerno_list = list(df["Players"].drop_duplicates().sort_values())
            return playerno_list
        except Exception as e:
            print(e)

    @staticmethod
    def mapnameAutocomplete(self: discord.AutocompleteContext):
        try:
            chosen_game_type = self.options.get('gametype')
            chosen_player_no = self.options.get('playerno')

            mapdf = pd.read_json('./resources/maps.json')
            df = mapdf
            df = df.loc[(df['Type'] == f'{chosen_game_type}') & (df['Players'] == chosen_player_no)]

            map_list = list(df["Name"].drop_duplicates().sort_values())
            return map_list
        except Exception as e:
            print(e)

    @staticmethod
    def unitAutocomplete(self: discord.AutocompleteContext):
        try:
            with open('./resources/units.json') as f:
                # load json
                data = json.load(f)

                # get units from json
                global units
                units = data["units"]

            # list of units
            return [f"{sub['name']} :{sub['unitType']['motherCountry']}:" for sub in units]
        except Exception as e:
            print(e)

    @mapgrp.command(
        guild_ids=["601387976370683906"],
        description="Randomly select a map from the ranked 1 v 1 pool.")
    @commands.has_any_role('WARYES DEVELOPER', 'MEMBER')
    async def getranked(self, ctx: ctx_parse):
        try:

            # reads maplist json
            mapdf = pd.read_json('./resources/maps.json')
            df = mapdf.loc[mapdf['RankedPool'] == True]

            # gets an image name at random
            map = random.choice(list(df["Image"].drop_duplicates().sort_values()))

            # uses image name to return full row from data frame
            df = mapdf.loc[(mapdf['Image'] == f'{map}')]

            imageurl = df['ImageURL'].iloc[0]
            mapname = df['Name'].iloc[0]

            # populate and response with embed.
            embedvar = discord.Embed(title=f"You have drawn {mapname}!",
                    colour=discord.Colour.random())
            embedvar.set_image(url=f"https://war-yes.com/{imageurl}")

            await ctx.respond(embed=embedvar)
        except Exception as e:
            print(e)

    @mapgrp.command(
        guild_ids=["601387976370683906"],
        description="Get a top down image of the map area and cap zones")
    @option("gametype", description="WARNO Game Mode",
            autocomplete=basic_autocomplete(gametypeAutocomplete))
    @option("playerno", description="Max Players",
            autocomplete=basic_autocomplete(playerNoAutocomplete))
    @option("mapname", description="Map Name",
            autocomplete=basic_autocomplete(mapnameAutocomplete))
    @commands.has_any_role('WARYES DEVELOPER', 'MEMBER')
    async def getoverview(self, ctx: ctx_parse,
                     gametype: str, playerno: int, mapname: str):
        try:
            # get map from maplist and retrieve imageurl
            mapdf = pd.read_json('./resources/maps.json')
            df = mapdf.loc[
                (mapdf['Type'] == f'{gametype}') & (mapdf['Players'] == playerno) & (mapdf['Name'] == f'{mapname}')]

            # concat image url and post
            url = f"https://war-yes.com/{df['ImageURL'].iloc[0]}"

            await ctx.respond(f"{url}")
        except Exception as e:
            print(e)

    @unitgrp.command(
        guild_ids=["601387976370683906"],
        description="Returns an embed with high level unit statistics")
    @option("unit", description="You must use the Eugen stated unit name",
            autocomplete=basic_autocomplete(unitAutocomplete))
    @commands.has_any_role('WARYES DEVELOPER', 'MEMBER')
    async def getunit(self, ctx: ctx_parse,
                      unit: str):
        try:

            # parses the unit name and country from the message
            unitname = unit.split(':')[0].rstrip()
            unitcountry = re.search(r"\:([A-Za-z0-9_]+)\:", unit).group(1)

            # gets the json array that matches the above variables
            unitarray = next(
                (item for item in units if
                 item["name"] == unitname and item['unitType']['motherCountry'] == unitcountry),
                None)

            # if the array is not empty
            if unitarray is not None:

                # gets the div and nation emoji's from the divisions file
                with open('./resources/divisions.json', 'r') as file:
                    json_data = json.load(file)
                    combined_array = json_data.get("nato", []) + json_data.get("pact", [])
                    divlist = {item["descriptor"]: item["division_emoji"] for item in combined_array}
                    nationlist = {item["nation"]: item["nation_emoji"] for item in combined_array}

                # populate embed titles and author link
                embedvar = discord.Embed(
                    title=f"{unitarray['name']} {nationlist.get(unitarray['unitType']['motherCountry'],'')}",
                    colour=discord.Colour.random())
                embedvar.set_author(name=f"Click Here For More Details!",
                                    url=f"https://war-yes.com/unit/{unitarray['descriptorName']}",
                                    icon_url="https://war-yes.com/a973a55405dd1851cc9a.png")

                # resize the image
                resizedimg = await self.resize_image_from_url(
                    f"https://war-yes.com/images/units/{unitarray['descriptorName']}.png",
                    340, 175)

                # add image to embed
                embedvar.set_image(url="attachment://resized_image.png")
                file = discord.File(resizedimg, filename="resized_image.png")  # Create a file object

                # get divisions unit belongs to
                divisions = ''
                for division in unitarray['divisions']:
                    divisions += divlist.get(division,'')

                # add general data to embed
                embedvar.add_field(name="General", value="")
                embedvar.add_field(name="", value=f"**Divisions**: {divisions}"
                                                  f"\n**Points**: {unitarray['commandPoints']} | **Strength**: {unitarray['maxDamage']} | **Optics[Air]**: {lkp.optics.get(unitarray['optics'],'Unknown')} [{unitarray['airOptics']}] "
                                                  f"\n**Speed (Road/OffRoad)**: {unitarray['roadSpeed']}/{unitarray['speed']}km/h | **Stealth**: {lkp.stealth.get(unitarray['stealth'], 'Unknown')}",
                                   inline=False)

                # add additional values based on infoPanelType (Unit Type)
                if unitarray['infoPanelType'] == 'default':
                    embedvar.add_field(name="",
                                       value=f"**Armour**: Front: {unitarray['frontArmor']} | Side: {unitarray['sideArmor']} | Rear: {unitarray['rearArmor']} | Top: {unitarray['topArmor']}"
                                             f"\n**Has Smoke**: {unitarray['hasDefensiveSmoke']}",
                                       inline=False)
                elif unitarray['infoPanelType'] == 'plane':
                    embedvar.add_field(name="",
                                       value=f"**Armour**: Front: {unitarray['frontArmor']} | Side: {unitarray['sideArmor']} | Rear: {unitarray['rearArmor']} | Top: {unitarray['topArmor']}"
                                             f"\n**ECM**: {(unitarray['ecm'] * 100) * -1}% | **Agility**: {unitarray['agility']} | **TravelTime**: {unitarray['travelTime']}s",
                                       inline=False)
                elif unitarray['infoPanelType'] == 'helicopter':
                    embedvar.add_field(name="",
                                       value=f"**Armour**: Front: {unitarray['frontArmor']} | Side: {unitarray['sideArmor']} | Rear: {unitarray['rearArmor']} | Top: {unitarray['topArmor']}"
                                             f"\n**ECM**: {(unitarray['ecm'] * 100) * -1}%",
                                       inline=False)

                # loop weapons array and add the weapons details
                if len(unitarray['weapons']) > 0:
                    embedvar.add_field(name="Weapons", value="")
                    for weapon in unitarray['weapons']:
                        traits = '|'.join(filter(None, weapon['traits']))

                        embedvar.add_field(name="",
                                           value=f"**{weapon['weaponName']} [{lkp.weapontype.get(weapon['minMaxCategory'], 'Unknown')}] ** \n **Traits**: {traits} \n **Range**: GRD: {weapon['groundRange']}m | HELO: {weapon['helicopterRange']}m | AIR: {weapon['planeRange']}m"
                                                 f"\n**Power**: AP: {weapon['penetration']} | HE: {weapon['he']} "
                                                 f"\n**Accuracy**: Static: {weapon['staticAccuracy']}% | Moving: {weapon['movingAccuracy']}%"
                                                 f"\n**Attribs**: RoF: {weapon['rateOfFire']} p/min | Aim: {weapon['aimingTime']}s | Reload: {weapon['reloadTime']}s | Salvo: {weapon['salvoLength']}",
                                           inline=False)

                await ctx.respond(file=file, embed=embedvar)
        except Exception as e:
            print(e)

    async def resize_image_from_url(self, image_url, new_width, new_height):
        response = requests.get(image_url)
        image = Image.open(io.BytesIO(response.content))
        resized_image = image.resize((new_width, new_height))
        resized_image.save("resized_image.png")  # Save the resized image
        return "resized_image.png"


def setup(bot):
    bot.add_cog(WarYes(bot))
