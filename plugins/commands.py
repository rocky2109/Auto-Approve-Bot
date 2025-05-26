import asyncio 
from pyrogram import Client, filters, enums
from config import *
from .database import db
from .fsub import get_fsub
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, ChatJoinRequest
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
import datetime
import time
import logging
from pyrogram.types import ChatMemberUpdated
import sqlite3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Global flag to control auto-approve
NEW_REQ_MODE = True

              
@Client.on_message(filters.command("start"))
async def start_message(c, m):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id, m.from_user.first_name)
        await c.send_message(LOG_CHANNEL, f"<b>#NewUser\nID - <code>{m.from_user.id}</code>\nName - {m.from_user.mention}</b>")

    if IS_FSUB and not await get_fsub(c, m): return

    text = (
        f"<b><blockquote> Ahoy Dear! 👋 {m.from_user.mention}</blockquote></b>\n\n"
        "𝖨 𝖼𝖺𝗇 𝖺𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖺𝗉𝗉𝗋𝗈𝗏𝖾 𝗇𝖾𝗐 𝖺𝗌 𝗐𝖾𝗅𝗅 𝖺𝗌 𝗉𝖾𝗇𝖽𝗂𝗇𝗀 𝗃𝗈𝗂𝗇 𝗋𝖾𝗊𝗎𝖾𝗌𝗍 𝗂𝗇 𝗒𝗈𝗎𝗋 𝖼𝗁𝖺𝗇𝗇𝖾𝗅𝗌 𝗈𝗋 𝗀𝗋𝗈𝗎𝗉𝗌.\n\n"
        "𝖩𝗎𝗌𝗍 𝖺𝖽𝖽 𝗆𝖾 𝗂𝗇 𝗒𝗈𝗎𝗋 𝖼𝗁𝖺𝗇𝗇𝖾𝗅𝗌 𝖺𝗇𝖽 𝗀𝗋𝗈𝗎𝗉𝗌 𝗐𝗂𝗍𝗁 𝗉𝖾𝗋𝗆𝗂𝗌𝗌𝗂𝗈𝗇 𝗍𝗈 𝖺𝖽𝖽 𝗇𝖾𝗐 𝗆𝖾𝗆𝖻𝖾𝗋𝗌.\n\n"
        "𝖴𝗌𝖾 /help 𝖿𝗈𝗋 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌 𝖺𝗇𝖽 𝖽𝖾𝗍𝖺𝗂𝗅𝗌.\n\n"
        "**<blockquote>ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ : @Movie_Pirates_x</blockquote>**"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⇆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘs ⇆", url="https://telegram.me/X_Queen_chat_bot?startgroup=true&admin=invite_users")],
        [InlineKeyboardButton("• 𝐔𝐩𝐝𝐚𝐭𝐞𝐬 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 •", url="https://t.me/+sQXky-6HHq8xMTk1"),
         InlineKeyboardButton("• 𝐌𝐨𝐯𝐢𝐞 𝐆𝐫𝐨𝐮𝐩 •", url="https://t.me/Movie_Pirates_x")],
        [InlineKeyboardButton("⇆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ⇆", url="https://telegram.me/X_Queen_chat_bot?startchannel=true&admin=invite_users")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
])


    await m.reply_text(text, reply_markup=buttons)


@Client.on_chat_member_updated()
async def track_admin_channels(client, update: ChatMemberUpdated):
    try:
        if update.new_chat_member and update.new_chat_member.user.id == client.me.id:
            new_status = update.new_chat_member.status
            if new_status == "administrator":
                chat_id = update.chat.id
                title = update.chat.title or "Unnamed"

                cur.execute("INSERT OR IGNORE INTO channels (chat_id, title) VALUES (?, ?)", (chat_id, title))
                conn.commit()
                print(f"✅ Added: {title} ({chat_id})")
    except Exception as e:
        print(f"[track_admin_channels ERROR] {e}")

@Client.on_callback_query(filters.regex("settings"))
async def open_settings_cb(client, query):
    try:
        cur.execute("SELECT chat_id, title FROM channels")
        rows = cur.fetchall()

        if not rows:
            await query.message.edit_text("⚠️ No channels found where I'm admin.")
            return

        keyboard = []
        for chat_id, title in rows:
            # For private channels (starting with -100), format correctly
            channel_url = f"https://t.me/c/{str(chat_id)[4:]}" if str(chat_id).startswith("-100") else f"https://t.me/{title}"
            keyboard.append([InlineKeyboardButton(title, url=channel_url)])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text("🛠️ Channels where I'm admin:", reply_markup=reply_markup)
    except Exception as e:
        print(f"[open_settings_cb ERROR] {e}")
        await query.message.edit_text("❌ Error loading channels.")
        
@Client.on_callback_query(filters.regex("back_to_home"))
async def back_home_cb(client, callback_query):
    await start_message(client, callback_query.message)  # Re-use existing /start handler

@Client.on_message(filters.command('help'))
async def help_message(c,m):
   await m.reply_text(f"{m.from_user.mention},\n\n𝖱𝖾𝖺𝖽 𝗍𝗁𝗂𝗌 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝖼𝖺𝗋𝖾𝖿𝗎𝗅𝗅𝗒 𝗌𝗈 𝗒𝗈𝗎 𝖽𝗈𝗇'𝗍 𝗁𝖺𝗏𝖾 𝖺𝗇𝗒 𝗉𝗋𝗈𝖻𝗅𝖾𝗆𝗌 𝗐𝗁𝗂𝗅𝖾 𝗎𝗌𝗂𝗇𝗀 𝗆𝖾.\n\n𝟏. 𝐇𝐨𝐰 𝐭𝐨 𝐚𝐜𝐜𝐞𝐩𝐭 𝐧𝐞𝐰 𝐣𝐨𝐢𝐧 𝐫𝐞𝐪𝐮𝐞𝐬𝐭𝐬?\n\n👉 𝖩𝗎𝗌𝗍 𝖺𝖽𝖽 𝗆𝖾 𝗂𝗇 𝗒𝗈𝗎 𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝗈𝗋 𝗀𝗋𝗈𝗎𝗉 𝖺𝗌 𝖺𝖽𝗆𝗂𝗇 𝖺𝗇𝖽 𝗐𝗂𝗍𝗁 𝗉𝖾𝗋𝗆𝗂𝗌𝗌𝗂𝗈𝗇 𝗍𝗈 𝖺𝖽𝖽 𝗇𝖾𝗐 𝗆𝖾𝗆𝖻𝖾𝗋𝗌.\n\n𝟐. 𝐇𝐨𝐰 𝐭𝐨 𝐚𝐜𝐜𝐞𝐩𝐭 𝐩𝐞𝐧𝐝𝐢𝐧𝐠 𝐣𝐨𝐢𝐧 𝐫𝐞𝐪𝐮𝐞𝐬𝐭𝐬?\n\n👉 𝖥𝗂𝗋𝗌𝗍 𝖺𝖽𝖽 𝗆𝖾 𝖺𝗌 𝖺𝖽𝗆𝗂𝗇 𝗂𝗇 𝗒𝗈𝗎𝗋 𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝗈𝗋 𝗀𝗋𝗈𝗎𝗉 𝗐𝗂𝗍𝗁 𝗉𝖾𝗋𝗆𝗂𝗌𝗌𝗂𝗈𝗇 𝗍𝗈 𝖺𝖽𝖽 𝗇𝖾𝗐 𝗆𝖾𝗆𝖻𝖾𝗋𝗌.\n\n👉 𝖳𝗁𝖾𝗇 𝗅𝗈𝗀𝗂𝗇 𝗂𝗇𝗍𝗈 𝗍𝗁𝖾 𝖻𝗈𝗍 𝗆𝗒 𝗎𝗌𝗂𝗇𝗀 /login 𝖼𝗈𝗆𝗆𝖺𝗇𝖽.\n\n👉 𝖭𝗈𝗐 𝗎𝗌𝖾 /accept 𝖼𝗈𝗆𝗆𝖺𝗇𝖽 𝗍𝗈 𝖺𝖼𝖼𝖾𝗉𝗍 𝖺𝗅𝗅 𝗉𝖾𝗇𝖽𝗂𝗇𝗀 𝗋𝖾𝗊𝗎𝖾𝗌𝗍.\n\n👉 𝖭𝗈𝗐 𝗃𝗎𝗌𝗍 𝗎𝗌𝖾 /logout 𝖼𝗈𝗆𝗆𝖺𝗇𝖽 𝖿𝗈𝗋 𝗅𝗈𝗀𝗈𝗎𝗍.\n\n<b>𝖨𝖿 𝗒𝗈𝗎 𝗌𝗍𝗂𝗅𝗅 𝖿𝖺𝖼𝖾 𝖺𝗇𝗒 𝗂𝗌𝗌𝗎𝖾 𝗍𝗁𝖾𝗇 𝖼𝗈𝗇𝗍𝖺𝖼𝗍 @CaptainX_Contact_bot</b>")

@Client.on_message(filters.command("users") & filters.user(ADMINS))
async def users(bot, message):
   total_users = await db.total_users_count()
   await message.reply_text(
        text=f'◉ ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ: {total_users}'
   )

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast(bot, message):
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text("Broadcasting your messages...")
    
    start_time = time.time()
    total_users = await db.total_users_count()

    # Initialize Counters
    done, blocked, deleted, failed, success = 0, 0, 0, 0, 0

    async for user in users:
        if 'id' in user:
            user_id = int(user['id'])
            try:
                await retry_with_backoff(5, b_msg.copy, chat_id=user_id)
                success += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
                try:
                    await b_msg.copy(chat_id=user_id)
                    success += 1
                except Exception:
                    failed += 1
            except InputUserDeactivated:
                await db.delete_user(user_id)
                logging.info(f"{user_id} - Removed from database (Deleted Account).")
                deleted += 1
            except UserIsBlocked:
                await db.delete_user(user_id)
                logging.info(f"{user_id} - Blocked the bot.")
                blocked += 1
            except PeerIdInvalid:
                await db.delete_user(user_id)
                logging.info(f"{user_id} - PeerIdInvalid")
                failed += 1
            except Exception:
                failed += 1
            
            done += 1
            if not done % 20:
                await sts.edit(f"Broadcast in progress:\n\nTotal Users: {total_users}\nCompleted: {done}/{total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")
    
    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users: {total_users}\nCompleted: {done}/{total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")

@Client.on_message(filters.command('accept') & filters.private)
async def accept(client, message):
    show = await message.reply("**Please Wait.....**")
    user_data = await db.get_session(message.from_user.id)
    if user_data is None:
        await show.edit("**For Accepte Pending Request You Have To /login First.**")
        return
    try:
        acc = Client("joinrequest", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
        await acc.connect()
    except:
        return await show.edit("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
    show = await show.edit("**Now Forward A Message From Your Channel Or Group With Forward Tag\n\nMake Sure Your Logged In Account Is Admin In That Channel Or Group With Full Rights.**")
    vj = await client.listen(message.chat.id)
    if vj.forward_from_chat and not vj.forward_from_chat.type in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
        chat_id = vj.forward_from_chat.id
        try:
            await retry_with_backoff(5, acc.get_chat, chat_id)
        except:
            await show.edit("**Error - Make Sure Your Logged In Account Is Admin In This Channel Or Group With Rights.**")
    else:
        return await message.reply("**Message Not Forwarded From Channel Or Group.**")
    await vj.delete()
    msg = await show.edit("**Accepting all join requests... Please wait until it's completed.**")
    try:
        while True:
            await retry_with_backoff(5, acc.approve_all_chat_join_requests, chat_id)
            await asyncio.sleep(1)
            join_requests = [request async for request in acc.get_chat_join_requests(chat_id)]
            if not join_requests:
                break
        await msg.edit("**Successfully accepted all join requests.**")
    except Exception as e:
        await msg.edit(f"**An error occurred:** {str(e)}")

@Client.on_message(filters.command("toggle_mode") & filters.user(6947378236))
async def toggle_mode(_, message: Message):
    global NEW_REQ_MODE
    NEW_REQ_MODE = not NEW_REQ_MODE
    status = "enabled ✅" if NEW_REQ_MODE else "disabled ❌"
    await message.reply(f"Auto-approve mode is now *{status}*")

