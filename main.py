"""
Classe principale du bot.
"""
# Imports
import discord
from discord import app_commands, utils
import config
import database as db


# Initisalisation du bot
class AClient(discord.Client):
    """
    Discord client
    """

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
        print(f"Connexion réussie : {self.user}.")

    async def setup_hook(self) -> None:
        self.add_view(MainView())
        self.add_view(TickerLauncher())
        self.add_view(ConfirmView())
        self.add_view(ArchiveConfirm())


intents = discord.Intents.default()
client = AClient(intents=intents)
tree = app_commands.CommandTree(client)


# Système de tickets
class TickerLauncher(discord.ui.View):
    """
    TODO
    """

    def __init__(self) -> None:
        super().__init__(timeout=None)

    # Bouton de création de ticket
    @discord.ui.button(label="🎫 Ticket", custom_id="ticket_button", style=discord.ButtonStyle.blurple)
    async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel_name = f"🎫︱ticket-{interaction.user.name}-{interaction.user.discriminator}".lower()

        ticket = utils.get(interaction.guild.channels, name=channel_name)

        if ticket is not None:
            # Le ticket existe déjà
            await interaction.response.send_message(
                f"🇬🇧🇺🇸 You already have a ticket open at {ticket.mention}!\n\n🇫🇷 Vous avez déjà un ticket ouvert à {ticket.mention}!",
                ephemeral=True)
        else:
            # Création du ticket
            overwrites = {
                # Permissions
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True,
                                                              embed_links=True),
                interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                                  read_message_history=True)
            }

            # Création du channel
            category = discord.utils.get(interaction.guild.categories, id=1059120888064249988)
            channel = await interaction.guild.create_text_channel(
                name=channel_name, overwrites=overwrites,
                reason=f"Ticket for {interaction.user}",
                category=category)

            await channel.send(
                f"🇬🇧🇺🇸 {interaction.user.mention} created a ticket ! Please give as much detail as possible about your request.\n\n 🇫🇷 {interaction.user.mention} viens de créer un ticket ! Merci de nous donner le plus de détails possibles sur votre demande.",
                view=MainView())
            await interaction.response.send_message(
                f"🇬🇧🇺🇸 I've opened a ticket for you at {channel.mention}!\n\n🇫🇷 J'ai ouvert un ticket pour vous ici {channel.mention}!",
                ephemeral=True)


# Système de fermeture de tickets
class ConfirmView(discord.ui.View):
    """
    TODO
    """

    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.red, custom_id="confirm")
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.channel.delete()
        except:
            await interaction.response.send_message(
                "🇬🇧🇺🇸 I can't delete this channel. Please check that i have the MANAGE_CHANNELS permission.\n\n🇫🇷 Impossible de supprimer le channel ! Merci de vérifier que je possède la permission MANAGE_CHANNELS",
                ephemeral=True)


class MainView(discord.ui.View):
    """
    TODO
    """

    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Close", custom_id="ticket_button_close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🇬🇧🇺🇸 Are you sure you want to close this ticket ?\n\n🇫🇷 Voulez-vous vraiment fermer ce ticket ?",
            color=discord.Colour.blurple())
        await interaction.response.send_message(embed=embed, view=ConfirmView(), ephemeral=True)

    @discord.ui.button(label="Archive", custom_id="ticket_archive", style=discord.ButtonStyle.blurple)
    async def archive(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🇬🇧🇺🇸 Are you sure you want to archive this ticket ?\n\n🇫🇷 Voulez-vous vraiment archiver ce ticket ?",
            color=discord.Colour.blurple())
        await interaction.response.send_message(embed=embed, view=ArchiveConfirm(), ephemeral=True)


# Système d'archivation de tickets
class ArchiveConfirm(discord.ui.View):
    """
    TODO
    """

    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.red, custom_id="confirm")
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            category = discord.utils.get(interaction.guild.categories, id=1061049218569084948)
            channel = interaction.channel
            if channel.category == category:
                await interaction.response.send_message(
                    "🇬🇧🇺🇸 You cannot archive a ticket twice !\n\n🇫🇷 Vous ne pouvez-pas archiver un ticket déjà archivé !",
                    ephemeral=True)
                return

            await channel.edit(category=category, name=channel.name + "-archived")
            await interaction.response.defer()
        except:
            await interaction.response.send_message(
                "🇬🇧🇺🇸 I can't archive this channel. Please check that i have the MANAGE_CHANNELS permission.\n\n🇫🇷 Impossible d'archiver le channel ! Merci de vérifier que je possède la permission MANAGE_CHANNELS",
                ephemeral=True)


# feedback système
class FeedBack(discord.ui.View):
    """
    TODO
    """

    def __init__(self, freelancer=None, channel=None) -> None:
        super().__init__(timeout=None)
        self.channel = channel
        self.tab = [None, None, None, freelancer]

    # bouton pour lancer le début du feedback
    @discord.ui.button(label="Commente", custom_id="commant_button", style=discord.ButtonStyle.blurple)
    async def feedbacklaunch(self, interaction: discord.Interaction, button: discord.ui.Button):
<<<<<<< Updated upstream
        self.tab[0] = str({interaction.user.name} - {interaction.user.discriminator})
=======
        self.tab[0]= interaction.user
>>>>>>> Stashed changes
        await interaction.response.send_message("écrit maintenant ton commentaire", ephemeral=True)
        self.tab

    # Button star
    @discord.ui.button(label="1star", custom_id="1_star", style=discord.ButtonStyle.blurple)
<<<<<<< Updated upstream
    async def star_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.tab[0] = str({interaction.user.name} - {interaction.user.discriminator})
=======
    async def star_1(self,interaction: discord.Interaction, button: discord.ui.Button):
        self.tab[0]= interaction.user
>>>>>>> Stashed changes
        self.tab[2] = 1
        await interaction.response.send_message("Tu a mis 1 étoile", ephemeral=True)

    # Button star
    @discord.ui.button(label="2star", custom_id="2_star", style=discord.ButtonStyle.blurple)
<<<<<<< Updated upstream
    async def star_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.tab[0] = str({interaction.user.name} - {interaction.user.discriminator})
        self.tab[2] = 2
=======
    async def star_2(self,interaction: discord.Interaction, button: discord.ui.Button):
        self.tab[0]= interaction.user
        self.tab[2]= 2
>>>>>>> Stashed changes
        await interaction.response.send_message("tu a mis 2 étoile", ephemeral=True)

    # Button star
    @discord.ui.button(label="3star", custom_id="3_star", style=discord.ButtonStyle.blurple)
<<<<<<< Updated upstream
    async def star_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.tab[0] = str({interaction.user.name} - {interaction.user.discriminator})
        self.tab[2] = 3
=======
    async def star_3(self,interaction: discord.Interaction, button: discord.ui.Button):
        self.tab[0]= interaction.user
        self.tab[2]= 3
>>>>>>> Stashed changes
        await interaction.response.send_message("tu a mis 2 étoile", ephemeral=True)

    # Button star
    @discord.ui.button(label="4star", custom_id="4_star", style=discord.ButtonStyle.blurple)
<<<<<<< Updated upstream
    async def star_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.tab[0] = str({interaction.user.name} - {interaction.user.discriminator})
        self.tab[2] = 4
=======
    async def star_4(self,interaction: discord.Interaction, button: discord.ui.Button):
        self.tab[0]= interaction.user
        self.tab[2]= 4
>>>>>>> Stashed changes
        await interaction.response.send_message("tu a mis 2 étoile", ephemeral=True)

    # Button star
    @discord.ui.button(label="5star", custom_id="5_star", style=discord.ButtonStyle.blurple)
<<<<<<< Updated upstream
    async def star_5(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.tab[0] = str({interaction.user.name} - {interaction.user.discriminator})
        self.tab[2] = 5
=======
    async def star_5(self,interaction: discord.Interaction, button: discord.ui.Button):
        self.tab[0]= interaction.user
        self.tab[2]= 5
>>>>>>> Stashed changes
        await interaction.response.send_message("tu a mis 2 étoile", ephemeral=True)

    # Button fini
    @discord.ui.button(label="finish", custom_id="comment_fini", style=discord.ButtonStyle.green)
<<<<<<< Updated upstream
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("voila votre commentaire est fini", ephemeral=True)
        # demander a mega pour la db

=======
    async def finish(self,interaction: discord.Interaction, button: discord.ui.Button):
        if not None in self.tab:
            db.add_avis(self.tab[0], self.tab[3], self.tab[1], self.tab[2])
            await interaction.response.send_message("voila votre commentaire est fini", ephemeral=True)
        else:
            await interaction.response.send_message("attention tu n'a pas mis d'étoile ou tu n'a pas mis un commentaire !",ephemeral=True)
            await interaction.response.defer()
>>>>>>> Stashed changes

# Commandes
@tree.command(name="ping", description="Pong !", guild=discord.Object(id=1046437841447686226))
async def ping(interaction: discord.Interaction):
    """
    Renvoie la latence du bot
    """
    await interaction.response.send_message(f"🏓 Pong ! {round(client.latency, 3)} ms!")


@tree.command(name="test", description="Test dev", guild=discord.Object(id=1046437841447686226))
async def test(interaction: discord.Interaction):
    """
    Test dev
    """
    db.add_avis(interaction.user, "Test", "Carré", 5)
    await interaction.response.send_message("Test")


# Commandes
@tree.command(name="clear", description="Retirer des messages d'un channel",
              guild=discord.Object(id=1046437841447686226))
async def self(ctx, amount: int = None):
    """
    Retire des messages d'un channel
    """
    await ctx.response.defer(ephemeral=True)
    if amount is None:
        await ctx.channel.purge(limit=1000000)
    else:
        try:
            int(amount)
        except Exception:  # Error handler
            await ctx.send(
                '🇬🇧🇺🇸 Please enter a valid integer as amount.\n\n🇫🇷 Veuillez entrer un nombre entier valide comme montant.',
                ephemeral=True)
        else:
            await ctx.followup.send(f'🇬🇧🇺🇸 {amount} messages deleted.\n\n🇫🇷 {amount} messages supprimés.',
                                    ephemeral=True)
            await ctx.channel.purge(limit=amount)


# Commandes
@tree.command(name="ticket", guild=discord.Object(id=1046437841447686226),
              description="Lance le système de ticket en affichant le message avec la réaction")
async def ticketing(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🇬🇧🇺🇸 If you need support or want to order, click the button below to create a ticket ! \n\n🇫🇷 Si vous avez besoin d'aide ou que vous souhaitez passer commande, clickez sur le bouton ci-dessous pour créer un ticket !",
        color=discord.Colour.blue())
    await interaction.channel.send(embed=embed, view=TickerLauncher())
    await interaction.response.send_message("Ticketing system launched!", ephemeral=True)


# Commandes
@tree.command(name="close", guild=discord.Object(id=1046437841447686226), description="Ferme le ticket")
async def close(interaction: discord.Interaction):
    if "ticket-for-" in interaction.channel.name:
        embed = discord.Embed(
            title="🇬🇧🇺🇸 Are you sure you want to close this ticket ?\n\n🇫🇷Voulez-vous vraiment fermer ce ticket ?",
            color=discord.Colour.blurple())
        await interaction.response.send_message(embed=embed, view=ConfirmView(), ephemeral=True)
    else:
        await interaction.response.send_message(
            "🇺🇸🇬🇧 This channel isn't a ticket !\n\n🇫🇷Ce channel n'est pas un ticket !", ephemeral=True)


# Commandes
@tree.command(name="add", guild=discord.Object(id=1046437841447686226), description="Ajoute un utilisateur au ticket")
@app_commands.describe(user="L'utilisateur à ajouter au ticket")
async def add(interaction: discord.Interaction, user: discord.Member):
    if "ticket-for-" in interaction.channel.name:
        await interaction.channel.set_permissions(user, view_channel=True, send_messages=True, attach_files=True,
                                                  embed_links=True)

    else:
        await interaction.response.send_message(
            "🇺🇸🇬🇧 This channel isn't a ticket !\n\n🇫🇷 Ce channel n'est pas un ticket !", ephemeral=True)


# Commandes
@tree.command(name="feedback", guild=discord.Object(id=1046437841447686226), description="Lance le système de feedback")
async def launchefeedback(interaction: discord.Interaction):
    embed = discord.Embed(title="🇬🇧🇺🇸 anglais ! \n\n🇫🇷 francais  !",
                          color=discord.Colour.blue())
    await interaction.channel.send(embed=embed,
                                   view=FeedBack({interaction.user.name} - {interaction.user.discriminator}))
    await interaction.response.send_message("feedback système launched", ephemeral=True)

# Commandes
@tree.command(name="point_fidelite", guild=discord.Object(id=1046437841447686226), description="ajoute les point de fidéliter")



@client.event
async def on_member_join(member):
    channel = member.guild.system_channel
    # TODO Embed
    await channel.send(f"Wewewe bvn {member.mention}")


if __name__ == '__main__':
    token = config.get_token()
    if token is None or token == "":
        print("Le token n'est pas valide ! Veuillez le renseigner dans le fichier config.json.")
    else:
        client.run(token)
