import os
import sqlite3
import warnings
import asyncio
from pyrogram import Client
from aiohttp import web

from config import API_ID, API_HASH, BOT_TOKEN
from plugins.quote.quote import auto_quote_sender  # ✅ Import properly


warnings.filterwarnings("ignore", message=".*message.forward_date.*")

# Initialize SQLite DB
conn = sqlite3.connect("bot_data.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS channels (
    chat_id INTEGER PRIMARY KEY,
    title TEXT
)
""")
conn.commit()

# Define aiohttp route for health check
r = web.RouteTableDef()

@r.get("/", allow_head=True)
async def root_route_handler(request):
    return web.Response(text='<h3 align="center"><b>I am Alive</b></h3>', content_type='text/html')

async def wsrvr():
    wa = web.Application(client_max_size=30000000)
    wa.add_routes(r)
    return wa

# Main Bot Class
class Bot(Client):
    def __init__(self):
        super().__init__(
            "auto_approve_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins"),
            workers=50,
            sleep_threshold=10
        )

    async def start(self):
        # Start aiohttp web server
        app = web.AppRunner(await wsrvr())
        await app.setup()
        ba = "0.0.0.0"
        port = int(os.environ.get("PORT", 8080)) or 8080
        await web.TCPSite(app, ba, port).start()
        
        # Start Pyrogram Client
        await super().start()
        me = await self.get_me()
        self.username = '@' + me.username

        # ✅ Start auto quote task in background
        asyncio.create_task(auto_quote_sender(self))

        print(f'Bot Started as {self.username} 🚀')

    async def stop(self, *args):
        await super().stop()
        print('Bot Stopped. Bye 👋')

# Run the bot
Bot().run()
