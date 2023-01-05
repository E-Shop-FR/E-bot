import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run("MTA1MTIwMjUxMDI5MzA1NzY0Nw.GviMZU.SRCECZQ8H5ezfW7LVOMszIpM4gQ48GPlka8H0w")