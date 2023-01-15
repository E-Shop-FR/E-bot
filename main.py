import discord
from discord import app_commands, utils
from discord.ext import commands

import config


class AClient(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.synced = False
        self.added = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=discord.Object(id=1046437841447686226))
            self.synced = True
        if not self.added:
            self.add_view(TickerLauncher())
            self.added = True
        print(f"We have logged in as {self.user}.")

    async def setup_hook(self) -> None:
        # Register the persistent view for listening here.
        # Note that this does not send the view to any message.
        # In order to do this you need to first send a message with the View, which is shown below.
        # If you have the message_id you can also pass it as a keyword argument, but for this example
        # we don't have one.
        self.add_view(MainView())
        self.add_view(TickerLauncher())
        self.add_view(ConfirmView())


intents = discord.Intents.default()
intents.members = True
client = AClient(intents=intents)
tree = app_commands.CommandTree(client)


class TickerLauncher(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Create a Ticket", custom_id="ticket_button", style=discord.ButtonStyle.blurple)
    async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel_name = f"ticket-for-{interaction.user.name}-{interaction.user.discriminator}".lower()
        print(channel_name)
        ticket = utils.get(interaction.guild.channels, name=channel_name)

        print(ticket)

        if ticket is not None:
            await interaction.response.send_message(f"You already have a ticket open at {ticket.mention}!",
                                                    ephemeral=True)
        else:
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True,
                                                              embed_links=True),
                interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                                  read_message_history=True)
            }
            
            category= discord.utils.get(interaction.guild.categories, id=1059120888064249988)
            channel = await interaction.guild.create_text_channel(
                name=channel_name, overwrites=overwrites,
                reason=f"Ticket for {interaction.user}",
                category = category)
            await channel.send(f"{interaction.user.mention} created a ticket !", view=MainView())
            await interaction.response.send_message(f"I've opened a ticket for you at {channel.mention}!",
                                                    ephemeral=True)


class ConfirmView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.red, custom_id="confirm")
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.channel.delete()
        except:
            await interaction.response.send_message(
                "Channel deletion failed! Make sure I have 'manage_channels' permissions!", ephemeral=True)


class MainView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", custom_id="ticket_button_close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("clicked")
        embed = discord.Embed(title="Are you sure you want to close this ticket ?", color=discord.Colour.blurple())
        await interaction.response.send_message(embed=embed, view=ConfirmView(), ephemeral=True)

    @discord.ui.button(label="Archive Ticket", custom_id="ticket_archive", style=discord.ButtonStyle.blurple)
    async def archive(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("archived")
        embed = discord.Embed(title="Are you sure you want to archive this ticket ?", color=discord.Colour.blurple())
        await interaction.response.send_message(embed=embed, view= ArchiveConfirm(), ephemeral=True)


class ArchiveConfirm(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.red, custom_id="confirm")
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            category= discord.utils.get(interaction.guild.categories, id=1061049218569084948)
            channel = interaction.channel
            if channel.category == category : 
                await interaction.response.send_message("You cannot archive the ticket twice !",ephemeral= True)
                return

            await channel.edit(category=category, name=channel.name+"-archived")
            await interaction.response.defer()
        except:
            await interaction.response.send_message(
                "Channel moving failed! Make sure I have 'manage_channels' permissions!", ephemeral=True)





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


@tree.command(name="ticket", guild=discord.Object(id=1046437841447686226), description="Launches the ticketing system")
async def ticketing(interaction: discord.Interaction):
    embed = discord.Embed(title=":flag_gb::flag_us: If you need support or want to order, click the button below and create a ticket ! \n \n:flag_fr: Si vous avez besoin d'aide ou passer commande ,Clickez sur le boutons en desous et crée un ticket !",
                            color=discord.Colour.blue())
    await interaction.channel.send(embed=embed, view=TickerLauncher())
    await interaction.response.send_message("Ticketing system launched!", ephemeral=True)


@tree.command(name="close", guild=discord.Object(id=1046437841447686226), description="close the ticket")
async def close(interaction: discord.Interaction):
    if "ticket-for-" in interaction.channel.name:
        embed = discord.Embed(title="Are you sure you want to close this ticket ?", color=discord.Colour.blurple())
        await interaction.response.send_message(embed=embed, view=ConfirmView(), ephemeral=True)
    else:
        await interaction.response.send_message("This isn't a ticket !", ephemeral=True)


@tree.command(name="add", guild=discord.Object(id=1046437841447686226), description="Adds a user to the ticket")
@app_commands.describe(user="The user you want to add to the ticket")
async def add(interaction: discord.Interaction, user: discord.Member):
    if "ticket-for-" in interaction.channel.name:
        await interaction.channel.set_permissions(user, view_channel=True, send_messages=True, attach_files=True,
                                                  embed_links=True)

    else:
        await interaction.response.send_message("This isn't a ticket!", ephemeral=True)


@client.event
async def on_member_join(member):
    channel = member.guild.system_channel
    await channel.send(f"Wewewe bvn {member.mention}")



if __name__ == '__main__':
    token = config.get_token()
    if token is None or token == "":
        print("Invalid token ! Please specify a valid one in the config file !")
    else:
        client.run(token)
