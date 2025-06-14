from os import environ
from typing import List

# Existing config (keep all your current variables)
API_ID = int(environ.get("API_ID", ""))
API_HASH = environ.get("API_HASH", "")
BOT_TOKEN = environ.get("BOT_TOKEN", "")
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", ""))
ADMINS = int(environ.get("ADMINS", ""))
DB_URI = environ.get("DB_URI", "")
DB_NAME = environ.get("DB_NAME", "autoacceptbot")
NEW_REQ_MODE = bool(environ.get('NEW_REQ_MODE', True))
IS_FSUB = bool(environ.get("FSUB", True))
AUTH_CHANNELS = list(map(int, environ.get("AUTH_CHANNEL", "").split()))
NEWS_CHANNEL = -1002673901150  # or "@YourChannelUsername"

# New OpenAI config
OPENAI_API_KEY = environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_MAX_TOKENS = int(environ.get("OPENAI_MAX_TOKENS", 60))
OPENAI_TEMPERATURE = float(environ.get("OPENAI_TEMPERATURE", 0.7))

# Initialize OpenAI
import openai
openai.api_key = OPENAI_API_KEY
