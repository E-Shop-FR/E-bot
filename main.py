"""
Classe principale du bot.
"""
# Imports
import asyncio
from typing import Optional

import discord
from discord.ext import commands
import config
import database as db
from discord.ext import tasks
import datetime
import calendar
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
        if config.get_dev_mode() == "False":
            embed = discord.Embed(title="🟢 Le bot est en ligne !",
                                  color=discord.Colour.dark_green())
            channelLog = client.get_channel(1068629560209440780)
            await channelLog.send(embed=embed)
        

        print(f"🤖 Connexion réussie : {self.user}.")
        self.loop.create_task(self.status_task())

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
                                          name=f"🫡 {len(guild.members)} membres", emoji=emoji_dict))
            await asyncio.sleep(10)
            await self.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching,
                                          name='🛒 Les commandes de E-Shop', emoji=emoji_dict))
            await asyncio.sleep(10)
            await self.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching,
                                          name=f"🫡 {len(guild.members)} members", emoji=emoji_dict))
            await asyncio.sleep(10)
            await self.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching,
                                          name="🛒 E-Shop's commands", emoji=emoji_dict))
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
                f"**Hey <@&1046437980333670510> !**\n🇫🇷{interaction.user.mention} viens de créer un ticket !"
                f"\nMerci de nous donner le plus de détails possibles sur votre demande, notament si c'est dans le cadre d'une commande :\n"
                f"- Une description précise de votre demande \n - Une deadline (date limite de réalisation de la demande) \n- Votre budget (optionnel) \n- Votre cahier des charges (optionnel) \n\- **Tous les détails que vous jugerez utiles !**\n"
                f"\n🇬🇧🇺🇸{interaction.user.mention} just created a ticket !"
                f"\nPlease give us as much details as possible about your request, especially if it is in the context of an order:\n"
                f"- A precise description of your request \n - A deadline \n- Your budget (optional) \n- Your specifications (optional) \n\- **All the details that you think will be useful !**",
                view=MainView())
            await interaction.response.send_message(
                f"🇫🇷 J'ai ouvert un ticket pour vous ici {channel.mention}!\n\n"
                f"🇬🇧🇺🇸 I've opened a ticket for you at {channel.mention}!",
                ephemeral=True)

            # Log ouverture ticket
            channelLog = client.get_channel(1068629560209440780)

            # Date conversion et formatage
            
            #date = interaction.created_at
            #date = date.astimezone(tz=timezone('Europe/Paris'))
            #date = date.strftime("%d/%m/%Y à %H:%M:%S")

            date = datetime.datetime.utcnow()
            utc_time = calendar.timegm(date.utctimetuple())
            date = "<t:{}:f>".format(utc_time)

            embed = discord.Embed(title="🎫 TICKET CREE",
                                  description=f"""
                                  **Channel :** {channel.mention} (`{channel.name}`)
                                  \n**Crée par :** {interaction.user.mention} (`{interaction.user.id}`)
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
        else:
            try:
                # Log delete ticket
                channelLog = client.get_channel(1068629560209440780)
                # Fetch des users ayant parlé dans le channel
                users = [message.author.mention async for message in interaction.channel.history(limit=200)]
                users = list(set(users))  # Suppression des doublons
                users = ", ".join(users)  # Conversion en string

                # Date conversion et formatage
                date = datetime.datetime.utcnow()
                utc_time = calendar.timegm(date.utctimetuple())
                date = "<t:{}:f>".format(utc_time)

                embed = discord.Embed(title="🎫 TICKET SUPPRIME",
                                      description=f"""
                                      **Channel :** {interaction.channel.mention} (`{interaction.channel.name}`)
                                        \n**Fermé par :** {interaction.user.mention} (`{interaction.user.id}`)
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
        try:
            if "ticket-" in interaction.channel.name:
                # Log fermeture ticket
                channelLog = client.get_channel(1068629560209440780)
                # Fetch des users ayant parlé dans le channel
                users = [message.author.mention async for message in interaction.channel.history(limit=200)]
                users = list(set(users))  # Suppression des doublons
                users = ", ".join(users)  # Conversion en string

                # Date conversion et formatage
                date = datetime.datetime.utcnow()
                utc_time = calendar.timegm(date.utctimetuple())
                date = "<t:{}:f>".format(utc_time)

                embed = discord.Embed(title="🎫 TICKET FERME",
                                      description=f"""
                                      **Channel :** {interaction.channel.mention} (`{interaction.channel.name}`)
                                        \n**Fermé par :** {interaction.user.mention} (`{interaction.user.id}`)
                                        \n **Utilisateurs ayant parlé dans le ticket :** {users}
                                        \n**Date de fermeture :** {date}""", color=discord.Colour.yellow())
                await channelLog.send(embed=embed)

                # kick du joueur channel
                user = interaction.user
                await interaction.channel.set_permissions(user, view_channel=False)

                # envoi message de fermeture
                await interaction.channel.send(
                    f"🇫🇷 Ce ticket a été fermé par {interaction.user.mention}."
                )
            else:
                await interaction.response.send_message(
                    "🇬🇧🇺🇸 This channel isn't a ticket !\n\n🇫🇷 Ce channel n'est pas un ticket !", ephemeral=True)

        except:
            await interaction.response.send_message(
                "🇫🇷 Impossible de supprimer le channel.",
                ephemeral=True)


class MainView(discord.ui.View):
    """
    Objet contenant 2 boutons avec les évenements de fermeture et d'archivage de tickets    
    """

    def __init__(self) -> None:
        super().__init__(timeout=None)

    # bouton qui kick le client du ticket
    @discord.ui.button(label="❌ Delete", custom_id="ticket_button_delete", style=discord.ButtonStyle.blurple)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = "🇫🇷 Voulez-vous vraiment suprimer ce ticket ?\n\n🇬🇧🇺🇸 Are you sure you want to delete this ticket ?"
        await interaction.response.send_message(msg, view=ConfirmView(), ephemeral=True)

    # bouton qui suprime le ticket
    @discord.ui.button(label="✅ Close", custom_id="ticket_button_close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = "🇫🇷 Voulez-vous vraiment fermer ce ticket ?\n\n🇬🇧🇺🇸 Are you sure you want to close this ticket ?"
        await interaction.response.send_message(msg, view=ConfirmClose(), ephemeral=True)

    # bouton qui archive le client du ticket
    @discord.ui.button(label="🗃️ Archive", custom_id="ticket_archive", style=discord.ButtonStyle.green)
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
        else:
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
                date = datetime.datetime.utcnow()
                utc_time = calendar.timegm(date.utctimetuple())
                date = "<t:{}:f>".format(utc_time)

                embed = discord.Embed(title="🎫 TICKET ARCHIVE",
                                      description=f"""
                                      **Channel :** {interaction.channel.mention} (`{interaction.channel.name}`)
                                        \n**Fermé par :** {interaction.user.mention} (`{interaction.user.id}`)
                                        \n **Utilisateurs ayant parlé dans le ticket :** {users}
                                        \n**Date de fermeture :** {date}""", color=discord.Colour.blurple())
                await channelLog.send(embed=embed)

                await interaction.channel.send(
                    f"🇫🇷 Ce ticket a été archivé par {interaction.user.mention}."
                )

            except:
                await interaction.response.send_message(
                    "🇫🇷 Impossible de déplacer le channel. "
                    "Merci de vérifier que je possède la permission MANAGE_CHANNELS.\n\n"
                    "🇬🇧🇺🇸 I can't archive this channel. Please check that i have the MANAGE_CHANNELS permission.",
                    ephemeral=True)


class Questionnaire(discord.ui.Modal):
    """
    Objet contenant 1 champ de texte avec l'évenement confirmation commentaire
    """

    def __init__(self, feedback_view):
        super(Questionnaire, self).__init__(title='Comment for feedback')
        self.feedback_view = feedback_view
        self.name = discord.ui.TextInput(
            label="Please enter your comment there", min_length=0, max_length=30)
        self.add_item(self.name)

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.user != self.feedback_view.feedbacker:
            await interaction.response.defer()
            return
        self.feedback_view.commentary = self.name.value
        await interaction.response.send_message(f'🇫🇷 Merci pour votre réponse. \n\n🇬🇧🇺🇸 Thanks for your response', ephemeral=True)


class FeedBack(discord.ui.View):
    """
    Objet contenant 6 boutons avec les évenements de feedback
    """

    def __init__(self, feedbacker: discord.Member, freelancer: discord.Member):
        super().__init__(timeout=None)
        self.freelancer = freelancer
        self.commentary = None
        self.star_numb = 5
        self.feedbacker = feedbacker

    @discord.ui.select(
        max_values=1,
        min_values=1,
        placeholder="Sélectionnez votre note",
        options=[
            discord.SelectOption(label="⭐", description="1 Etoile"),
            discord.SelectOption(label="⭐⭐", description="2 Etoiles"),
            discord.SelectOption(label="⭐⭐⭐", description="3 Etoiles"),
            discord.SelectOption(label="⭐⭐⭐⭐", description="4 Etoiles"),
            discord.SelectOption(
                label="⭐⭐⭐⭐⭐", description="5 Etoiles", default=True)
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
            db.add_avis(self.feedbacker, self.freelancer.id,
                        self.commentary, self.star_numb)
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
                    "🇫🇷 **Merci pour votre retour ! "
                    "Rendez-vous dans le channel <#1061023547402768505> "
                    "pour ajouter la réaction sous votre message pour certifier son authenticité.** 💖 \n\n"
                    "🇬🇧🇺🇸 **Thank you for your feedback ! "
                    "Go to the channel <#1061023547402768505> "
                    "to add the reaction under your message to certify its authenticity.** 💖")

            # Embed
            channelLog = client.get_channel(1061023547402768505)
            embed = discord.Embed(title="📝 FEEDBACK",
                                  description=f"""
            **Seller :** {self.freelancer}
            **Client :** {interaction.user.mention}
            **Rating :** {self.star_numb}/5
            **Comment :** {self.commentary}
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

"""
@tree.command(name="test", description="Test dev", guild=discord.Object(id=1046437841447686226))
@commands.has_permissions(administrator=True)
async def test(interaction: discord.Interaction):
    channel = interaction.channel
    member = interaction.user
    
    embed = discord.Embed(title="👋 WELCOME !",
                          description=f"🇫🇷 Bienvenue <@{member.id}> ! "
                                      f"Nous espérons que vous serez satisfait par nos services.\n"
                                      f"Pour tout comprendre sur notre système de commande, "
                                      f"rendez-vous ici : <#1061021846146912347>. \n\n"
                                      f"🇬🇧🇺🇸 Welcome <@{member.id}> ! We hope you will be satisfied by our services.\n"
                                      f"To understand our order system, go here : <#1061021846146912347>.",
                          color=discord.Colour.blue())
    embed.set_thumbnail(url=f"{member.display_avatar}")

    message = await channel.send(embed=embed)
    await message.add_reaction("👋")
"""
    



@tree.command(name="clear", description="Retirer des messages d'un channel",
              guild=discord.Object(id=1046437841447686226))
@discord.app_commands.checks.has_permissions(manage_channels=True)
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
@discord.app_commands.checks.has_permissions(administrator=True)
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
@discord.app_commands.checks.has_permissions(manage_channels=True)
async def close(interaction: discord.Interaction):
    """
    Ferme le ticket
    """
    if "ticket-" in interaction.channel.name:
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
    if "ticket-" in interaction.channel.name:
        await interaction.channel.set_permissions(user, view_channel=True, send_messages=True, attach_files=True,
                                                  embed_links=True)
        await interaction.response.send_message(
            f"🇫🇷 {user} a désormais accès à ce ticket.\n\n🇬🇧🇺🇸 {user} has now access to this ticket.")
        channelLog = client.get_channel(1068629560209440780)
        
        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())
        date = "<t:{}:f>".format(utc_time)

        channelLog = client.get_channel(1068629560209440780)
        embed = discord.Embed(title=" 📥 TICKET ADD",
                            description=f"""
                            **Ticket : ** {interaction.channel.mention} `({interaction.channel.name})`
                            \n**Utilisateur ajouté :** {user.mention} `({user.id})`
                            \n**Par :** {interaction.user.mention} `({interaction.user.id})`
                            \n** Date de l'ajout :** {date}""",
                            color=discord.Colour.purple())
        await channelLog.send(embed=embed)

    else:
        await interaction.response.send_message(
            "🇬🇧🇺🇸 This channel isn't a ticket !\n\n🇫🇷 Ce channel n'est pas un ticket !", ephemeral=True)


@tree.command(name="feedback", guild=discord.Object(id=1046437841447686226), description="Lance le système de feedback")
@discord.app_commands.checks.has_permissions(manage_channels=True)
@discord.app_commands.describe(freelancer="Le freelancer à qui donner le feedback")
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

@tree.command(name="ticketremove", guild=discord.Object(id=1046437841447686226),
                description="Retire un utilisateur du ticket")
@discord.app_commands.describe(user="L'utilisateur à retirer du ticket")
@discord.app_commands.checks.has_permissions(manage_channels=True)
async def remove(interaction: discord.Interaction, user: discord.Member):
    """
    Retire un utilisateur du ticket
    """
    if "ticket-" in interaction.channel.name:
            date = datetime.datetime.utcnow()
            utc_time = calendar.timegm(date.utctimetuple())
            date = "<t:{}:f>".format(utc_time)

            await interaction.channel.set_permissions(user, view_channel=False, send_messages=False, attach_files=False,
                                                  embed_links=False)
            await interaction.response.send_message(
                f"🇫🇷 {user} n'a désormais plus accès à ce ticket.\n\n🇬🇧🇺🇸 {user} has no more access to this ticket.")
            channelLog = client.get_channel(1068629560209440780)
            embed = discord.Embed(title="📤 TICKET REMOVE",
                            description=f"""
                            **Ticket : ** {interaction.channel.mention} `({interaction.channel.name})`
                            \n**Utilisateur retiré :** {user.mention} `({user.id})`
                            \n**Par :** {interaction.user.mention} `({interaction.user.id})`
                            \n** Date du retrait :** {date}""",
                            color=discord.Colour.purple())
            await channelLog.send(embed=embed)

@tree.command(name="proposition", guild=discord.Object(id=1046437841447686226), description="Lance le système d'estimation")
@discord.app_commands.describe(client="Le client à qui faire l'estimation", product = "Récapiltlatif de la commande", price="Le prix de la commande")
@discord.app_commands.checks.has_permissions(manage_channels=True)
async def launch_estimate(interaction: discord.Interaction, client: discord.Member, product: str, price: int):
    embed = discord.Embed(title="📈 OFFRE POUR LA COMMANDE",
                          description=f"""
                          **Vendeur :** {interaction.user.mention}
                          **Client :** {client.mention}
                          **Récapitulatif de la commande :** {product}
                          **Prix proposé par le vendeur :** {price}€              
                          """,
                          color=discord.Colour.blue())
    embed.set_footer(text="Attention, ce message est affiché à titre indicatif car le prix de la commande ne dépasse 25€ peut pas être considérée comme un devis ou une facture.\nEn confirmant la commande, vous acceptez les conditions générales de vente de E-shop.")
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ Système d'estimation lancé avec succès !", ephemeral=True)

@tree.command(name="points", guild=discord.Object(id=1046437841447686226), description="Permet de modifier ou visualiser les points de fidélité d'un client")
@discord.app_commands.choices(action=[
    discord.app_commands.Choice(name="reset", value='reset'),
    discord.app_commands.Choice(name="add", value='add'),
    discord.app_commands.Choice(name="remove", value='remove'),
    discord.app_commands.Choice(name="show", value='show')
])
async def fidelity_points(interaction: discord.Interaction, user: discord.Member, action: str, points: Optional[int]):
    """
    Modifie les points de fidélité d'un client
    """
    channelLog = client.get_channel(1068629560209440780)
    if action == 'reset':
        db.reset_client_points(user)
        await interaction.response.send_message(
            f"🇫🇷 Points de fidélité de {user} réinitialisés avec succès ! \n\n🇬🇧🇺🇸 {user} fidelity points reset with success !")
        embed = discord.Embed(title="🌟 POINTS DE FIDÉLITÉ",
                              description="Action : Réinitialisation\n"
                              f"Victime : {user.mention}\n"
                              f"Par : {interaction.user.mention}\n"
                              f"Points : {db.get_client_points(user)}",
                              color=discord.Colour.red())
        await channelLog.send(embed=embed)

    elif action == 'add':
        db.add_client_points(user, points)
        await interaction.response.send_message(
            f"🇫🇷 {points} points de fidélité ajoutés à {user} avec succès ! \n\n🇬🇧🇺🇸 {points} fidelity points added to {user} with success !")
        embed = discord.Embed(title="🌟 POINTS DE FIDÉLITÉ",
                              description="Action : Ajout\n"
                              f"Victime : {user.mention}\n"
                              f"Par : {interaction.user.mention}\n"
                              f"Points : {db.get_client_points(user)}",
                                    color=discord.Colour.green())
        await channelLog.send(embed=embed)

    elif action == 'remove':
        db.remove_client_points(user, points)
        await interaction.response.send_message(
            f"🇫🇷 {points} points de fidélité retirés à {user} avec succès ! \n\n🇬🇧🇺🇸 {points} fidelity points removed to {user} with success !")
        embed = discord.Embed(title="🌟 POINTS DE FIDÉLITÉ",
                              description="Action : Retrait\n"
                              f"Victime : {user.mention}\n"
                              f"Par : {interaction.user.mention}\n"
                              f"Points : {db.get_client_points(user)}",
                                    color=discord.Colour.orange())
        await channelLog.send(embed=embed)

    else:
        points = db.get_client_points(user)
        await interaction.response.send_message(
            f"🇫🇷 Nombre de points de {user} : {points} 🌟\n\n🇬🇧🇺🇸 {user} fidelity points : {points} 🌟")
        embed = discord.Embed(title="🌟 POINTS DE FIDÉLITÉ",
                              description="Action : Visualisation\n"
                              f"Victime : {user.mention}\n"
                              f"Par : {interaction.user.mention}\n"
                              f"Points : {db.get_client_points(user)}",
                                    color=discord.Colour.yellow())
        await channelLog.send(embed=embed)

'''
@tree.error
async def error_handler(interaction: discord.Interaction, error):
    if config.get("DEV_MODE") == "False":
        # if isinstance(error, discord.app_commands.errors.Forbidden):
        #     await interaction.response.send_message("❌ Je n'ai pas les permissions nécessaires pour effectuer cette action !", ephemeral=True)
        if isinstance(error, discord.app_commands.errors.HTTPException):
            await interaction.response.send_message("❌ Une erreur est survenue lors de l'envoi du message !", ephemeral=True)
        # elif isinstance(error, discord.app_commands.errors.NotFound):
        #         await interaction.response.send_message("❌ Une erreur est survenue lors de l'envoi du message !", ephemeral=True)
         # elif isinstance(error, discord.app_commands.errors.MissingRequiredArgument):
        #     await interaction.response.send_message("❌ Vous n'avez pas renseigné tous les arguments nécessaires !", ephemeral=True)
        # elif isinstance(error, discord.app_commands.errors.BadArgument):
        #     await interaction.response.send_message("❌ Vous n'avez pas renseigné un argument correct !", ephemeral=True)
        elif isinstance(error, discord.app_commands.errors.CommandInvokeError):
            await interaction.response.send_message("❌ Une erreur est survenue lors de l'envoi du message !", ephemeral=True)
        elif isinstance(error, discord.app_commands.errors.CommandNotFound):
            await interaction.response.send_message("❌ Cette commande n'existe pas !", ephemeral=True)
        elif isinstance(error, discord.app_commands.errors.CheckFailure) or isinstance(error, discord.app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ Vous n'avez pas les permissions nécessaires pour effectuer cette action !", ephemeral=True)
        else: raise error
'''
# Message de bienvenue


@client.event
async def on_member_join(member):
    channel = member.guild.system_channel
    embed = discord.Embed(title="👋 WELCOME !",
                          description=f"🇫🇷 Bienvenue <@{member.id}> ! "
                                      f"Nous espérons que vous serez satisfait par nos services.\n"
                                      f"Pour tout comprendre sur notre système de commande, "
                                      f"rendez-vous ici : <#1061021846146912347>. \n\n"
                                      f"🇬🇧🇺🇸 Welcome <@{member.id}> ! We hope you will be satisfied by our services.\n"
                                      f"To understand our order system, go here : <#1061021846146912347>.",
                          color=discord.Colour.blue())
    embed.set_thumbnail(url=f"{member.display_avatar}")

    message = await channel.send(embed=embed)
    await message.add_reaction("👋")


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


# Minuit en France (UTC+1)
@tasks.loop(time=datetime.time(hour=23, minute=0, second=0))
async def sendDbBackup():
    fichier = "resources/database.db"
    channel = client.get_channel(1068629536700366959)
    print("Envoi de la base de données...")
    date = datetime.datetime.now()
    date = date.astimezone(tz=timezone('Europe/Paris'))
    date = date.strftime("%d/%m/%Y à %H:%M:%S")
    await channel.send("Database du " + date + "\n Taille : " + str(
        os.path.getsize(fichier)) + " octets", file=discord.File(fichier))


if __name__ == '__main__':
    token = config.get_token()
    if token is None or token == "":
        print("❌ Le token n'est pas valide ! Veuillez le renseigner dans le fichier config.json.")
    else:
        client.run(token)
