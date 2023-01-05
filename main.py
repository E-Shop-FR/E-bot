import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("Ready !")

client.run("MTA1MTIwMjUxMDI5MzA1NzY0Nw.GviMZU.SRCECZQ8H5ezfW7LVOMszIpM4gQ48GPlka8H0w")