from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("id"))
async def id_command_handler(client, message: Message):
    lines = []

    # 🆔 Chat ID
    lines.append(f"📢 **Chat ID:** `{message.chat.id}`")

    # 🙋‍♂️ From User ID
    if message.from_user:
        user = message.from_user
        name = f"{user.first_name} {user.last_name or ''}".strip()
        lines.append(f"🙋‍♂️ **Your ID:** `{user.id}`")
        lines.append(f"🧑‍💼 **Your Name:** `{name}`")
        if user.username:
            lines.append(f"🔗 **Username:** `@{user.username}`")

    # 🔁 Replied User
    if message.reply_to_message and message.reply_to_message.from_user:
        replied_user = message.reply_to_message.from_user
        rep_name = f"{replied_user.first_name} {replied_user.last_name or ''}".strip()
        lines.append("\n📥 **Replied To:**")
        lines.append(f"   ┗ 🆔 `{replied_user.id}`")
        lines.append(f"   ┗ 👤 `{rep_name}`")
        if replied_user.username:
            lines.append(f"   ┗ 🔗 `@{replied_user.username}`")

    # 🔄 Forwarded User
    if message.forward_from:
        fwd_user = message.forward_from
        fwd_name = f"{fwd_user.first_name} {fwd_user.last_name or ''}".strip()
        lines.append("\n📤 **Forwarded From:**")
        lines.append(f"   ┗ 🆔 `{fwd_user.id}`")
        lines.append(f"   ┗ 👤 `{fwd_name}`")
        if fwd_user.username:
            lines.append(f"   ┗ 🔗 `@{fwd_user.username}`")

    await message.reply_text("\n".join(lines), quote=True)
