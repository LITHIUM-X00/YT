# config.py
import os

def get_env(name: str, default=None):
    val = os.getenv(name, default)
    if val is None:
        return None
    if isinstance(val, str):
        if val.lower() == "true":
            return True
        if val.lower() == "false":
            return False
        if val.isdigit() and name not in ["AUTHORIZED_USER", "OWNER"]:
            return int(val)
    return val

API_ID = get_env("API_ID")
API_HASH = get_env("API_HASH")
BOT_TOKEN = get_env("BOT_TOKEN")
OWNER = [int(i) for i in str(get_env("OWNER", "0")).split(",")]

ENABLE_FFMPEG = get_env("ENABLE_FFMPEG", True)
AUDIO_FORMAT = get_env("AUDIO_FORMAT", "mp3")
