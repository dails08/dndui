import json
import os

CONFIG_FILE = "config.json"
DEFAULT_MEDIA_ROOT_DIR = r"C:\Users\Christopher\Dropbox\CoS\COS2\working assets\visual assets\bg"
DEFAULT_NPC_ROOT_DIR = r"C:\Users\Christopher\Dropbox\CoS\COS2\working assets\visual assets\npc"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as config_file:
            return json.load(config_file)
    return {}


def save_config(config):
    with open(CONFIG_FILE, "w") as config_file:
        json.dump(config, config_file)
