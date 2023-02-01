'''
Ce fichier permet la gestion de la base de données.
'''

# Imports
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
            avatar TEXT NOT NULL,
            points_fidelite INTEGER NOT NULL DEFAULT 0
            )""")

cur.execute("""CREATE TABLE IF NOT EXISTS avis(
            id_avis INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
            id_client INTEGER NOT NULL,
            date_publication TEXT NOT NULL,
            type_commande TEXT NOT NULL,
            commentaire TEXT NOT NULL, 
            note INTEGER NOT NULL,
            FOREIGN KEY(id_client) REFERENCES comptes(id_discord)
            )""")
con.commit()

# Méthodes SQL
def get_all_avis():
    '''
    Renvoie les avis de tout le market
    '''
    cur.execute('''SELECT comptes.pseudo, avis.type_commande, avis.commentaire, avis.note FROM avis
                JOIN comptes ON avis.id_client = comptes.id_discord
                ORDER BY avis.note DESC
                ''')
    return cur.fetchall()


def add_avis(user: discord.Member, type_commande: str, commentaire: str, note: int):
    '''
    Ajoute un avis à la base de données
    ---
    member : Le membre qui a posté l'avis
    type_commande: Pseudo du vendeur
    commentaire: Commentaire du client
    note: Note du client sur 5
    '''
    pseudo_client = user.name
    id_client = user.id
    avatar_client = str(user.avatar)
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cur.execute('''INSERT OR REPLACE INTO comptes (id_discord, pseudo, avatar) VALUES (?, ?, ?)''',
                (id_client, pseudo_client, avatar_client))
    cur.execute('''INSERT INTO avis (id_client, date_publication, type_commande, commentaire, note) VALUES (?, ?, ?, 
    ?, ?)''',
                (id_client, date, type_commande, commentaire, note))
    con.commit()


def remove_avis(id_avis: int):
    '''
    Supprime un avis de la base de données
    ---
    id_avis: ID du commentaire
    '''
    cur.execute("""DELETE FROM avis WHERE id_avis = ?""",
                (id_avis,))
    con.commit()


def get_client_avis(client: discord.Member):
    '''
    Renvoie les avis d'un client
    ---
    id_client: ID discord du client
    ---
    Renvoie une liste de tuples (type_commande, note, commentaire, date de publication)
    '''
    id_client = client.id

    cur.execute('''SELECT avis.type_commande, avis.note, avis.commentaire avis.date_publication FROM avis
                WHERE avis.id_client = ?
                ORDER BY avis.date_publication DESC''', (id_client, ))
    return cur.fetchall()


def get_client_points(client: discord.Member):
    '''
    Renvoie les points de fidélité d'un client
    ---
    id_client: ID discord du client
    ---
    Renvoie un int
    '''
    id_client = client.id

    cur.execute("""SELECT comptes.points_fidelite FROM comptes
                WHERE comptes.id_discord = ?""", (id_client, ))
    return cur.fetchone()[0]


def add_client_points(client: discord.Member, points: int):
    '''
    Ajoute des points de fidélité à un client
    ---
    id_client: ID discord du client
    points: Nombre de points à ajouter
    '''
    id_client = client.id
    name = client.name
    avatar = str(client.avatar)

    cur.execute("""INSERT INTO comptes (id_discord, pseudo, avatar) VALUES (?, ?, ?)
                ON CONFLICT (id_discord) DO UPDATE SET points_fidelite = (points_fidelite + ?)""",
                (id_client, name, avatar, points))


def remove_client_points(client: discord.Member, points: int):
    '''
    Retire des points de fidélité à un client
    ---
    id_client: ID discord du client
    points: Nombre de points à retirer
    '''
    id_client = client.id
    name = client.name
    avatar = str(client.avatar)

    cur.execute("""INSERT INTO comptes (id_discord, pseudo, avatar) VALUES (?, ?, ?)
                ON CONFLICT (id_discord) DO UPDATE SET points_fidelite = (points_fidelite - ?)""",
                (id_client, name, avatar, points))
    con.commit()


def set_client_points(client: discord.Member, points: int):
    '''
    Définit les points de fidélité d'un client
    ---
    id_client: ID discord du client
    points: Nombre de points à définir
    '''
    id_client = client.id
    name = client.name
    avatar = str(client.avatar)

    cur.execute("""INSERT INTO comptes (id_discord, pseudo, avatar) VALUES (?, ?, ?)
                ON CONFLICT (id_discord) DO UPDATE SET points_fidelite = ?""",
                (id_client, name, avatar, points))
    con.commit()


def reset_client_points(client: discord.Member):
    '''
    Réinitialise les points de fidélité d'un client à 0
    id_client: ID discord du client
    '''
    id_client = client.id
    name = client.name
    avatar = str(client.avatar)

    cur.execute("""INSERT INTO comptes (id_discord, pseudo, avatar) VALUES (?, ?, ?)
                ON CONFLICT (id_discord) DO UPDATE SET points_fidelite = 0""",
                (id_client, name, avatar))
    con.commit()


def get_client_pseudo(client: discord.Member):
    '''
    Renvoie le pseudo d'un client
    ---
    id_client: ID discord du client
    ---
    Renvoie un str
    '''
    id_client = client.id

    cur.execute("""SELECT comptes.pseudo FROM comptes
                WHERE comptes.id_discord = ?""", (id_client, ))
    return cur.fetchone()[0]


def get_client_avatar(id_client: int):
    '''
    Renvoie l'avatar d'un client
    ---
    id_client: ID discord du client
    ---
    Renvoie un str
    '''
    cur.execute("""SELECT comptes.avatar FROM comptes
                WHERE comptes.id_discord = ?""", (id_client, ))
    return cur.fetchone()[0]


def get_client_id(pseudo: str):
    '''
    Renvoie l'ID d'un client
    ---
    pseudo: Pseudo du client
    ---
    Renvoie un int
    '''
    cur.execute("""SELECT comptes.id_discord FROM comptes
                WHERE comptes.pseudo = ?""", (pseudo, ))
    return cur.fetchone()[0]


def get_client_informations(id_client: int):
    '''
    Renvoie les informations d'un client
    ---
    id_client: ID discord du client
    ---
    Renvoie un tuple (pseudo, avatar, points de fidélité)
    '''
    cur.execute("""SELECT comptes.pseudo, comptes.avatar, comptes.points_fidelite FROM comptes
                WHERE comptes.id_discord = ?""", (id_client, ))
    return cur.fetchone()


def get_all_clients():
    '''
    Renvoie tous les clients
    ---
    Renvoie une liste de tuples (pseudo, avatar, points de fidélité)
    '''
    cur.execute(
        """SELECT comptes.pseudo, comptes.avatar, comptes.points_fidelite FROM comptes""")
    return cur.fetchall()


def get_points_ranking():
    '''
    Renvoie le classement des points de fidélité
    ---
    Renvoie une liste de tuples (pseudo, points de fidélité)
    '''
    cur.execute("""SELECT comptes.pseudo, comptes.points_fidelite FROM comptes
                ORDER BY comptes.points_fidelite DESC""")
    return cur.fetchall()

def get_user_infos(id_client: int):
    '''
    Renvoie les informations d'un client
    ---
    id_client: ID discord du client
    ---
    Renvoie un tuple (pseudo, avatar, points de fidélité)
    '''
    cur.execute("""SELECT comptes.pseudo, comptes.avatar, comptes.points_fidelite FROM comptes
                WHERE comptes.id_discord = ?""", (id_client, ))
    return cur.fetchone()

def get_user(pseudo: str):
    '''
    Renvoie les informations d'un client
    ---
    pseudo: Pseudo du client
    ---
    Renvoie un tuple (pseudo, avatar, points de fidélité)
    '''
    cur.execute("""SELECT comptes.pseudo, comptes.avatar, comptes.points_fidelite FROM comptes
                WHERE comptes.pseudo = ?""", (pseudo, ))
    return cur.fetchone()

def get_user(member: discord.Member):
    '''
    Renvoie les informations d'un client
    ---
    member: Membre du serveur
    ---
    Renvoie un tuple (pseudo, avatar, points de fidélité)
    '''
    client_id = member.id
    cur.execute("""SELECT comptes.pseudo, comptes.avatar, comptes.points_fidelite FROM comptes
                WHERE comptes.id_discord = ?""", (client_id, ))
    return cur.fetchone()

def user_exists(id_client: int):
    '''
    Vérifie si un client existe
    ---
    id_client: ID discord du client
    ---
    Renvoie un bool
    '''
    cur.execute("""SELECT comptes.id_discord FROM comptes
                WHERE comptes.id_discord = ?""", (id_client, ))
    return cur.fetchone() is not None

def user_exists(pseudo: str):
    '''
    Vérifie si un client existe
    ---
    pseudo: Pseudo du client
    ---
    Renvoie un bool
    '''
    cur.execute("""SELECT comptes.pseudo FROM comptes
                WHERE comptes.pseudo = ?""", (pseudo, ))
    return cur.fetchone() is not None

def user_exists(member: discord.Member):
    '''
    Vérifie si un client existe
    ---
    member: Membre du serveur
    ---
    Renvoie un bool
    '''
    client_id = member.id
    cur.execute("""SELECT comptes.id_discord FROM comptes
                WHERE comptes.id_discord = ?""", (client_id, ))
    return cur.fetchone() is not None

