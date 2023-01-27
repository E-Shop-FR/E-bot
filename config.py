"""
Ce fichier permet de récupérer des valeurs dans le fichier de configuration.
"""

import json
# Imports
import os

# Config
CONFIG_DIR = "resources"
CONFIG_FILE_NAME = "config.json"


def create_folder():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)


def create_file(file_name: str):
    path = CONFIG_DIR + "/" + file_name
    if not os.path.exists(path):
        create_folder()
        open(path, "x", encoding="utf-8")
    return path


def db_file_path():
    return create_file("database.db")


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
    config_path = create_file(CONFIG_FILE_NAME)
    with open(config_path, "r", encoding="utf-8") as f:
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
