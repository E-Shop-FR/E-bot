import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Tu est connectez sous le compte {client.user}')


@bot.commands()
async def test(ctx,arg):
    await ctx.send(arg)


bot.run("MTA1MTIwMjUxMDI5MzA1NzY0Nw.GviMZU.SRCECZQ8H5ezfW7LVOMszIpM4gQ48GPlka8H0w")