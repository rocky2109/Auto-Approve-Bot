import asyncio
import json
import os
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# 🚀 Target channel where quotes will be auto-sent
TARGET_CHANNEL_ID = -1002673901150  # Replace with your channel ID

# 📂 Directory containing quote JSON files
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# 🗂 Available quote categories (JSON filenames without extension)
CATEGORIES = ["motivation", "inspiration", "funny"]

# 🔁 Auto send quote to target channel every 5 minutes
async def auto_quote_sender(app: Client):
    await asyncio.sleep(10)  # delay on startup
    while True:
        try:
            category = random.choice(CATEGORIES)
            quote = get_random_quote(category)
            if quote:
                await app.send_message(
                    chat_id=TARGET_CHANNEL_ID,
                    text=f"📝 Quote of the Moment\n\n{quote}"
                )
        except Exception as e:
            print(f"[Auto Quote Error] {e}")
        await asyncio.sleep(300)  # 5 minutes

# 🔍 Load random quote from selected category
def get_random_quote(category: str) -> str:
    file_path = os.path.join(DATA_DIR, f"{category}.json")
    if not os.path.exists(file_path):
        return "⚠️ No quotes found for this category."
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            quotes = json.load(f)
        if not quotes:
            return "⚠️ No quotes available."
        quote_data = random.choice(quotes)
        return f"“{quote_data['quote']}”\n\n— {quote_data['author']}"
    except Exception as e:
        return f"Error reading quote: {e}"

# 🔘 Handle /quote command in PM
@Client.on_message(filters.command("quote") & filters.private)
async def quote_menu(_, message: Message):
    buttons = [
        [InlineKeyboardButton("🔥 Motivation", callback_data="quote_motivation")],
        [InlineKeyboardButton("💡 Inspiration", callback_data="quote_inspiration")],
        [InlineKeyboardButton("😂 Funny", callback_data="quote_funny")]
    ]
    await message.reply_text(
        "🧠 *Choose a category to get a quote:*",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# 🎯 Handle button callback to send category quote
@Client.on_callback_query(filters.regex("^quote_"))
async def send_category_quote(_, callback_query: CallbackQuery):
    category = callback_query.data.split("_")[1]
    quote = get_random_quote(category)
    await callback_query.message.reply_text(
        text=quote
    )
    await callback_query.answer()
