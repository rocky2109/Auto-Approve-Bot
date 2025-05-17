from os import environ
from typing import List

API_ID = int(environ.get("API_ID", ""))
API_HASH = environ.get("API_HASH", "")
BOT_TOKEN = environ.get("BOT_TOKEN", "")
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", ""))
ADMINS = int(environ.get("ADMINS", ""))
DB_URI = environ.get("DB_URI", "")
DB_NAME = environ.get("DB_NAME", "autoacceptbot")
NEW_REQ_MODE = bool(environ.get('NEW_REQ_MODE', True))
IS_FSUB = bool(environ.get("FSUB", True)) # Set "True" For Enable Force Subscribe
AUTH_CHANNELS = list(map(int, environ.get("AUTH_CHANNEL", "").split())) # Add Multiple channel id
