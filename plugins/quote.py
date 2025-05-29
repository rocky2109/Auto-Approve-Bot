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

# 🔒 Set your quote posting target channel here (make sure it's correct)
TARGET_CHANNEL_ID = -1002673901150  # Replace this with your actual channel ID

# ✅ Auto send random quote every 5 minutes
async def auto_quote_sender(app: Client):
    await asyncio.sleep(10)  # Wait a bit for startup
    while True:
        try:
            quote = random.choice(QUOTES)
            await app.send_message(
                chat_id=TARGET_CHANNEL_ID,
                text=f"📝 Quote of the Moment\n\n{quote}"
            )
        except Exception as e:
            print(f"[Quote Error] {e}")
        await asyncio.sleep(300)  # 5 minutes = 300 seconds

# 🔘 /quote command handler (only when /quote is used)
@Client.on_message(filters.command("quote") & (filters.private | filters.group | filters.channel))
async def send_quote(_, message: Message):
    quote = random.choice(QUOTES)
    await message.reply_text(
        f"📝 Your Quote\n\n{quote}",
        disable_web_page_preview=True
    )
