import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message

# 🔁 List of Cool Quotes
QUOTES = [
    "✨ Great things never come from comfort zones.",
    "🔥 Push yourself, because no one else is going to do it for you.",
    "🚀 Don't stop until you're proud.",
    "💡 Success is what happens after you survive all your mistakes.",
    "🌟 Believe in yourself and magic will happen.",
    "🎯 The harder you work for something, the greater you’ll feel when you achieve it.",
    "🌈 Stay positive, work hard, and make it happen!",
    "🧠 Think big. Trust yourself. Make it happen.",
    "💪 Discipline is doing what needs to be done, even if you don’t want to.",
    "⏳ The pain you feel today will be the strength you feel tomorrow."
]

# 🔒 Your target channel ID (replace with your real one)
TARGET_CHANNEL_ID = -1002673901150

# ✅ Quote auto-sender (every 5 minutes)
async def auto_quote_sender(app: Client):
    await asyncio.sleep(10)  # Allow bot to fully start
    while True:
        try:
            quote = random.choice(QUOTES)
            await app.send_message(
                chat_id=TARGET_CHANNEL_ID,
                text=f"📝 Quote of the Moment\n\n{quote}"
            )
        except Exception as e:
            print(f"[Quote Error] {e}")
        await asyncio.sleep(300)  # 5 minutes
        

# 🔘 Handle /quote only in private chat (bot PM only)
@Client.on_message(filters.command("quote") & filters.private)
async def send_quote_pm(client: Client, message: Message):
    quote = random.choice(QUOTES)
    await message.reply_text(
        f"📝 Your Quote\n\n{quote}",
        disable_web_page_preview=True
    )
