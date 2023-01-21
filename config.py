"""
Ce fichier permet de récupérer des valeurs dans le fichier de configuration.
"""

# Imports
import os
import json

# Config
CONFIG_DIR = "resources"
CONFIG_PATH = CONFIG_DIR + "/config.json"


def get_token():
    """
    Renvoie le token du bot
    """
    return get("TOKEN")


def get(field: str):
    """
    Permet de récupérer une valeur dans le fichier de configuration
    ---
    field: Valeur à récupérer
    """
    if not os.path.exists(CONFIG_PATH):
        # Si le fichier de configuration n'existe pas, on le crée
        os.makedirs(CONFIG_PATH, exist_ok=True)
        open(CONFIG_PATH, "x", encoding="utf-8")
        return ""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        # On lit le fichier de configuration
        fields = field.split(".")
        value = f.read()
        for field_name in fields:
            if isinstance(value, str):
                try:
                    data = json.loads(value)
                except json.JSONDecodeError:
                    return ""
            elif isinstance(value, dict):
                data = value
            else:
                return ""

            value = get_in_dict(data, field_name)
            if value is None:
                return ""
        return value


def get_in_dict(data: dict, field: str):
    """
    Permet de récupérer une valeur dans un dictionnaire
    ---
    data: Dictionnaire
    field: Valeur à récupérer
    """
    if field in data:
        return data[field]
    if field.upper() in data:
        return data[field.upper()]
    if field.lower() in data:
        return data[field.lower()]
