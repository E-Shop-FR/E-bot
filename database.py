"""
Ce fichier permet la gestion de la base de données.
"""

# Imports
import os
import sqlite3
import discord
import datetime

# Database
con = sqlite3.connect("resources/database.db")
cur = con.cursor()

# Création des tables

cur.execute("""CREATE TABLE IF NOT EXISTS comptes(
            id_discord INTEGER PRIMARY KEY NOT NULL,
            pseudo TEXT NOT NULL,
            avatar TEXT NOT NULL
            )""")

cur.execute("""CREATE TABLE IF NOT EXISTS avis(
            id_commentaire INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
            id_client INTEGER NOT NULL,
            date_publication TEXT NOT NULL,
            pseudo_vendeur TEXT NOT NULL,
            commentaire TEXT NOT NULL, 
            note INTEGER NOT NULL,
            FOREIGN KEY(id_client) REFERENCES comptes(id_discord)
            )""")
con.commit()

# Méthodes SQL


def get_all_avis():
    """
    Renvoie les avis de tout le market
    """
    cur.execute("""SELECT comptes.pseudo, avis.pseudo_vendeur, avis.commentaire, avis.note FROM avis
                JOIN comptes ON avis.id_client = comptes.id_discord
                ORDER BY avis.note DESC
                """)
    return cur.fetchall()


<<<<<<< Updated upstream
def add_avis(user: discord.Member, pseudo_vendeur: int, commentaire: str, note: int):
    """
=======
def add_avis(user: discord.Member, pseudo_vendeur: str, commentaire: str, note: int):
    '''
>>>>>>> Stashed changes
    Ajoute un avis à la base de données
    ---
    member : Le membre qui a posté l'avis
    pseudo_vendeur: Pseudo du vendeur
    commentaire: Commentaire du client
    note: Note du client sur 5
    """
    pseudo_client = user.name
    id_client = user.id
    avatar_client = str(user.avatar)
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cur.execute("""INSERT OR REPLACE INTO comptes (id_discord, avatar, pseudo) VALUES (?, ?, ?)""",
                (id_client, pseudo_client, avatar_client))
    cur.execute("""INSERT INTO avis (id_client, date_publication, pseudo_vendeur, commentaire, note) VALUES (?, ?, ?, 
    ?, ?)""",
                (id_client, date, pseudo_vendeur, commentaire, note))
    con.commit()


def remove_avis(id_commentaire: int):
    """
    Supprime un avis de la base de données
    ---
    id_commentaire: ID du commentaire
    """
    cur.execute("""DELETE FROM avis WHERE id_commentaire = ?""",
                (id_commentaire,))
    con.commit()


def get_client_avis(id_client: int):
    """
    Renvoie les avis d'un client
    ---
    id_client: ID discord du client
    ---
    Renvoie une liste de tuples (pseudo_vendeur, note, commentaire, date de publication)
    """

    cur.execute("""SELECT avis.pseudo_vendeur, avis.note, avis.commentaire avis.date_publication FROM avis
                WHERE avis.id_client = ?
                ORDER BY avis.date_publication DESC""", (id_client, ))
    return cur.fetchall()


def get_vendeur_avis(pseudo_vendeur: str):
    """
    Renvoie les avis sur vendeur
    ---
    pseudo_vendeur: Pseudo du vendeur
    ---
    Renvoie une liste de tuples (pseudo_client, note, commentaire, date de publication)
    """
    cur.execute("""SELECT comptes.pseudo, avis.note, avis.commentaire, avis.date_publication FROM avis
                JOIN comptes ON avis.id_client = comptes.id_discord
                WHERE avis.pseudo_vendeur = ?
                ORDER BY avis.note DESC""", (pseudo_vendeur, ))
    return cur.fetchall()


def get_vendeur_moyenne(pseudo_vendeur: str):
    """
    Renvoie la note moyenne d'un vendeur
    ---
    pseudo_vendeur: Pseudo du vendeur
    ---
    Renvoie un float
    """
    cur.execute("""SELECT AVG(avis.note) FROM avis
                WHERE avis.pseudo_vendeur = ?""", (pseudo_vendeur, ))
    return cur.fetchone()[0]


def get_vendeur_nb_avis(pseudo_vendeur: str):
    """
    Renvoie le nombre d'avis d'un vendeur
    ---
    pseudo_vendeur: Pseudo du vendeur
    ---
    Renvoie un int
    """
    cur.execute("""SELECT COUNT(avis.note) FROM avis
                WHERE avis.pseudo_vendeur = ?""", (pseudo_vendeur, ))
    return cur.fetchone()[0]
