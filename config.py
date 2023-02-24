"""
Ce fichier permet de récupérer des valeurs dans le fichier de configuration.
"""

# Imports
import os
import json

# Config
CONFIG_DIR = "resources"
CONFIG_FILE_NAME = "config.json"


def create_folder():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)


def create_file(file_name: str, json_default: dict = None):
    path = CONFIG_DIR + "/" + file_name
    if not os.path.exists(path):
        create_folder()
        with open(path, "w+", encoding="utf-8") as f:
            if json_default:
                to_write = json.dumps(json_default, indent=4)
                f.write(to_write)
    return path


def get_token():
    """
    Renvoie le token du bot
    """
    return get("TOKEN")

def get_dev_mode():
    """
    Renvoie le mode du bot
    """
    return get("DEV_MODE")

def get(field: str):
    """
    Permet de récupérer une valeur dans le fichier de configuration
    ---
    field: Valeur à récupérer
    """
    config_path = create_file(CONFIG_FILE_NAME, json_default={"TOKEN": ""})

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