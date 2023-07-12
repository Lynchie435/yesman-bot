from io import BytesIO
import json
import re
import requests
from PIL import Image
import discord
from discord import option
from discord.ext import commands
from discord.utils import basic_autocomplete

units = []


class WarYes(commands.Cog):
    ctx_parse = discord.ApplicationContext

    def __init__(self, bot: discord.Bot):
        self.bot = bot.user

    grp = discord.SlashCommandGroup("waryes", "This is a collection of waryes commands")

    @staticmethod
    def unitAutocomplete(self: discord.AutocompleteContext):
        with open('./resources/units.json') as f:
            # load json
            data = json.load(f)

            # get units from json
            global units
            units = data["units"]

        # list of units
        return [f"{sub['name']} :{sub['unitType']['motherCountry']}:" for sub in units]

    @grp.command(
        guild_ids=["601387976370683906"],
        description="")
    @option("unit", description="The unit you wish to retrieve details for.",
            autocomplete=basic_autocomplete(unitAutocomplete))
    @commands.has_any_role('WARYES DEVELOPER', 'MEMBER')
    async def unitget(self, ctx: ctx_parse,
                      unit: str):
        try:

            unitname = unit.split(':')[0].rstrip()
            unitcountry = re.search(r"\:([A-Za-z0-9_]+)\:", unit).group(1)

            # global unitarray
            unitarray = next(
                (item for item in units if
                 item["name"] == unitname and item['unitType']['motherCountry'] == unitcountry),
                None)

            if unitarray is not None:

                embedvar = discord.Embed(title=f"{unitarray['name']} - {unitarray['unitType']['motherCountry']}",
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
                    divisions += self.get_divisionicon(division)

                # add general data to embed
                embedvar.add_field(name="General", value="")
                embedvar.add_field(name="", value=f"**Divisions**: {divisions}"
                                                  f"\n**Points**: {unitarray['commandPoints']} | **Strength**: {unitarray['maxDamage']} | **Optics[Air]**: {unitarray['optics']} [{unitarray['airOptics']}] "
                                                  f"\n**Speed (Road/OffRoad)**: {unitarray['roadSpeed']}/{unitarray['speed']}km/h | **Stealth**: {self.calc_stealth(unitarray['stealth'])}",
                                   inline=False)

                # add armour values if a vehicle
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
                                           value=f"**{weapon['weaponName']} [{self.get_weapontype(weapon['minMaxCategory'])}] ** \n **Traits**: {traits} \n **Range**: GRD: {weapon['groundRange']}m | HELO: {weapon['helicopterRange']}m | AIR: {weapon['planeRange']}m "
                                                 f"\n**Power**: AP: {weapon['penetration']} | HE: {weapon['he']} "
                                                 f"\n**Accuracy**: Static: {weapon['staticAccuracy']}% | Moving: {weapon['movingAccuracy']}%"
                                                 f"\n**Attribs**: RoF: {weapon['rateOfFire']} p/min | Aim: {weapon['aimingTime']}s | Reload: {weapon['reloadTime']}s | Salvo: {weapon['salvoLength']}",
                                           inline=False)

                await ctx.respond(file=file, embed=embedvar)
        except Exception as e:
            print(e)

    def calc_stealth(self, stealthvalue):
        match stealthvalue:
            case 1:
                return 'Bad'
            case 1.5:
                return 'Mediocre'
            case 2:
                return 'Good'
            case 2.5:
                return 'Exceptional'

    def get_divisionicon(self, division):

        # icon codes are as per the WarYes discord
        match division:
            case 'Descriptor_Deck_Division_SOV_35_AirAslt_Brig_multi':
                return '<:35ya:1073600139144482896>'
            case 'Descriptor_Deck_Division_SOV_39_Gds_Rifle_multi':
                return '<:39ya:1073600140419543151>'
            case 'Descriptor_Deck_Division_SOV_79_Gds_Tank_multi':
                return '<:79ya:1073600142848049222>'
            case 'Descriptor_Deck_Division_WP_Unternehmen_Zentrum_multi':
                return '<:untzen:1073600225408733264>'
            case 'Descriptor_Deck_Division_RDA_4_MSD_multi':
                return '<:4mot:1073600127199088651>'
            case 'Descriptor_Deck_Division_RDA_7_Panzer_multi':
                return '<:7mot:1073600134149050378>'
            case 'Descriptor_Deck_Division_RDA_KdA_Bezirk_Erfurt_multi':
                return '<:kda:1073600228659310652>'
            case 'Descriptor_Deck_Division_RFA_TerrKdo_Sud_multi':
                return '<:tks:1073600223068299376>'
            case 'Descriptor_Deck_Division_US_3rd_Arm_multi':
                return '<:3rdarmor:1073600125802401852>'
            case 'Descriptor_Deck_Division_US_8th_Inf_multi':
                return '<:8thinf:1073600135218598039>'
            case 'Descriptor_Deck_Division_US_82nd_Airborne_multi':
                return '<:82nd:1073600144425099265>'
            case 'Descriptor_Deck_Division_RFA_5_Panzer_multi':
                return '<:5pz:1073600131775086622>'
            case 'Descriptor_Deck_Division_RFA_2_PzGrenadier_multi':
                return '<:2pz:1073600154994749490>'
            case 'Descriptor_Deck_Division_UK_1st_Armoured_multi':
                return '<:1starmor:1073600151115018362>'
            case 'Descriptor_Deck_Division_UK_2nd_Infantry_multi':
                return '<:2ndinf:1073600227262611506>'
            case 'Descriptor_Deck_Division_NATO_Garnison_Berlin_multi':
                return '<:berlincmd:1073600146920714271>'
            case 'Descriptor_Deck_Division_FR_11e_Para_multi':
                return '<:11e:1073600137374474270>'
            case 'Descriptor_Deck_Division_FR_5e_Blindee_multi':
                return '<:5e:1073600129828929567>'
            case 'Descriptor_Deck_Division_SOV_119IndTkBrig_multi':
                return '<:119:1128418744465633351>'
            case 'Descriptor_Deck_Division_US_11ACR_multi':
                return '<:11acr:1128418742561427725>'
        return 'None'

    def get_weapontype(self, weaponminmax):
        match weaponminmax:
            case 'MinMax_SAM':
                return 'SAM'
            case 'MinMax_obusier':
                return 'Howitzer'
            case 'MinMax_CanonAP':
                return 'Cannon'
            case 'MinMax_MMG_HMG':
                return 'MMG/HMG'
            case 'MinMax_Mortier':
                return 'Mortar'
            case 'MinMax_ATGM':
                return 'ATGM'
            case 'MinMax_AutocanonHE':
                return 'Autocannon'
            case 'MinMax_DCA':
                return 'SPAAG'
            case 'MinMax_inf_MMG':
                return 'Small Arms'
            case 'MinMax_LAW':
                return 'Antitank'
            case 'MinMax_Grenade':
                return 'Grenade'
            case 'MinMax_MLRS':
                return 'MLRS'
            case 'MinMax_FLAME':
                return 'Flamethrower'
            case 'MinMax_inf_sniper':
                return 'Sniper Rifle'
        return 'UKN'

    async def resize_image_from_url(self, image_url, new_width, new_height):
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        resized_image = image.resize((new_width, new_height))
        resized_image.save("resized_image.png")  # Save the resized image
        return "resized_image.png"


def setup(bot):
    bot.add_cog(WarYes(bot))
