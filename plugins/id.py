from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("id"))
async def id_command_handler(client, message: Message):
    text = ""

    # 1. Chat ID (group/channel/PM)
    text += f"**Chat ID:** `{message.chat.id}`\n"

    # 2. From user ID (if available)
    if message.from_user:
        text += f"**Your ID:** `{message.from_user.id}`\n"

    # 3. Replied user ID (if replying to someone)
    if message.reply_to_message and message.reply_to_message.from_user:
        replied_id = message.reply_to_message.from_user.id
        text += f"**Replied User ID:** `{replied_id}`\n"

    # 4. Forwarded user ID
    if message.forward_from:
        text += f"**Forwarded From User ID:** `{message.forward_from.id}`\n"

    await message.reply(text)
