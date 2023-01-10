import discord
from discord import app_commands, utils
from discord.app_commands import commands


class ticket_launcher(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout = None)

    @discord.ui.button(label="Create a Ticket", custom_id="ticket_button", style=discord.ButtonStyle.blurple)

    async def ticket(self, interaction: discord.Interaction, button:discord.ui.Button):
        ticket = utils.get(interaction.guild.text_channels, name = f"ticket-for-{interaction.user.name}-{interaction.user.discriminator}")
        
        
        if ticket is not None: await interaction.response.send_message(f"You already have aticket open at {ticket.mention=}!", ephemeral = True )
        else:
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel = False),
                interaction.user: discord.PermissionOverwrite(view_channel = True, send_messages = True, attach_files = True, embed_links = True),
                interaction.guild.me: discord.PermissionOverwrite(view_channel = True, send_messages = True, read_message_history = True)
            }

            channel = await interaction.guild.create_text_channel(name = f"ticket-for-{interaction.user.name}-{interaction.user.discriminator}", overwrites = overwrites, reason = f"Ticket for {interaction.user}")
            await channel.send(f"{interaction.user.mention} created a ticket !", view = main)
            await interaction.response.send_message(f"I've opened a ticket for you at {channel.mention}!" , ephemeral = True)

class confirm(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout = None)

    @discord.ui.button(label = "Confirm" , style = discord.ButtonStyle.red, custom_id = "confirm")
    async def confirm_button(self, interaction, button):
        try: await interaction.channel.delete()
        except: await interaction.response.send_message("Channel deletion failed! Make sure I have 'manage_channels' permissions!", ephemeral = True)

class main(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout = None)

    @discord.ui.button(label = "Close Ticket" , style = discord.ButtonStyle.red, custom_id = "close")
    async def close(self, interaction, button):
        embed = discord.Embed(title = "Are you sure you want to close this ticket ?", color = discord.Colour.blurple())
        await interaction.response.send_message(embed = embed, ephemeral = True)

class AClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False
        self.added = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=discord.Object(id=1046437841447686226))
            self.synced = True
        if not self.added:
            self.add_view(ticket_launcher())
            self.added = True
        print(f"We have logged in as {self.user}.")
            
    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello World!')

    async def on_member_join(self, member):
        print(member)


client = AClient()
tree = app_commands.CommandTree(client)


@tree.command(name="fact", description="Tells a TRUE fact", guild=discord.Object(id=1046437841447686226))
async def self(interaction: discord.Interaction, name: str, numb: int):
    await interaction.response.send_message(f"Suicidaul le pdddddddddd {name} {numb}")


@tree.command(name="clear", description="Clear messages", guild=discord.Object(id=1046437841447686226))
async def self(ctx, amount: int = None):  # Set default value as None
    await ctx.response.defer(ephemeral=True)
    if amount is None:
        await ctx.channel.purge(limit=1000000)
    else:
        try:
            int(amount)
        except Exception:  # Error handler
            await ctx.send('Please enter a valid integer as amount.')
        else:
            await ctx.followup.send(f"Cleared {amount} messages.", ephemeral=True)
            await ctx.channel.purge(limit=amount)


@tree.command(name="ticket",guild=discord.Object(id=1046437841447686226), description = "Launches the ticketing system")
async def ticketing(interaction: discord.Interaction):
    embed = discord.Embed(title = "If you need support, click the button below and create a ticket ! ", color = discord.Colour.blue())
    await interaction.channel.send(embed = embed, view = ticket_launcher())
    await interaction.response.send_message("Ticketing system launched!", ephemeral = True)

@tree.command(name="close",guild=discord.Object(id=1046437841447686226), description = "close the ticket")
async def close(interaction: discord.Interaction):
    if "ticket-for-" in interaction.channel.name:
        embed = discord.Embed(title = "Are you sure you want to close this ticket ?", color = discord.Colour.blurple())
        await interaction.response.send_message(embed = embed, view = confirm(), ephemeral = True)
    else: await interaction.response.send_message("This isn't a ticket !", ephemeral = True)

@tree.command(name="add",guild=discord.Object(id=1046437841447686226), description = "Adds a user to the ticket")
@app_commands.describe(user = "The user you want to add to the ticket")
async def add(interaction: discord.Interaction, user: discord.member):
    if "ticket-for-" in interaction.channel.name:
        await interaction.channel.set_permissions(user, view_channel = True, send_messages = True, attach_files = True, embed_links = True)
        
    else: await interaction.response.send_message("This isn't a ticket!", ephemeral = True)

config = open("token.txt", "r")
token = config.read()
config.close()
client.run(token)
