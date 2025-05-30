import asyncio
import json
import os
import random
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# 🚀 Target channel where quotes will be auto-sent
TARGET_CHANNEL_ID = -1002673901150  # ✅ Replace with your actual channel ID

# 📂 Directory containing quote JSON files (motivation.json, inspiration.json, etc.)
DATA_DIR = Path(__file__).parent / "quotes"

# 🧠 Dynamically list all categories based on files in the directory
def get_all_categories():
    try:
        return [
            file.stem
            for file in DATA_DIR.glob("*.json")
            if file.is_file()
        ]
    except Exception as e:
        print(f"Error getting categories: {e}")
        return []

# 🔍 Load random quote from selected category
def get_random_quote(category: str) -> str:
    file_path = DATA_DIR / f"{category}.json"
    if not file_path.exists():
        return "⚠️ No quotes found for this category."
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            quotes = json.load(f)
        
        if not quotes or not isinstance(quotes, list):
            return "⚠️ No quotes available or invalid format."
            
        quote_data = random.choice(quotes)
        
        # Simplified to handle only the quote text
        if isinstance(quote_data, dict):
            return f"\"{quote_data.get('quote', str(quote_data))}\""
        return f"\"{str(quote_data)}\""
            
    except json.JSONDecodeError:
        return "⚠️ Invalid JSON format in quotes file."
    except Exception as e:
        return f"⚠️ Error reading quote file: {str(e)}"

# 🔁 Auto send random quote every 5 minutes to the target channel
async def auto_quote_sender(app: Client):
    await asyncio.sleep(10)  # Give bot time to fully start
    while True:
        try:
            categories = get_all_categories()
            if not categories:
                print("❌ No valid quote categories found.")
                await asyncio.sleep(30)
                continue

            category = random.choice(categories)
            quote = get_random_quote(category)
            if not quote.startswith("⚠️"):
                await app.send_message(
                    chat_id=TARGET_CHANNEL_ID,
                    text=f"📝 {category.capitalize()} Quote\n\n"
                    f"<blockquote>❁┉━┉━┉━┉┉━┉━┉━┉┉━┉━┉❁</blockquote>\n"
                    f"<b><blockquote>{quote}</blockquote></b>\n"
                    f"<blockquote>❁┉━┉━┉━┉┉━┉━┉━┉┉━┉━┉❁</blockquote>\n\n"
                    f"<blockquote><b>@II_LevelUP_II 🔥</b></blockquote>"
                )
                print(f"[✅] Sent quote from '{category}'")
        except Exception as e:
            print(f"[❌ Auto Quote Error] {str(e)}")
        await asyncio.sleep(30)  # Every 5 minutes

# 🔘 /quote command - Show buttons for available categories
@Client.on_message(filters.command("quote") & filters.private)
async def quote_menu(client: Client, message: Message):
    categories = get_all_categories()
    if not categories:
        await message.reply_text("⚠️ No quote categories found.")
        return

    buttons = [
        [InlineKeyboardButton(f"📌 {cat.capitalize()}", callback_data=f"quote_{cat}")]
        for cat in sorted(categories)
    ]
    
    await message.reply_text(
        "🧠 *Choose a category to get a quote:*",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# 🎯 Handle quote button callback
@Client.on_callback_query(filters.regex(r"^quote_"))
async def send_category_quote(client: Client, callback_query: CallbackQuery):
    category = callback_query.data.split("_", 1)[1]
    quote = get_random_quote(category)
    
    try:
        await callback_query.message.reply_text(quote)
    except Exception as e:
        await callback_query.message.reply_text(f"⚠️ Failed to send quote: {str(e)}")
    
    await callback_query.answer()
