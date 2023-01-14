import json
import os

config_path = "resources/config.json"


def get_token():
    return get("TOKEN")


def get(field: str):
    if not os.path.exists(config_path):
        open(config_path, "x")
        return ""
    with open(config_path, "r") as f:
        json_data = json.load(f)
        fields = field.split(".")
        value = json_data
        for field_name in fields:
            if type(value) != dict:
                return ""
            value = get_in_dict(json_data, field_name)
            if value is None:
                return ""
        return value


def get_in_dict(data: dict, field: str):
    if field in data:
        return data[field]
    if field.upper() in data:
        return data[field.upper()]
    if field.lower() in data:
        return data[field.lower()]
