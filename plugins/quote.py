import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message

# Your target channel ID or @username for auto-posting quotes
TARGET_CHANNEL = "-1002673901150"  # e.g. "@MyChannel" or -1001234567890

# List of cool quotes 😎
QUOTES = [
    "💡 <b>“Success is not final, failure is not fatal: It is the courage to continue that counts.”</b>\n— Winston Churchill",
    "🚀 <b>“Don’t watch the clock; do what it does. Keep going.”</b>\n— Sam Levenson",
    "🔥 <b>“The way to get started is to quit talking and begin doing.”</b>\n— Walt Disney",
    "🌟 <b>“Push yourself, because no one else is going to do it for you.”</b>",
    "🎯 <b>“You don’t need to see the whole staircase, just take the first step.”</b>\n— Martin Luther King Jr.",
    "💎 <b>“Dream it. Wish it. Do it.”</b>",
    "🏆 <b>“Great things never come from comfort zones.”</b>",
    "🧠 <b>“Believe you can and you’re halfway there.”</b>\n— Theodore Roosevelt"
]

# Quote command: works in PM, groups, channels
@Client.on_message(filters.command("quote") & filters.private | filters.group | filters.channel)
async def send_quote(client: Client, message: Message):
    quote = random.choice(QUOTES)
    await message.reply_text(
        text=quote,       
        disable_web_page_preview=True
    )

# Auto sender task
async def auto_quote_sender(app: Client):
    await app.wait_until_ready()
    while True:
        try:
            quote = random.choice(QUOTES)
            await app.send_message(
                chat_id=TARGET_CHANNEL,
                text=quote,
                disable_web_page_preview=True
            )
        except Exception as e:
            print(f"[Auto Quote Error] {e}")
        await asyncio.sleep(300)  # 5 minutes
