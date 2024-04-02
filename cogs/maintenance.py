import logging
import os

import discord
import requests
from discord.ext import commands

from raw import functions as fu

logger = logging.getLogger(__name__)

class Maintenance(commands.Cog):
    def __init__(self, bot):  # this is a special method that is called when the cog is loaded
        self.bot = bot

    grp = discord.SlashCommandGroup("admin", "This is a collection of admin/bot commands")
    botgrp = grp.create_subgroup("bot", "A list of commands related to the bot")


    @botgrp.command(name="ping", description="Ping the bot")
    @commands.has_any_role('WARYES DEVELOPER')
    async def ping(self, ctx):
        try:
            await ctx.respond(f"Latency is {self.bot.latency} ms")
        except Exception as e:
            logger.error(f"{e}")


    @botgrp.command(name="update_units_file_cache",description="Update unit JSON from the WarYes website.")
    @commands.has_any_role('WARYES DEVELOPER')
    async def update(self, ctx):
        try:
            patchdata = fu.get_data_from_api('https://war-yes.com/api/patch/latest')
            patchname = patchdata['data']['name']

            url = f'https://war-yes.com/static/{patchname}/warno.json'
            destfolder = 'resources'
            self.download(url=url, dest_folder=destfolder)
            await ctx.respond(f"Updated Unit File Cache!")
        except Exception as e:
            logger.error(f"{e}")

    def download(self, url: str, dest_folder: str):
        try:
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)  # create folder if it does not exist

            filename = "units.json"
            file_path = os.path.join(dest_folder, filename)

            r = requests.get(url, stream=True)
            if r.ok:
                print("saving to", os.path.abspath(file_path))
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024 * 8):
                        if chunk:
                            f.write(chunk)
                            f.flush()
                            os.fsync(f.fileno())
            else:  # HTTP status code 4XX/5XX
                #print("Download failed: status code {}\n{}".format(r.status_code, r.text))
                logger.info("Download failed: status code {}\n{}".format(r.status_code, r.text))
        except Exception as e:
            logger.error(f"{e}")
def setup(bot):
    bot.add_cog(Maintenance(bot))
