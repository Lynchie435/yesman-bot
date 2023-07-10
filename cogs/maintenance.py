import os

import discord
from discord.ext import commands
import requests

class Maintenance(commands.Cog):
    def __init__(self, bot):  # this is a special method that is called when the cog is loaded
        self.bot = bot

    grp = discord.SlashCommandGroup("maint", "This is a collection of maintenance commands")

    @grp.command(name="ping", description="Ping the bot")
    @commands.has_any_role('WARYES DEVELOPER')
    async def ping(self, ctx):
        try:
            await ctx.respond(f"Latency is {self.bot.latency} ms")
        except Exception as e:
            print(e)


    @grp.command(name="update_cache",description="Update file cache from the website")
    @commands.has_any_role('WARYES DEVELOPER')
    async def update(self, ctx):
        try:
            url = 'https://firebasestorage.googleapis.com/v0/b/catur-11410.appspot.com/o/warno%2Funits-and-divisions.json?alt=media'
            destfolder = 'resources'
            self.download(url=url, dest_folder=destfolder)
            await ctx.respond(f"Updated Unit File Cache!")
        except Exception as e:
            print(e)

    def download(self, url: str, dest_folder: str):
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
            print("Download failed: status code {}\n{}".format(r.status_code, r.text))
def setup(bot):
    bot.add_cog(Maintenance(bot))
