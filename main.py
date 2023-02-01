"""
Classe principale du bot.
"""
# Imports
import asyncio

import discord
from discord.ext import commands
import config
import database as db
from discord.ext import tasks
import datetime
import os
from pytz import timezone


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

        # Db
        if not sendDbBackup.is_running():
            sendDbBackup.start()

        # Logs
        embed = discord.Embed(title="🟢 Le bot est en ligne !",
                              color=discord.Colour.dark_green())
        print(f"🤖 Connexion réussie : {self.user}.")
        self.loop.create_task(self.status_task())
        if not config.get("DEV_MODE"):
            channelLog = client.get_channel(1068629560209440780)
            await channelLog.send(embed=embed)

    async def status_task(self):
        guild = self.get_guild(1046437841447686226)
        emoji_dict = {
            'animated': False,
            'id': 1070410297300504708,
            'name': "discord"
        }
        while True:
            await self.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching,
                                          name=f"{len(guild.members)} membres", emoji=emoji_dict))
            await asyncio.sleep(10)
            await self.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching,
                                          name='Les commandes de E-Shop', emoji=emoji_dict))
            await asyncio.sleep(10)
            await self.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching,
                                          name=f"{len(guild.members)} members", emoji=emoji_dict))
            await asyncio.sleep(10)
            await self.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching,
                                          name="E-Shop's commands", emoji=emoji_dict))
            await asyncio.sleep(10)

    async def setup_hook(self) -> None:
        self.add_view(MainView())
        self.add_view(TickerLauncher())
        self.add_view(ConfirmView())
        self.add_view(ArchiveConfirm())
        self.add_view(ConfirmClose())


client_intents = discord.Intents.default()
client_intents.members = True
client_intents.message_content = True
client = AClient(intents=client_intents)
tree = discord.app_commands.CommandTree(client)
feedback_listen = dict()


class TickerLauncher(discord.ui.View):
    """
    Objet contenant 1 bouton avec l'évenement création ticket
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
                f"🇫🇷 Vous avez déjà un ticket ouvert à {ticket.mention}!\n\n"
                f"🇬🇧🇺🇸 You already have a ticket open at {ticket.mention}!",
                ephemeral=True)
        elif interaction.user.guild_permissions.send_messages is False:
            # L'utilisateur a été mute
            await interaction.response.send_message(
                f"🇫🇷 Vous avez été mute, vous ne pouvez pas ouvrir de ticket!\n\n"
                f"🇬🇧🇺🇸 You have been muted, you cannot open a ticket!",
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

            # Log ouverture ticket
            channelLog = client.get_channel(1068629560209440780)

            # Création du channel
            category = discord.utils.get(
                interaction.guild.categories, id=1059120888064249988)
            channel = await interaction.guild.create_text_channel(
                name=channel_name, overwrites=overwrites,
                reason=f"Ticket pour {interaction.user}",
                category=category)

            await channel.send(
                f"**Hey <@&1046437980333670510> !**\n🇫🇷{interaction.user.mention} viens de créer un ticket ! "
                f"Merci de nous donner le plus de détails possibles sur votre demande.\n\n"
                f"🇬🇧🇺🇸 {interaction.user.mention} created a ticket ! "
                f"Please give as much detail as possible about your request.",
                view=MainView())
            await interaction.response.send_message(
                f"🇫🇷 J'ai ouvert un ticket pour vous ici {channel.mention}!\n\n"
                f"🇬🇧🇺🇸 I've opened a ticket for you at {channel.mention}!",
                ephemeral=True)

            # Log ouverture ticket
            channelLog = client.get_channel(1068629560209440780)

            # Date conversion et formatage
            date = interaction.created_at
            date = date.astimezone(tz=timezone('Europe/Paris'))
            date = date.strftime("%d/%m/%Y à %H:%M:%S")

            embed = discord.Embed(title="🎫 TICKET CREE",
                                  description=f"""
                                  **Nom du channel :** {channel.name}
                                  \n**Crée par :** {interaction.user.mention}
                                  \n**Date de création :** {date}""", color=discord.Colour.green())
            await channelLog.send(embed=embed)


class ConfirmView(discord.ui.View):
    """
    Objet contenant 1 bouton avec l'évenement confirmation fermeture ticket
    """

    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.red, custom_id="confirm")
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.manage_channels is False:
            await interaction.response.send_message(
                f"🇫🇷 Vous n'avez pas la permission pour supprimer ce ticket!\n\n"
                f"🇬🇧🇺🇸 You don't have permission to delete this ticket!",
                ephemeral=True)
            return
        try:
            # Log delete ticket
            channelLog = client.get_channel(1068629560209440780)
            # Fetch des users ayant parlé dans le channel
            users = [message.author.mention async for message in interaction.channel.history(limit=200)]
            users = list(set(users))  # Suppression des doublons
            users = ", ".join(users)  # Conversion en string

            # Date conversion et formatage
            date = interaction.created_at
            date = date.astimezone(tz=timezone('Europe/Paris'))
            date = date.strftime("%d/%m/%Y à %H:%M:%S")

            embed = discord.Embed(title="🎫 TICKET suprimer",
                                  description=f"""**Nom du channel :** {interaction.channel.name}
                                    \n**Fermé par :** {interaction.user.mention}
                                    \n **Utilisateurs ayant parlé dans le ticket :** {users}
                                    \n**Date de supression :** {date}""", color=discord.Colour.red())
            await channelLog.send(embed=embed)

            # delet channel
            await interaction.channel.delete()
        except:
            await interaction.response.send_message(
                "🇫🇷 Impossible de supprimer le channel. Merci de vérifier "
                "que je possède la permission MANAGE_CHANNELS.\n\n"
                "🇬🇧🇺🇸 I can't delete this channel. Please check that i have the MANAGE_CHANNELS permission.",
                ephemeral=True)


class ConfirmClose(discord.ui.View):
    """
    Objet contenant 1 bouton avec l'évenement confirmation fermeture ticket
    """

    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.red, custom_id="confirm")
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.manage_channels is False:
            await interaction.response.send_message(
                f"🇫🇷 Vous n'avez pas la permission de fermer ce ticket!\n\n"
                f"🇬🇧🇺🇸 You don't have permission to fermer this ticket!",
                ephemeral=True)
            return
        try:
            # Log fermeture ticket
            channelLog = client.get_channel(1068629560209440780)
            # Fetch des users ayant parlé dans le channel
            users = [message.author.mention async for message in interaction.channel.history(limit=200)]
            users = list(set(users))  # Suppression des doublons
            users = ", ".join(users)  # Conversion en string

            # Date conversion et formatage
            date = interaction.created_at
            date = date.astimezone(tz=timezone('Europe/Paris'))
            date = date.strftime("%d/%m/%Y à %H:%M:%S")

            embed = discord.Embed(title="🎫 TICKET FERME",
                                  description=f"""**Nom du channel :** {interaction.channel.name}
                                    \n**Fermé par :** {interaction.user.mention}
                                    \n **Utilisateurs ayant parlé dans le ticket :** {users}
                                    \n**Date de finition :** {date}""", color=discord.Colour.red())
            await channelLog.send(embed=embed)

            # kick du joueur channel
            user = interaction.user
            if "ticket-" in interaction.channel.name:
                await interaction.channel.set_permissions(user, view_channel=False)

            else:
                await interaction.response.send_message(
                    "🇬🇧🇺🇸 This channel isn't a ticket !\n\n🇫🇷 Ce channel n'est pas un ticket !", ephemeral=True)

        except:
            await interaction.response.send_message(
                "🇫🇷 Impossible de kick le joueur.",
                ephemeral=True)


class MainView(discord.ui.View):
    """
    Objet contenant 2 boutons avec les évenements de fermeture et d'archivage de tickets    
    """

    def __init__(self) -> None:
        super().__init__(timeout=None)

    # bouton qui kick le client du ticket
    @discord.ui.button(label="Delete", custom_id="ticket_button_delete", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = "🇫🇷 Voulez-vous vraiment suprimer ce ticket ?\n\n🇬🇧🇺🇸 Are you sure you want to delete this ticket ?"
        await interaction.response.send_message(msg, view=ConfirmView(), ephemeral=True)

    # bouton qui suprime le ticket
    @discord.ui.button(label="Close", custom_id="ticket_button_close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = "🇫🇷 Voulez-vous vraiment fermer ce ticket ?\n\n🇬🇧🇺🇸 Are you sure you want to close this ticket ?"
        await interaction.response.send_message(msg, view=ConfirmClose(), ephemeral=True)

    # bouton qui archive le client du ticket
    @discord.ui.button(label="Archive", custom_id="ticket_archive", style=discord.ButtonStyle.blurple)
    async def archive(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = "🇫🇷 Voulez-vous vraiment archiver ce ticket ?\n\n🇬🇧🇺🇸 Are you sure you want to archive this ticket ?"
        await interaction.response.send_message(msg, view=ArchiveConfirm(), ephemeral=True)


class ArchiveConfirm(discord.ui.View):
    """
    Objet contenant 1 bouton avec l'évenement confirmation archivage ticket
    """

    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.red, custom_id="confirm")
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.manage_channels is False:
            await interaction.response.send_message(
                f"🇫🇷 Vous n'avez pas la permission d'archiver ce ticket!\n\n"
                f"🇬🇧🇺🇸 You don't have permission to archive this ticket!",
                ephemeral=True)
            return
        try:
            category = discord.utils.get(
                interaction.guild.categories, id=1061049218569084948)
            channel = interaction.channel
            if channel.category == category:
                await interaction.response.send_message(
                    "🇫🇷 Vous ne pouvez-pas archiver un ticket déjà archivé !\n\n"
                    "🇬🇧🇺🇸 You cannot archive a ticket twice !",
                    ephemeral=True)
                return

            await channel.edit(category=category, name=channel.name + "-archived")
            await interaction.response.defer()

            # Log archive ticket
            channelLog = client.get_channel(1068629560209440780)

            # Log fermeture ticket
            channelLog = client.get_channel(1068629560209440780)
            # Fetch des users ayant parlé dans le channel
            users = [message.author.mention async for message in interaction.channel.history(limit=200)]
            users = list(set(users))  # Suppression des doublons
            users = ", ".join(users)  # Conversion en string

            # Date conversion et formatage
            date = interaction.created_at
            date = date.astimezone(tz=timezone('Europe/Paris'))
            date = date.strftime("%d/%m/%Y à %H:%M:%S")

            embed = discord.Embed(title="🎫 TICKET ARCHIVE",
                                  description=f"""**Channel :** {interaction.channel.mention}
                                    \n**Fermé par :** {interaction.user.mention}
                                    \n **Utilisateurs ayant parlé dans le ticket :** {users}
                                    \n**Date de fermeture :** {date}""", color=discord.Colour.blurple())
            await channelLog.send(embed=embed)

        except:
            await interaction.response.send_message(
                "🇫🇷 Impossible de déplacer le channel. "
                "Merci de vérifier que je possède la permission MANAGE_CHANNELS.\n\n"
                "🇬🇧🇺🇸 I can't archive this channel. Please check that i have the MANAGE_CHANNELS permission.",
                ephemeral=True)


class Questionnaire(discord.ui.Modal):

    def __init__(self, feedback_view):
        super(Questionnaire, self).__init__(title='Comment for feedback')
        self.feedback_view = feedback_view
        self.name = discord.ui.TextInput(label="Please enter your comment there", min_length=0, max_length=30)
        self.add_item(self.name)

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.user != self.feedback_view.feedbacker:
            await interaction.response.defer()
            return
        self.feedback_view.commentary = self.name.value
        await interaction.response.send_message(f'Thanks for your response, {self.name}!', ephemeral=True)


class FeedBack(discord.ui.View):
    """
    Objet contenant 6 boutons avec les évenements de feedback
    """

    def __init__(self, feedbacker: discord.Member, freelancer: discord.Member):
        super().__init__(timeout=None)
        self.feedbacker = feedbacker
        self.commentary = None
        self.star_numb = 5
        self.freelancer = freelancer

    @discord.ui.select(
        max_values=1,
        min_values=1,
        placeholder="Sélectionnez votre note",
        options=[
            discord.SelectOption(label="⭐", description="1 Etoile"),
            discord.SelectOption(label="⭐⭐", description="2 Etoiles"),
            discord.SelectOption(label="⭐⭐⭐", description="3 Etoiles"),
            discord.SelectOption(label="⭐⭐⭐⭐", description="4 Etoiles"),
            discord.SelectOption(label="⭐⭐⭐⭐⭐", description="5 Etoiles", default=True)
        ])
    async def mark(self, interaction: discord.Interaction, menu: discord.ui.Select):
        if interaction.user != self.feedbacker:
            await interaction.response.defer()
            return
        self.star_numb = len(menu.values[0])
        if self.star_numb == 1:
            await interaction.response.send_message(
                "🇫🇷 Vous avez mis une note de 1 étoile. \n\n🇬🇧🇺🇸 You have given a 1 star rating.", ephemeral=True)
        else:
            await interaction.response.send_message(
                f"🇫🇷 Vous avez mis une note de {self.star_numb} étoile. \n\n"
                f"🇬🇧🇺🇸 You have given a {self.star_numb} star rating.", ephemeral=True)

    # Button commentaire
    @discord.ui.button(label="💬", custom_id="comment_button", style=discord.ButtonStyle.blurple)
    async def feedbacklaunch(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Questionnaire(self))

    # Button fini
    @discord.ui.button(label="✅", custom_id="comment_fini", style=discord.ButtonStyle.green)
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.commentary is not None:
            db.add_avis(self.feedbacker, self.freelancer.name, self.commentary, self.star_numb)
            if self.star_numb in (1, 2):
                await interaction.response.send_message(
                    "🇫🇷 Commentaire enregistré avec succès. "
                    "Nous sommes désolés de votre déception face à notre service. "
                    "Votre commentaire sera pris en compte afin que cela n'arrive plus. \n\n"
                    "🇬🇧🇺🇸 Feedback successfully saved."
                    "We are sorry for your disappointment with our service. "
                    "Your comment will be taken into account so that this does not happen again.")
            else:
                await interaction.response.send_message(
                    "🇫🇷 **Merci pour votre retour !** 💖 \n\n🇬🇧🇺🇸 **Thank you for your feedback !** 💖")

            # Embed
            channelLog = client.get_channel(1061023547402768505)
            embed = discord.Embed(title="📝 FEEDBACK",
                                  description=f"""
            **Client :** {interaction.user.mention}
            **Freelancer :** {self.freelancer}
            **Note :** {self.star_numb}/5
            **Commentaire :** {self.commentary}
            """, color=discord.Color.purple())
            embed.set_thumbnail(url=interaction.user.avatar)
            message = await channelLog.send(embed=embed)
            await message.add_reaction("✅")

        else:
            await interaction.response.send_message(
                "🇫🇷 Vous n'avez pas donné de note ou de commentaire. \n\n"
                "🇬🇧🇺🇸 You have not given a rating or a comment.",
                ephemeral=True)
            # await interaction.response.defer()


# Commandes
@tree.command(name="ping", description="Pong !", guild=discord.Object(id=1046437841447686226))
async def ping(interaction: discord.Interaction):
    """
    Renvoie la latence du bot
    """
    await interaction.response.send_message(f"🏓 Pong ! {round(client.latency, 3)} ms!")


@tree.command(name="test", description="Test dev", guild=discord.Object(id=1046437841447686226))
@commands.has_permissions(administrator=True)
async def test(interaction: discord.Interaction):
    """
    Test dev
    """
    member = interaction.user
    embed = discord.Embed(title="👋 WELCOME !",
                          description=f"🇫🇷 Bienvenue <@{member.id}> ! "
                                      f"Nous espérons que tu trouvera ton bonheur dans nos services.\n"
                                      f"Pour tout comprendre sur notr système de commande, "
                                      f"rendez-vous ici : <#1061021846146912347>. \n\n"
                                      f"🇬🇧🇺🇸 Welcome <@{member.id}> ! "
                                      f"We hope you will find your happiness in our services.\n"
                                      f"To understand our order system, go here : <#1061021846146912347>.",
                          color=discord.Colour.blue())
    embed.set_thumbnail(url=f"{member.display_avatar}")
    await interaction.response.send_message(embed=embed)


@tree.command(name="clear", description="Retirer des messages d'un channel",
              guild=discord.Object(id=1046437841447686226))
@commands.has_permissions(manage_channels=True)
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
                '🇫🇷 Veuillez entrer un nombre entier valide comme montant.\n\n'
                '🇬🇧🇺🇸 Please enter a valid integer as amount.',
                ephemeral=True)
        else:
            await ctx.followup.send(f'🇫🇷 {amount} messages supprimés.\n\n🇬🇧🇺🇸 {amount} messages deleted.',
                                    ephemeral=True)
            await ctx.channel.purge(limit=amount)


@tree.command(name="ticket", guild=discord.Object(id=1046437841447686226),
              description="Lance le système de ticket en affichant le message avec la réaction")
@commands.has_permissions(administrator=True)
async def ticketing(interaction: discord.Interaction):
    """
    Lance le système de ticket en affichant le message avec la réaction
    """
    embed = discord.Embed(
        title="🇬🇧🇺🇸 If you need support or want to order, click the button below to create a ticket ! \n\n"
              "🇫🇷 Si vous avez besoin d'aide ou que vous souhaitez passer commande, "
              "clickez sur le bouton ci-dessous pour créer un ticket !",
        color=discord.Colour.blue())
    await interaction.channel.send(embed=embed, view=TickerLauncher())
    await interaction.response.send_message("✅ Système de ticket lancé avec succès !", ephemeral=True)


@tree.command(name="close", guild=discord.Object(id=1046437841447686226), description="Ferme le ticket")
@commands.has_permissions(manage_channels=True)
async def close(interaction: discord.Interaction):
    """
    Ferme le ticket
    """
    if "ticket-for-" in interaction.channel.name:
        msg = "🇬🇧🇺🇸 Are you sure you want to close this ticket ?\n\n🇫🇷Voulez-vous vraiment fermer ce ticket ?"
        await interaction.response.send_message(msg, view=ConfirmView(), ephemeral=True)
    else:
        await interaction.response.send_message(
            "🇬🇧🇺🇸 This channel isn't a ticket !\n\n🇫🇷Ce channel n'est pas un ticket !", ephemeral=True)


# Commandes
@tree.command(name="ticketadd", guild=discord.Object(id=1046437841447686226),
              description="Ajoute un utilisateur au ticket")
@discord.app_commands.describe(user="L'utilisateur à ajouter au ticket")
async def add(interaction: discord.Interaction, user: discord.Member):
    """
    Ajoute un utilisateur au ticket
    """
    if "ticket-for-" in interaction.channel.name:
        await interaction.channel.set_permissions(user, view_channel=True, send_messages=True, attach_files=True,
                                                  embed_links=True)

    else:
        await interaction.response.send_message(
            "🇬🇧🇺🇸 This channel isn't a ticket !\n\n🇫🇷 Ce channel n'est pas un ticket !", ephemeral=True)


@tree.command(name="feedback", guild=discord.Object(id=1046437841447686226), description="Lance le système de feedback")
@discord.app_commands.describe(freelancer="Freelancer concerné")
async def launch_feedback(interaction: discord.Interaction, freelancer: discord.Member):
    embed = discord.Embed(title="🌟 FEEDBACK",
                          description="🇫🇷 Afin d'avoir un retour clair sur notre service, "
                                      "nous vous invitons à ajouter un commentaire et une note à E-shop "
                                      "en utilisant les boutons ci-dessous ! "
                                      "Cela ne prendra que quelques minutes.\n\n"
                                      "🇬🇧🇺🇸 To have a honnest feedback on our service, "
                                      "we invite you to add a comment and a rating to E-shop using the buttons below ! "
                                      "This will only take a few minutes.",
                          color=discord.Colour.blue())
    await interaction.channel.send(embed=embed,
                                   view=FeedBack(feedbacker=interaction.user, freelancer=freelancer))
    await interaction.response.send_message("✅ Système de feedback lancé avec succès !", ephemeral=True)


# Message de bienvenue
@client.event
async def on_member_join(member):
    channel = member.guild.system_channel
    embed = discord.Embed(title="👋 WELCOME !",
                          description=f"🇫🇷 Bienvenue <@{member.id}> ! "
                                      f"Nous espérons que vous serez satisfait par nos services.\n"
                                      f"Pour tout comprendre sur notr système de commande, "
                                      f"rendez-vous ici : <#1061021846146912347>. \n\n"
                                      f"🇬🇧🇺🇸 Welcome <@{member.id}> ! We hope you will be satisfied by our services.\n"
                                      f"To understand our order system, go here : <#1061021846146912347>.",
                          color=discord.Colour.blue())
    embed.set_thumbnail(url=f"{member.display_avatar}")
    await channel.send(embed=embed)


# Commentaires pour le feedback
@client.event
async def on_message(message):
    if message.channel not in feedback_listen:
        return
    pending_list = feedback_listen[message.channel]
    for el in pending_list:
        if el[0] != message.author:
            continue
        el[1].commentary = message.content
        await message.channel.send("🇫🇷 Commentaire enregistré avec succès.\n\n🇬🇧🇺🇸 Comment successfully saved.")
        pending_list.remove(el)
        return


@tasks.loop(time=datetime.time(hour=23, minute=0, second=0))  # Minuit en France (UTC+1)
async def sendDbBackup():
    fichier = "resources/database.db"
    channel = client.get_channel(1068629536700366959)
    print("Envoi de la base de données...")
    await channel.send("Database du " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n Taille : " + str(
        os.path.getsize(fichier)) + " octets", file=discord.File(fichier))


if __name__ == '__main__':
    token = config.get_token()
    if token is None or token == "":
        print("❌ Le token n'est pas valide ! Veuillez le renseigner dans le fichier config.json.")
    else:
        client.run(token)
