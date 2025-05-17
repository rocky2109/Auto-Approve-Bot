import asyncio
import random
import logging
import datetime
import time
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from config import *
from .database import db
from pyrogram.types import Message
from .fsub import get_fsub
from threading import Thread    # Import all the command handlers from commands.py

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define NEW_REQ_MODE (configurable)
NEW_REQ_MODE = True  # Set to False to disable auto-approval

async def retry_with_backoff(retries, coroutine, *args, **kwargs):
    """Retry a coroutine with exponential backoff."""
    delay = 1
    for attempt in range(retries):
        try:
            return await coroutine(*args, **kwargs)
        except (TimeoutError, ConnectionError) as e:
            if attempt == retries - 1:
                raise e
            await asyncio.sleep(delay)
            delay *= 2

@Client.on_message(filters.command("start"))
async def start_message(c, m: Message):
    """Handle /start command and initialize user/channel/group."""

    # Handle sender info (user, channel, or anonymous admin)
    user = m.from_user
    sender_chat = m.sender_chat

    # Allow bot to work with channels/groups (for /start sent from them)
    if not user and not sender_chat:
        await m.reply("⚠️ I couldn't identify the sender. If you're using anonymous mode, try from your own account.")
        return

    # Use user ID or fallback to sender_chat ID (for channels/groups)
    sender_id = user.id if user else sender_chat.id
    sender_name = user.first_name if user else sender_chat.title
    sender_mention = user.mention if user else f"<code>{sender_chat.title}</code>"

    # Register in DB
    if not await db.is_user_exist(sender_id):
        await db.add_user(sender_id, sender_name)
        await c.send_message(
            LOG_CHANNEL,
            f"<b>#NewUser\nID - <code>{sender_id}</code>\nName - {sender_mention}</b>"
        )

    # Forced Sub check (optional, skip in channels)
    if IS_FSUB and user and not await get_fsub(c, m):
        return

    text = (
        f"Ahoy 👋 {m.from_user.mention},\n\n"
        "𝖨 𝖼𝖺𝗇 𝖺𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖺𝗉𝗉𝗋𝗈𝗏𝖾 𝗇𝖾𝗐 & 𝗉𝖾𝗇𝖽𝗂𝗇𝗀 𝗃𝗈𝗂𝗇 𝗋𝖾𝗊𝗎𝖾𝗌𝗍 𝗂𝗇 any C𝗁𝖺𝗇𝗇𝖾𝗅𝗌 𝗈𝗋 G𝗋𝗈𝗎𝗉𝗌.\n\n"
        "𝖩𝗎𝗌𝗍 𝖺𝖽𝖽 𝗆𝖾 𝗂𝗇 𝗒𝗈𝗎𝗋 𝖼𝗁𝖺𝗇𝗇𝖾𝗅𝗌 𝖺𝗇𝖽 𝗀𝗋𝗈𝗎𝗉𝗌 𝗐𝗂𝗍𝗁 𝗉𝖾𝗋𝗆𝗂𝗌𝗌𝗂𝗈𝗇 𝗍𝗈 𝖺𝖽𝖽 𝗇𝖾𝗐 𝗆𝖾𝗆𝖻𝖾𝗋𝗌.\n\n"
        "𝖴𝗌𝖾 /help for Guide\n\n"
        "**<blockquote>ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ : @Real_Pirates 🏴‍☠️</blockquote>**"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "⇆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⇆",
            url="https://t.me/Music_queen_X_bot?startgroup=true&admin=invite_users"
        )],
        [
            InlineKeyboardButton("• 𝐔𝐩𝐝𝐚𝐭𝐞𝐬 •", url="https://t.me/+sQXky-6HHq8xMTk1"),
            InlineKeyboardButton("• 𝐒𝐮𝐩𝐩𝐨𝐫𝐭 𝐆𝐫𝐨𝐮𝐩 •", url="https://t.me/Movie_Pirates_x")
        ],
        [InlineKeyboardButton(
            "⇆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ⇆",
            url="https://t.me/Music_queen_X_bot?startchannel=true&admin=invite_users"
        )],
    ])

    await m.reply_text(text, reply_markup=buttons)

@Client.on_message(filters.command('help'))
async def help_message(c, m):
    """Provide help instructions for joining channels."""
    await m.reply_text(
        f"""**Dear {m.from_user.mention},**

𝖱𝖾𝖺𝖽 𝗍𝗁𝗂𝗌 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝖼𝖺𝗋𝖾𝖿𝗎𝗅𝗅𝗒 𝗌𝗈 𝗒𝗈𝗎 𝖽𝗈𝗇'𝗍 𝗁𝖺𝗏𝖾 𝖺𝗇𝗒 𝗉𝗋𝗈𝖻𝗅𝖾𝗆𝗌 𝗐𝗁𝗂𝗅𝖾 joining channels.

🎯 **Join Any Channel in Just 2 Simple Steps** 🤫

🔹 **Step 1️⃣**  
To get access of any <b>Request to Join Channel</b>, add **Any One Tag** in your Bio,from below 👇

To Join
🎬 **Movie Channels**
⊱─‌─‌─‌─‌──‌─‌─‌─‌─‌─‌─‌─‌─‌⊰  
<blockquote>• `@Real_Pirates`</blockquote>
<blockquote>• `@Drama_Loverx`</blockquote>

To Join
📚 **Study / Skills Channels**
⊱─‌─‌─‌─‌──‌─‌─‌─‌─‌─‌─‌─‌─‌⊰  
<blockquote>• `@II_Way_to_Success_II`</blockquote>
<blockquote>• `@Myownsuccess`</blockquote>
<blockquote>• `@Just_Vibing_Alone`</blockquote>
<b><i>Tap to Copy 👆</i></b>
𝐀𝐝𝐝 𝐐𝐮𝐢𝐜𝐤𝐥𝐲 😉 : <b>{m.from_user.mention}</b> 👈

🔹 **Step 2️⃣**  
Once you've added **Any One** of these in your bio,  
Try joining again using the invite link —  
I'll be happy to approve your request! 😉
""",
        disable_web_page_preview=True
    )

@Client.on_message(filters.command("users") & filters.user(ADMINS))
async def users(bot, message):
    """Display total number of users (admin only)."""
    total_users = await db.total_users_count()
    await message.reply_text(f'◉ ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ: {total_users}')

@Client.on_message(filters.command("id"))
async def chat_id_cmd(client: Client, message: Message):
    chat = message.chat
    user = message.from_user

    # Chat Info
    chat_type = str(chat.type).capitalize()
    chat_title = chat.title or user.first_name if user else "Unknown"
    chat_username = f"@{chat.username}" if chat.username else "—"
    
    # User Info
    if user:
        user_id = user.id
        user_name = f"{user.first_name} {user.last_name or ''}".strip()
        user_username = f"@{user.username}" if user.username else "—"
    else:
        user_id = "—"
        user_name = "Unknown"
        user_username = "—"
    
    # Forwarded Info
    forward_date = (
        message.forward_origin.date.strftime("%Y-%m-%d %H:%M:%S")
        if message.forward_origin else None
    )

    text = f"""<b>🆔 ID & Info Panel</b>

<b>👤 User:</b> {user_name}
<b>🔸 User ID:</b> <code>{user_id}</code>
<b>🔹 Username:</b> {user_username}

<b>💬 Chat:</b> {chat_title}
<b>🔸 Chat ID:</b> <code>{chat.id}</code>
<b>🔹 Chat Type:</b> {chat_type}
<b>🌐 Username:</b> {chat_username}"""

    if forward_date:
        text += f"\n<b>📤 Forwarded On:</b> <code>{forward_date}</code>"

    await message.reply(text)



@Client.on_message(filters.command('accept') & filters.private)
async def accept(client, message):
    """Accept all pending join requests for a channel/group."""
    show = await message.reply("**Please Wait...**")
    user_data = await db.get_session(message.from_user.id)
    if user_data is None:
        await show.edit("**To accept pending requests, you must /login first.**")
        return

    try:
        acc = Client("joinrequest", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
        await acc.connect()
    except Exception as e:
        await show.edit(f"**Login failed: {e}. Please /logout and /login again.**")
        return

    await show.edit(
        "**Forward a message from your channel or group with the forward tag.\n"
        "Ensure the logged-in account is an admin with full rights.**"
    )
    vj = await client.listen(message.chat.id)
    if not (vj.forward_from_chat and vj.forward_from_chat.type not in [enums.ChatType.PRIVATE, enums.ChatType.BOT]):
        await vj.delete()
        await show.edit("**Message not forwarded from a channel or group.**")
        return

    chat_id = vj.forward_from_chat.id
    try:
        await retry_with_backoff(5, acc.get_chat, chat_id)
    except Exception as e:
        await vj.delete()
        await show.edit(f"**Error: Ensure the logged-in account is an admin with rights. {e}**")
        return

    await vj.delete()
    msg = await show.edit("**Accepting all join requests... Please wait.**")
    
    max_attempts = 100  # Prevent infinite loop
    attempts = 0
    try:
        while attempts < max_attempts:
            await retry_with_backoff(5, acc.approve_all_chat_join_requests, chat_id)
            await asyncio.sleep(1)
            join_requests = [request async for request in acc.get_chat_join_requests(chat_id)]
            if not join_requests:
                break
            attempts += 1
        await msg.edit("**Successfully accepted all join requests.**")
    except Exception as e:
        await msg.edit(f"**Error occurred: {e}**")
    finally:
        await acc.disconnect()

user_bios = {}

# Function to check the user's bio every 2 minutes
async def check_bio_periodically(client, chat_id, user_id, original_bio, required_tags):
    """Check the user's bio every 2 minutes to see if it contains required tags."""
    await asyncio.sleep(120)  # Wait for 2 minutes asynchronously
    
    # Get the user's bio again asynchronously
    user = await client.get_users(user_id)
    updated_bio = user.bio if user.bio else ""

    # If the bio doesn't contain required tags, remove the user
    if not any(tag in updated_bio.lower() for tag in required_tags):
        await client.kick_chat_member(chat_id, user_id)
        print(f"User {user_id} does not have required tags, removed from the group.")
