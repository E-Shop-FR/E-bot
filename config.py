import json
import os
from json import JSONDecodeError

config_dir = "resources"
config_path = config_dir + "/config.json"


def get_token():
    return get("TOKEN")


def get(field: str):
    if not os.path.exists(config_path):
        os.makedirs(config_dir, exist_ok=True)
        open(config_path, "x")
        return ""
    with open(config_path, "r") as f:
        # data = json.load(f)
        fields = field.split(".")
        value = f.read()
        for field_name in fields:
            if type(value) == str:
                try:
                    data = json.loads(value)
                except JSONDecodeError:
                    return ""
            elif type(value) == dict:
                data = value
            else:
                return ""

            value = get_in_dict(data, field_name)
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
