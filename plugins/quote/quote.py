import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import config
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
ai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configuration
class Config:
    def __init__(self):
        self.target_channel_id = -1002673901150  # Default channel
        self.admins = [12345678]  # Your admin ID(s)
        self.load()
    
    def load(self):
        try:
            with open("config.json") as f:
                config = json.load(f)
                self.target_channel_id = config.get("target_channel_id", self.target_channel_id)
        except (FileNotFoundError, json.JSONDecodeError):
            self.save()
    
    def save(self):
        with open("config.json", "w") as f:
            json.dump({"target_channel_id": self.target_channel_id}, f)

config = Config()

# Paths
DATA_DIR = Path(__file__).parent / "quotes"
AI_QUOTES_CACHE = Path(__file__).parent / "ai_quotes_cache.json"

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

# AI Quote Generator (Fixed and improved)
async def generate_ai_quote(topic="inspiration"):
    try:
        # Create more specific prompt
        prompt = (
            f"Generate a short, powerful {topic} quote that would inspire someone. "
            "Make it 1 sentence maximum (under 15 words). "
            "Respond ONLY with the quote text itself without any additional commentary, "
            "quotation marks, or author attribution."
        )
        
        response = await ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a world-class quote generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=50
        )
        
        quote = response.choices[0].message.content.strip('"\'').strip()
        return quote if len(quote.split()) <= 15 else None
    
    except Exception as e:
        print(f"AI Generation Error: {str(e)}")
        return None

# Quote management
def get_all_categories():
    try:
        return [file.stem for file in DATA_DIR.glob("*.json") if file.is_file()]
    except Exception as e:
        print(f"Error getting categories: {e}")
        return []

def get_random_quote(category: str) -> str:
    file_path = DATA_DIR / f"{category}.json"
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            quotes = json.load(f)
        
        if not quotes or not isinstance(quotes, list):
            return None
            
        quote = random.choice(quotes)
        if isinstance(quote, dict):
            return quote.get("quote", str(quote))
        return str(quote)
    except Exception:
        return None

# Message formatting
def format_quote(quote: str, source: str = "Regular") -> str:
    emoji = get_random_emoji()
    border = "┉━" * 10
    return (
        f"✨ {source} Quote ✨\n\n"
        f"{border}\n"
        f"{emoji} {quote} {emoji}\n"
        f"{border}\n\n"
        f"#Motivation #Inspiration"
    )

# Auto quote sender
async def auto_quote_sender(app: Client):
    await asyncio.sleep(10)
    while True:
        try:
            # Try AI quote first (30% chance)
            if random.random() < 0.3:
                ai_topic = random.choice(["motivation", "success", "wisdom", "life"])
                quote = await generate_ai_quote(ai_topic)
                if quote:
                    await app.send_message(
                        chat_id=config.target_channel_id,
                        text=format_quote(quote, f"AI {ai_topic.title()}")
                    )
                    await asyncio.sleep(300)
                    continue
            
            # Fallback to regular quotes
            categories = get_all_categories()
            if not categories:
                await asyncio.sleep(300)
                continue

            category = random.choice(categories)
            quote = get_random_quote(category)
            if quote:
                await app.send_message(
                    chat_id=config.target_channel_id,
                    text=format_quote(quote, category.title())
                )
            
        except Exception as e:
            print(f"Auto-send Error: {str(e)}")
        
        await asyncio.sleep(300)  # 5 minutes

# Command handlers
@Client.on_message(filters.command("quote") & filters.private)
async def quote_menu(client: Client, message: Message):
    categories = get_all_categories()
    if not categories:
        await message.reply("⚠️ No quote categories available")
        return

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
async def send_category_quote(client: Client, callback: CallbackQuery):
    category = callback.data.split("_", 1)[1]
    quote = get_random_quote(category)
    if quote:
        await callback.message.reply_text(format_quote(quote, category.title()))
    else:
        await callback.message.reply_text("⚠️ Failed to get quote")
    await callback.answer()

@Client.on_callback_query(filters.regex(r"^ai_quote_menu$"))
async def ai_quote_menu(client: Client, callback: CallbackQuery):
    topics = ["motivation", "success", "wisdom", "life"]
    buttons = [
        [InlineKeyboardButton(f"{get_random_emoji()} {t.title()}", callback_data=f"ai_{t}")]
        for t in topics
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
    if quote:
        await callback.message.reply_text(format_quote(quote, f"AI {topic.title()}"))
    else:
        await callback.message.reply_text("⚠️ Failed to generate quote")
    await callback.answer()

@Client.on_message(filters.command("setchannel") & filters.private & filters.user(config.admins))
async def set_channel(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.forward_from_chat:
        config.target_channel_id = message.reply_to_message.forward_from_chat.id
        config.save()
        await message.reply(f"✅ Channel set to ID: {config.target_channel_id}")
    else:
        await message.reply("ℹ️ Reply to a forwarded channel message")

@Client.on_message(filters.command("testai") & filters.private)
async def test_ai(client: Client, message: Message):
    quote = await generate_ai_quote("motivation")
    if quote:
        await message.reply(f"✅ AI Test Successful:\n\n{format_quote(quote, 'AI Test')}")
    else:
        await message.reply("❌ AI Generation Failed")

# Main bot handler
async def main():
    async with Client(
        "my_bot",
        api_id=os.getenv("API_ID"),
        api_hash=os.getenv("API_HASH")
    ) as app:
        asyncio.create_task(auto_quote_sender(app))
        print("✅ Bot started successfully")
        await app.run()

if __name__ == "__main__":
    asyncio.run(main())
