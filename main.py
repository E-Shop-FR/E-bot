import discord
from discord.ext import commands

bot = commands.Bot(command_prefix = "!", description = "Bot de Suicidaul")

@bot.event
async def on_ready():
    print("Ready !")

bot.run("MTA1MTIwMjUxMDI5MzA1NzY0Nw.GviMZU.SRCECZQ8H5ezfW7LVOMszIpM4gQ48GPlka8H0w")