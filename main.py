"""
Classe principale du bot.
"""
# Imports
import asyncio

import discord
from discord import app_commands, utils, Activity

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
        self.guild = None

    async def on_ready(self):
        await self.wait_until_ready()
        self.guild = self.get_guild(1046437841447686226)
        if not self.synced:
            await tree.sync(guild=self.guild)
            self.synced = True
        if not self.added:
            self.add_view(TickerLauncher())
            self.added = True
        print(f"🤖 Connexion réussie : {self.user}.")
        self.loop.create_task(self.status_task())

    async def setup_hook(self) -> None:
        self.add_view(MainView())
        self.add_view(TickerLauncher())
        self.add_view(ConfirmView())
        self.add_view(ArchiveConfirm())

    async def set_activity_text(self, text: str):
        activity = discord.Activity(type=discord.ActivityType.watching, name=text)
        await self.change_presence(status=discord.Status.online, activity=activity)

    async def status_task(self):
        while True:
            members_numb = len(self.guild.members)
            await self.set_activity_text(f"{members_numb} membres")
            await asyncio.sleep(10)
            await self.set_activity_text("les commandes de E-shop")
            await asyncio.sleep(10)
            await self.set_activity_text(f"{members_numb} members")
            await asyncio.sleep(10)
            await self.set_activity_text("E-shop's commands")
            await asyncio.sleep(10)


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = AClient(intents=intents)
tree = discord.app_commands.CommandTree(client)
feedback_listen = dict()


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

        ticket = discord.utils.get(
            interaction.guild.channels, name=channel_name)

        if ticket is not None:
            # Le ticket existe déjà
            await interaction.response.send_message(
                f"🇫🇷 Vous avez déjà un ticket ouvert à {ticket.mention}!\n\n🇬🇧🇺🇸 You already have a ticket open at {ticket.mention}!",
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
            category = discord.utils.get(
                interaction.guild.categories, id=1059120888064249988)
            channel = await interaction.guild.create_text_channel(
                name=channel_name, overwrites=overwrites,
                reason=f"Ticket pour {interaction.user}",
                category=category)

            await channel.send(
                f"**Hey <@&1046437980333670510> !**\n🇫🇷{interaction.user.mention} viens de créer un ticket ! Merci de nous donner le plus de détails possibles sur votre demande.\n\n🇬🇧🇺🇸 {interaction.user.mention} created a ticket ! Please give as much detail as possible about your request.",
                view=MainView())
            await interaction.response.send_message(
                f"🇫🇷 J'ai ouvert un ticket pour vous ici {channel.mention}!\n\n🇬🇧🇺🇸 I've opened a ticket for you at {channel.mention}!",
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
                "🇫🇷 Impossible de supprimer le channel. Merci de vérifier que je possède la permission MANAGE_CHANNELS.\n\n\n🇬🇧🇺🇸 I can't delete this channel. Please check that i have the MANAGE_CHANNELS permission.",
                ephemeral=True)


class MainView(discord.ui.View):
    """
    TODO
    """

    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Close", custom_id="ticket_button_close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = "🇫🇷 Voulez-vous vraiment fermer ce ticket ?\n\n🇬🇧🇺🇸 Are you sure you want to close this ticket ?"
        await interaction.response.send_message(msg, view=ConfirmView(), ephemeral=True)

    @discord.ui.button(label="Archive", custom_id="ticket_archive", style=discord.ButtonStyle.blurple)
    async def archive(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg="🇫🇷 Voulez-vous vraiment archiver ce ticket ?\n\n🇬🇧🇺🇸 Are you sure you want to archive this ticket ?"
        await interaction.response.send_message(msg, view=ArchiveConfirm(), ephemeral=True)


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
            category = discord.utils.get(
                interaction.guild.categories, id=1061049218569084948)
            channel = interaction.channel
            if channel.category == category:
                await interaction.response.send_message(
                    "🇫🇷 Vous ne pouvez-pas archiver un ticket déjà archivé !\n\n🇬🇧🇺🇸 You cannot archive a ticket twice !",
                    ephemeral=True)
                return

            await channel.edit(category=category, name=channel.name + "-archived")
            await interaction.response.defer()
        except:
            await interaction.response.send_message(
                "🇫🇷 Impossible de déplacer le channel. Merci de vérifier que je possède la permission MANAGE_CHANNELS.\n\n🇬🇧🇺🇸 I can't archive this channel. Please check that i have the MANAGE_CHANNELS permission.",
                ephemeral=True)


# feedback système
class FeedBack(discord.ui.View):
    """
    TODO
    """

    def __init__(self, freelancer=None) -> None:
        super().__init__(timeout=None)
        self.tab = [None, None, None, freelancer]

        # Button star
    @discord.ui.button(label="⭐️", custom_id="1_star", style=discord.ButtonStyle.blurple)
    async def star_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.tab[0] = interaction.user
        self.tab[2] = 1
        await interaction.response.send_message("🇫🇷 Vous avez mis une note de 1 étoile. \n\n🇬🇧🇺🇸 You have given a 1 star rating.", ephemeral=True)

    # Button star
    @discord.ui.button(label="⭐️⭐️", custom_id="2_star", style=discord.ButtonStyle.blurple)
    async def star_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.tab[0] = interaction.user
        self.tab[2] = 2
        await interaction.response.send_message("🇫🇷 Vous avez mis une note de 2 étoiles. \n\n🇬🇧🇺🇸 You have given a 2 stars rating.", ephemeral=True)

    # Button star
    @discord.ui.button(label="⭐️⭐️⭐️", custom_id="3_star", style=discord.ButtonStyle.blurple)
    async def star_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.tab[0] = interaction.user
        self.tab[2] = 3
        await interaction.response.send_message("🇫🇷 Vous avez mis une note de 3 étoiles. \n\n🇬🇧🇺🇸 You have given a 3 stars rating." , ephemeral=True)

    # Button star
    @discord.ui.button(label="⭐️⭐️⭐️⭐️", custom_id="4_star", style=discord.ButtonStyle.blurple)
    async def star_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.tab[0] = interaction.user
        self.tab[2] = 4
        await interaction.response.send_message("🇫🇷 Vous avez mis une note de 4 étoiles. \n\n🇬🇧🇺🇸 You have given a 4 stars rating.", ephemeral=True)

    # Button star
    @discord.ui.button(label="⭐️⭐️⭐️⭐️⭐️", custom_id="5_star", style=discord.ButtonStyle.blurple)
    async def star_5(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.tab[0] = interaction.user
        self.tab[2] = 5
        await interaction.response.send_message("🇫🇷 Vous avez mis une note de 5 étoiles. \n\n🇬🇧🇺🇸 You have given a 5 stars rating.", ephemeral=True)

    # Button commentaire
    @discord.ui.button(label="💬", custom_id="comment_button", style=discord.ButtonStyle.blurple)
    async def feedbacklaunch(self, interaction: discord.Interaction, button: discord.ui.Button):
        global feedback_listen
        self.tab[0] = interaction.user
        await interaction.response.send_message("🇫🇷 Veuillez écrire votre commentaire. \n\n🇬🇧🇺🇸 Please write your comment.")
        pl = []
        if interaction.channel in feedback_listen:
            pl = feedback_listen[interaction.channel]
        pl.append((interaction.user, self))
        feedback_listen[interaction.channel] = pl

    # Button fini
    @discord.ui.button(label="✅", custom_id="comment_fini", style=discord.ButtonStyle.green)
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not None in self.tab:
            db.add_avis(self.tab[0], self.tab[3], self.tab[1], self.tab[2])
            await interaction.response.send_message("🇫🇷 **Merci pour votre retour !** 💖 \n\n🇬🇧🇺🇸 **Thank you for your feedback !** 💖")
        else:
            await interaction.response.send_message(
                "🇫🇷 Vous n'avez pas donné de note ou de commentaire. \n\n🇬🇧🇺🇸 You have not given a rating or a comment.", ephemeral=True)
            # await interaction.response.defer()


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
    member = interaction.user
    embed = discord.Embed(title="👋 WELCOME !",
                          description=f"🇫🇷 Bienvenue <@{member.id}> ! Nous espérons que tu trouvera ton bonheur dans nos services.\nPour tout comprendre sur notr système de commande, rendez-vous ici : <#1061021846146912347>. \n\n🇬🇧🇺🇸 Welcome <@{member.id}> ! We hope you will find your happiness in our services.\nTo understand our order system, go here : <#1061021846146912347>.", color=discord.Colour.blue())
    embed.set_thumbnail(url=f"{member.display_avatar}")
    await interaction.response.send_message(embed=embed)


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
                '🇫🇷 Veuillez entrer un nombre entier valide comme montant.\n\n🇬🇧🇺🇸 Please enter a valid integer as amount.',
                ephemeral=True)
        else:
            await ctx.followup.send(f'🇫🇷 {amount} messages supprimés.\n\n🇬🇧🇺🇸 {amount} messages deleted.',
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
    await interaction.response.send_message("✅ Système de ticket lancé avec succès !", ephemeral=True)


# Commandes
@tree.command(name="close", guild=discord.Object(id=1046437841447686226), description="Ferme le ticket")
async def close(interaction: discord.Interaction):
    if "ticket-for-" in interaction.channel.name:
        msg="🇬🇧🇺🇸 Are you sure you want to close this ticket ?\n\n🇫🇷Voulez-vous vraiment fermer ce ticket ?"
        await interaction.response.send_message(msg, view=ConfirmView(), ephemeral=True)
    else:
        await interaction.response.send_message(
            "🇬🇧🇺🇸 This channel isn't a ticket !\n\n🇫🇷Ce channel n'est pas un ticket !", ephemeral=True)


# Commandes
@tree.command(name="add", guild=discord.Object(id=1046437841447686226), description="Ajoute un utilisateur au ticket")
@discord.app_commands.describe(user="L'utilisateur à ajouter au ticket")
async def add(interaction: discord.Interaction, user: discord.Member):
    if "ticket-for-" in interaction.channel.name:
        await interaction.channel.set_permissions(user, view_channel=True, send_messages=True, attach_files=True,
                                                  embed_links=True)

    else:
        await interaction.response.send_message(
            "🇬🇧🇺🇸 This channel isn't a ticket !\n\n🇫🇷 Ce channel n'est pas un ticket !", ephemeral=True)


# Commandes
@tree.command(name="feedback", guild=discord.Object(id=1046437841447686226), description="Lance le système de feedback")
async def launchefeedback(interaction: discord.Interaction):
    embed = discord.Embed(title="🌟 FEEDBACK", description="🇫🇷 Afin d'avoir un retour clair sur notre service, nous vous invitons à ajouter un commentaire et une note à E-shop en utilisant les boutons ci-dessous ! Cela ne prendra que quelques minutes.\n\n🇬🇧🇺🇸 To have a honnest feedback on our service, we invite you to add a comment and a rating to E-shop using the buttons below ! This will only take a few minutes.",
                          color=discord.Colour.blue())
    await interaction.channel.send(embed=embed,
                                   view=FeedBack(f"{interaction.user.name} - {interaction.user.discriminator}"))
    await interaction.response.send_message("✅ Système de feedback lancé avec succès !", ephemeral=True)

# Commandes


@tree.command(name="ptsfidelite", guild=discord.Object(id=1046437841447686226), description="fidelise le client")
@discord.app_commands.choices(param=[
    discord.app_commands.Choice(name="reset", value='reset'),
    discord.app_commands.Choice(name="ajouter", value='add'),
    discord.app_commands.Choice(name="retirer", value='remove'),
])
async def ptsfidelite(interaction: discord.Interaction, acheteur: discord.Member, param: str, nbre_point: int):
    if param == 'reset':
        db.reset_client_points(acheteur)

    elif param == 'add':
        db.add_client_points(acheteur, nbre_point)

    elif param == 'remove':
        db.remove_client_points(acheteur, nbre_point)


@client.event
async def on_member_join(member):
    channel = member.guild.system_channel
    embed = discord.Embed(title="👋 WELCOME !",
                          description=f"🇫🇷 Bienvenue <@{member.id}> ! Nous espérons que tu trouvera ton bonheur dans nos services.\nPour tout comprendre sur notr système de commande, rendez-vous ici : <#1061021846146912347>. \n\n🇬🇧🇺🇸 Welcome <@{member.id}> ! We hope you will find your happiness in our services.\nTo understand our order system, go here : <#1061021846146912347>.", color=discord.Colour.blue())
    embed.set_thumbnail(url=f"{member.display_avatar}")
    await channel.send(embed=embed)


@client.event
async def on_message(message):
    if message.channel not in feedback_listen:
        return
    pending_list = feedback_listen[message.channel]
    for el in pending_list:
        if el[0] != message.author:
            continue
        el[1].tab[1] = message.content
        await message.channel.send("🇫🇷 Commentaire enregistré avec succès.\n\n🇬🇧🇺🇸 Comment successfully saved.")
        pending_list.remove(el)
        return


async def send_perm_error(ctx: discord.Interaction):
    channel = ctx.channel
    embed = discord.Embed(title="Vous n'avez pas les permissions pour effectuer cette commande !",
                          description="🇬🇧 You do not have the permission to use this command ! "
                                      "Please contact a staff member if you think that is an error."
                                      "\n\n🇫🇷 Vous n'avez pas les permissions pour effectuer cette commande ! "
                                      "Veuillez contacter le staff si vous pensez que c'est une erreur.", color=discord.Colour.red())

    await channel.send(embed=embed)


if __name__ == '__main__':
    token = config.get_token()
    if token is None or token == "":
        print("❌ Le token n'est pas valide ! Veuillez le renseigner dans le fichier config.json.")
    else:
        client.run(token)
