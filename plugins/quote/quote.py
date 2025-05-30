import asyncio
import json
import os
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# 🚀 Target channel where quotes will be auto-sent
TARGET_CHANNEL_ID = -1002673901150  # ✅ Replace with your actual channel ID

# 📂 Directory containing quote JSON files (motivation.json, inspiration.json, etc.)
DATA_DIR = os.path.join(os.path.dirname(__file__), "quotes")

# 🧠 Dynamically list all categories based on files in the directory
def get_all_categories():
    return [
        os.path.splitext(file)[0]
        for file in os.listdir(DATA_DIR)
        if file.endswith(".json")
    ]

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
        return f"⚠️ Error reading quote file: {e}"

# 🔁 Auto send random quote every 5 minutes to the target channel
async def auto_quote_sender(app: Client):
    await asyncio.sleep(10)  # Give bot time to fully start
    while True:
        try:
            categories = get_all_categories()
            valid = [cat for cat in categories if os.path.exists(os.path.join(DATA_DIR, f"{cat}.json"))]
            if not valid:
                print("❌ No valid quote categories found.")
                await asyncio.sleep(300)
                continue

            category = random.choice(valid)
            quote = get_random_quote(category)
            if "⚠️" not in quote:
                await app.send_message(
                    chat_id=TARGET_CHANNEL_ID,
                    text=f"📝 Quote of the Moment\n\n{quote}"
                )
                print(f"[✅] Sent quote from '{category}'")
        except Exception as e:
            print(f"[❌ Auto Quote Error] {e}")
        await asyncio.sleep(300)  # Every 5 minutes

# 🔘 /quote command - Show buttons for available categories
@Client.on_message(filters.command("quote") & filters.private)
async def quote_menu(_, message: Message):
    categories = get_all_categories()
    if not categories:
        await message.reply_text("⚠️ No quote categories found.")
        return

    buttons = [
        [InlineKeyboardButton(f"📌 {cat.capitalize()}", callback_data=f"quote_{cat}")]
        for cat in categories
    ]
    await message.reply_text(
        "🧠 *Choose a category to get a quote:*",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# 🎯 Handle quote button callback
@Client.on_callback_query(filters.regex("^quote_"))
async def send_category_quote(_, callback_query: CallbackQuery):
    category = callback_query.data.split("_", 1)[1]
    quote = get_random_quote(category)
    await callback_query.message.reply_text(text=quote)
    await callback_query.answer()
