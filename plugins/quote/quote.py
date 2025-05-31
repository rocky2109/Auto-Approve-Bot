import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
ai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Constants
TARGET_CHANNEL_ID = -1002673901150  # Replace with your channel ID
DATA_DIR = Path(__file__).parent / "quotes"
AI_QUOTES_CACHE = Path(__file__).parent / "ai_quotes_cache.json"
ADMINS = [12345678]  # Replace with your admin ID(s)

# Emoji generator
def get_random_emoji():
    emoji_categories = {
        'stars': ['✨', '🌟', '⭐', '💫', '☄️', '🌠'],
        'fire': ['🔥', '🎇', '🎆', '🧨', '💥'],
        'hands': ['👏', '🙌', '👍', '✊', '🤝', '🫶'],
        'symbols': ['💯', '⚡', '🔄', '♻️', '✅', '✔️'],
        'nature': ['🌱', '🌲', '🌞', '🌈', '🌊'],
        'objects': ['🏆', '🎯', '⏳', '⌛', '🔑', '💎'],
        'faces': ['😤', '🤩', '😎', '🤯', '🫡']
    }
    all_emojis = [emoji for category in emoji_categories.values() for emoji in category]
    return random.choice(all_emojis)

# Cache management
def load_ai_cache():
    try:
        with open(AI_QUOTES_CACHE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_ai_cache(cache):
    with open(AI_QUOTES_CACHE, "w") as f:
        json.dump(cache, f, indent=2)

# AI Quote Generator (Fixed)
async def generate_ai_quote(topic="inspiration"):
    cache = load_ai_cache()
    
    # Check cache first
    if topic in cache:
        cached_data = cache[topic]
        if datetime.now() - datetime.fromisoformat(cached_data["generated_at"]) < timedelta(hours=6):
            return cached_data["quote"]
    
    try:
        response = await ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "Generate concise, viral-style quotes. Respond ONLY with the quote text."
                },
                {
                    "role": "user",
                    "content": f"Create a {topic} quote under 15 words"
                }
            ],
            temperature=0.8,
            max_tokens=50
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
        print(f"AI Generation Error: {str(e)}")
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
            
        return f"\"{random.choice(quotes)}\""
            
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# Auto quote sender with AI integration
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
                            f"🤖 *AI {ai_topic.title()} Quote:*\n\n"
                            f"{get_random_emoji()} {quote} {get_random_emoji()}\n\n"
                            f"#{ai_topic} #AI"
                        )
                    )
                    await asyncio.sleep(300)
                    continue
            
            # Fallback to regular quotes
            categories = get_all_categories()
            if not categories:
                print("❌ No quote categories found")
                await asyncio.sleep(300)
                continue

            quote = get_random_quote(random.choice(categories))
            if not quote.startswith("⚠️"):
                await app.send_message(
                    chat_id=TARGET_CHANNEL_ID,
                    text=(
                        f"📌 *Quote of the Day*\n\n"
                        f"{get_random_emoji()} {quote} {get_random_emoji()}\n\n"
                        f"@YourChannelHandle"
                    )
                )
        except Exception as e:
            print(f"Auto-send Error: {str(e)}")
        await asyncio.sleep(300)  # 5 minutes

# Command handlers
@Client.on_message(filters.command("quote") & filters.private)
async def quote_menu(client: Client, message: Message):
    categories = get_all_categories()
    buttons = [
        [InlineKeyboardButton(f"{get_random_emoji()} {cat.title()}", callback_data=f"quote_{cat}")]
        for cat in categories
    ]
    buttons.append([InlineKeyboardButton("✨ AI Quote", callback_data="ai_quote_menu")])
    
    await message.reply_text(
        "📚 Choose quote type:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex(r"^quote_"))
async def send_quote(client: Client, callback: CallbackQuery):
    category = callback.data.split("_", 1)[1]
    quote = get_random_quote(category)
    await callback.message.reply_text(f"{get_random_emoji()} {quote}")
    await callback.answer()

@Client.on_callback_query(filters.regex(r"^ai_quote_menu$"))
async def ai_quote_menu(client: Client, callback: CallbackQuery):
    topics = ["motivation", "success", "wisdom", "life"]
    buttons = [
        [InlineKeyboardButton(f"{get_random_emoji()} {topic.title()}", callback_data=f"ai_{topic}")]
        for topic in topics
    ]
    await callback.message.edit_text(
        "🤖 Choose AI quote topic:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await callback.answer()

@Client.on_callback_query(filters.regex(r"^ai_"))
async def send_ai_quote(client: Client, callback: CallbackQuery):
    topic = callback.data.split("_", 1)[1]
    quote = await generate_ai_quote(topic)
    await callback.message.reply_text(
        f"✨ AI {topic.title()} Quote:\n\n{quote}\n\n#{topic}" if quote 
        else "⚠️ Failed to generate quote"
    )
    await callback.answer()

# Admin commands
@Client.on_message(filters.command("setchannel") & filters.private & filters.user(ADMINS))
async def set_channel(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.forward_from_chat:
        new_id = message.reply_to_message.forward_from_chat.id
        TARGET_CHANNEL_ID = new_id  # In production, save to config/db
        await message.reply(f"✅ Channel set to ID: {new_id}")
    else:
        await message.reply("ℹ️ Reply to a forwarded channel message")

# Start the bot
async def main():
    async with Client("my_bot") as app:
        await asyncio.gather(
            auto_quote_sender(app),
            app.run()
        )

if __name__ == "__main__":
    asyncio.run(main())
