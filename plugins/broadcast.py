import time, datetime, asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from config import ADMINS
from plugins.database import db  # make sure this works!

# Send message to a single user
@Client.on_message(filters.command("send") & filters.user(ADMINS))
async def send_message_to_user(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("❌ Usage: `/send <user_id> <message>`", quote=True)

    try:
        user_id = int(message.command[1])
        text = " ".join(message.command[2:])
        await client.send_message(chat_id=user_id, text=text)
        await message.reply_text(f"✅ Message sent successfully to `{user_id}`.")
    except Exception as e:
        await message.reply_text(
            f"⚠️ Failed to send message.\n\n<b>Error:</b> <code>{str(e)}</code>",
            quote=True,
            parse_mode="html"
        )


# Broadcast a message to all users
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast(client: Client, message: Message):
    users = await db.get_all_users()
    total_users = await db.total_users_count()
    b_msg = message.reply_to_message

    sent = blocked = deleted = failed = 0
    start_time = time.time()
    done = 0

    sts = await message.reply_text("📢 Starting broadcast...")

    async for user in users:
        user_id = user.get("id")
        if not user_id:
            continue

        try:
            await b_msg.copy(chat_id=user_id)
            sent += 1

        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await b_msg.copy(chat_id=user_id)
                sent += 1
            except Exception:
                failed += 1

        except InputUserDeactivated:
            await db.delete_user(user_id)
            deleted += 1

        except UserIsBlocked:
            await db.delete_user(user_id)
            blocked += 1

        except PeerIdInvalid:
            await db.delete_user(user_id)
            failed += 1

        except Exception:
            failed += 1

        done += 1
        if done % 20 == 0:
            await sts.edit_text(
                f"📣 Broadcasting...\n"
                f"✅ Sent: {sent}\n"
                f"🚫 Blocked: {blocked}\n"
                f"🗑 Deleted: {deleted}\n"
                f"❌ Failed: {failed}\n"
                f"🔄 Progress: {done}/{total_users}"
            )

    end_time = time.time()
    duration = datetime.timedelta(seconds=int(end_time - start_time))

    await sts.edit_text(
        f"✅ Broadcast completed in {duration}.\n\n"
        f"👥 Total: {total_users}\n"
        f"✅ Sent: {sent}\n"
        f"🚫 Blocked: {blocked}\n"
        f"🗑 Deleted: {deleted}\n"
        f"❌ Failed: {failed}"
    )



# Store sent message IDs globally (ideally store in a database for persistence)
sent_messages = []

# Function to store the sent messages
async def store_sent_message(client: Client, chat_id, text):
    sent_msg = await client.send_message(chat_id, text)
    sent_messages.append(sent_msg.message_id)  # Store the message ID

# Command to delete all bot's sent messages in a private chat
@Client.on_message(filters.command("delete_all_msgs") & filters.private)
async def delete_all_bot_messages(client: Client, message):
    chat_id = message.chat.id  # Get the private chat ID

    # Go through all stored sent messages and delete them
    for msg_id in sent_messages:
        try:
            await client.delete_messages(chat_id, msg_id)
        except (PeerIdInvalid, MessageNotModified):
            pass  # Handle specific exceptions gracefully

    await message.reply_text("✅ All messages sent by the bot have been deleted successfully.")

# Example of sending a message and storing the message ID
@Client.on_message(filters.text)
async def example_message_handler(client: Client, message):
    if message.text.lower() == "send me a message":
        await store_sent_message(client, message.chat.id, "This is a message from the bot.")
