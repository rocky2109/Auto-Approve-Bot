import os
import json
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Path to quotes folder (relative to this file's location)
CURRENT_DIR = os.path.dirname(__file__)
QUOTES_DIR = os.path.join(CURRENT_DIR, "quotes")

# Load all categories from JSON files
def load_all_quotes():
    quotes_by_cat = {}
    for filename in os.listdir(QUOTES_DIR):
        if filename.endswith(".json"):
            category = filename.replace(".json", "")
            with open(os.path.join(QUOTES_DIR, filename), "r", encoding="utf-8") as f:
                data = json.load(f)
                quotes_by_cat[category] = data.get("quotes", [])
    return quotes_by_cat

QUOTES_BY_CATEGORY = load_all_quotes()

# /quote command: show category buttons (PM only)
@Client.on_message(filters.command("quote") & filters.private)
async def quote_menu(_, message: Message):
    if not QUOTES_BY_CATEGORY:
        await message.reply_text("⚠️ No quote categories found.")
        return

    buttons = [
        [InlineKeyboardButton(category.capitalize(), callback_data=f"quote_{category}")]
        for category in QUOTES_BY_CATEGORY
    ]

    await message.reply_text(
        "📚 Choose a quote category:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Callback handler: send random quote from selected category
@Client.on_callback_query(filters.regex(r"^quote_"))
async def send_quote_callback(_, callback_query: CallbackQuery):
    category = callback_query.data.split("_", 1)[1]
    quotes = QUOTES_BY_CATEGORY.get(category)

    if not quotes:
        await callback_query.answer("⚠️ No quotes available in this category.", show_alert=True)
        return

    quote = random.choice(quotes)
    await callback_query.message.reply_text(f"📝 {category.capitalize()} Quote:\n\n{quote}")
    await callback_query.answer()
