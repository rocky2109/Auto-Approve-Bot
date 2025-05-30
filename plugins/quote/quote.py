import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Constants
TARGET_CHANNEL_ID = -1002673901150  # Replace with your channel ID
DATA_DIR = Path(__file__).parent / "quotes"
AI_QUOTES_CACHE = Path(__file__).parent / "ai_quotes_cache.json"

# Emoji generator (your existing function)
def get_random_emoji():
    emoji_categories = {
        'stars': ['✨', '🌟', '⭐', '💫', '☄️', '🌠'],
        'fire': ['🔥', '🎇', '🎆', '🧨', '💥'],
        # ... (keep your existing emoji categories)
    }
    all_emojis = [emoji for category in emoji_categories.values() for emoji in category]
    return ''.join(random.choices(all_emojis, k=random.randint(1, 2)))

# Cache management for AI quotes
def load_ai_cache():
    try:
        with open(AI_QUOTES_CACHE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_ai_cache(cache):
    with open(AI_QUOTES_CACHE, "w") as f:
        json.dump(cache, f, indent=2)

# AI Quote Generator
async def generate_ai_quote(topic="inspiration"):
    cache = load_ai_cache()
    
    # Check cache first
    if topic in cache:
        cached_data = cache[topic]
        generated_at = datetime.fromisoformat(cached_data["generated_at"])
        if datetime.now() - generated_at < timedelta(days=7):
            return cached_data["quote"]
    
    # Call OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You're a world-class quote generator. Respond ONLY with the quote in 1-2 sentences."},
                {"role": "user", "content": f"Generate a {topic} quote that would go viral on social media"}
            ],
            temperature=0.7,
            max_tokens=60
        )
        
        quote = response.choices[0].message.content.strip('"')
        
        # Update cache
        cache[topic] = {
            "quote": quote,
            "generated_at": datetime.now().isoformat()
        }
        save_ai_cache(cache)
        
        return quote
    except Exception as e:
        print(f"AI Quote Generation Error: {str(e)}")
        return None

# Existing quote functions
def get_all_categories():
    try:
        return [file.stem for file in DATA_DIR.glob("*.json") if file.is_file()]
    except Exception as e:
        print(f"Error getting categories: {e}")
        return []

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
        
        if isinstance(quote_data, dict):
            return f"\"{quote_data.get('quote', str(quote_data))}\""
        return f"\"{str(quote_data)}\""
            
    except json.JSONDecodeError:
        return "⚠️ Invalid JSON format in quotes file."
    except Exception as e:
        return f"⚠️ Error reading quote file: {str(e)}"

# Auto quote sender (now with AI quotes)
async def auto_quote_sender(app: Client):
    await asyncio.sleep(10)
    while True:
        try:
            # 30% chance for AI quote
            if random.random() < 0.3:
                ai_topic = random.choice(["motivation", "success", "wisdom", "life"])
                quote = await generate_ai_quote(ai_topic)
                if quote:
                    await app.send_message(
                        chat_id=TARGET_CHANNEL_ID,
                        text=(
                            f"🤖 *AI-Generated {ai_topic.title()} Quote:*\n\n"
                            f"<blockquote>{get_random_emoji()} {quote} {get_random_emoji()}</blockquote>\n\n"
                            f"#{ai_topic} #AIWisdom"
                        )
                    )
                    await asyncio.sleep(300)
                    continue
            
            # Original quote system
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
                    text=(
                        f"❝ <b>{category.capitalize()} Quote ❞</b>\n\n"
                        f"<blockquote>❁┉━┉━┉━┉┉━┉━┉━┉┉━┉━┉❁</blockquote>\n"
                        f"<b><blockquote>{get_random_emoji()} {quote} {get_random_emoji()}</blockquote></b>\n"
                        f"<blockquote>❁┉━┉━┉━┉┉━┉━┉━┉┉━┉━┉❁</blockquote>\n\n"
                        f"<blockquote><b>@II_LevelUP_II {get_random_emoji()}</b></blockquote>"
                    )
                )
        except Exception as e:
            print(f"[❌ Auto Quote Error] {str(e)}")
        await asyncio.sleep(300)  # 5 minutes

# Command handlers
@Client.on_message(filters.command("quote") & filters.private)
async def quote_menu(client: Client, message: Message):
    categories = get_all_categories()
    if not categories:
        await message.reply_text("⚠️ No quote categories found.")
        return

    buttons = [
        [InlineKeyboardButton(f"📌 {cat.capitalize()}", callback_data=f"quote_{cat}"),
        [InlineKeyboardButton("🤖 AI Quote", callback_data="ai_quote_menu")]
    ]
    
    await message.reply_text(
        "🧠 *Choose a category to get a quote:*",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex(r"^quote_"))
async def send_category_quote(client: Client, callback_query: CallbackQuery):
    category = callback_query.data.split("_", 1)[1]
    quote = get_random_quote(category)
    await callback_query.message.reply_text(quote)
    await callback_query.answer()

@Client.on_callback_query(filters.regex(r"^ai_quote_menu$"))
async def ai_quote_menu(client: Client, callback_query: CallbackQuery):
    buttons = [
        [InlineKeyboardButton(f"{get_random_emoji()} Motivation", callback_data="ai_quote_motivation")],
        [InlineKeyboardButton(f"{get_random_emoji()} Success", callback_data="ai_quote_success")],
        [InlineKeyboardButton(f"{get_random_emoji()} Wisdom", callback_data="ai_quote_wisdom")],
        [InlineKeyboardButton(f"{get_random_emoji()} Life", callback_data="ai_quote_life")]
    ]
    await callback_query.message.edit_text(
        "✨ *Choose an AI Quote Topic:*",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await callback_query.answer()

@Client.on_callback_query(filters.regex(r"^ai_quote_"))
async def send_ai_quote(client: Client, callback_query: CallbackQuery):
    topic = callback_query.data.split("_", 2)[2]
    quote = await generate_ai_quote(topic)
    
    if quote:
        await callback_query.message.reply_text(
            f"✨ *AI-Generated {topic.title()} Quote:*\n\n"
            f"_{quote}_\n\n"
            f"{get_random_emoji()} #{topic} #AIWisdom"
        )
    else:
        await callback_query.message.reply_text("⚠️ Failed to generate quote. Please try again later.")
    
    await callback_query.answer()

@Client.on_message(filters.command("aiquote") & (filters.private | filters.chat(TARGET_CHANNEL_ID)))
async def ai_quote_command(client: Client, message: Message):
    topic = " ".join(message.command[1:]) if len(message.command) > 1 else "inspiration"
    quote = await generate_ai_quote(topic)
    
    if quote:
        await message.reply_text(
            f"✨ *AI-Generated {topic.title()} Quote:*\n\n"
            f"_{quote}_\n\n"
            f"{get_random_emoji()} #{topic.replace(' ', '')} #AIWisdom"
        )
    else:
        await message.reply_text("⚠️ Failed to generate quote. Please try again later.")
