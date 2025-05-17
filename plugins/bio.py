import logging
import random
from pyrogram import Client
from pyrogram.types import ChatJoinRequest
from pyrogram.errors import UserNotMutualContact, PeerIdInvalid

from config import LOG_CHANNEL, NEW_REQ_MODE

logging.disable(logging.CRITICAL)

# Define your required tags per channel or globally
REQUIRED_TAGS = ["@real_pirates"]  # You can make this dynamic per chat if needed

# Check if user's bio has at least one required tag
def has_required_tag_in_bio(bio: str, required_tags: list):
    if not bio or not required_tags:
        return False
    bio = bio.lower()
    return any(tag.lower() in bio for tag in required_tags)

# Main join request handler
async def handle_join_request(client: Client, m: ChatJoinRequest, NEW_REQ_MODE: bool, LOG_CHANNEL: int):
    if not NEW_REQ_MODE:
        return

    try:
        chat = await client.get_chat(m.chat.id)
        user = await client.get_chat(m.from_user.id)
        bio = user.bio or ""

        # Create join link (optional, you can use a static one if you prefer)
        invite_link_obj = await client.create_chat_invite_link(
            chat_id=m.chat.id,
            name=f"Join {chat.title}",
            creates_join_request=True
        )
        invite_link = invite_link_obj.invite_link

        full_name = f"{m.from_user.first_name or ''} {m.from_user.last_name or ''}".strip()

        if has_required_tag_in_bio(bio, REQUIRED_TAGS):
            # Approve user
            await client.approve_chat_join_request(m.chat.id, m.from_user.id)

            approved_text = (
                f"✅ <b>Access Granted</b>\n\n"
                f"Hey <a href='tg://user?id={m.from_user.id}'>{full_name}</a>, welcome aboard! 🥳\n"
                f"Your request to join <b>{chat.title}</b> has been approved!\n\n"
                f"<i>Make sure to keep the required tag in your bio to remain a member!</i>"
            )

            try:
                await client.send_message(m.from_user.id, approved_text, parse_mode="html")
                await client.send_sticker(m.from_user.id, "CAACAgUAAxkBAAKcLmf-E2SXmiXe99nF5KuHMMbeBsEoAALbHAACocj4Vkl1jIJ0iWpmHgQ")
            except Exception as e:
                print(f"Failed to send PM to approved user: {e}")

            try:
                await client.send_message(LOG_CHANNEL, f"✅ Approved: {full_name} ({m.from_user.id})")
            except:
                pass

        else:
            # Deny user
            await client.decline_chat_join_request(m.chat.id, m.from_user.id)

            denied_text = (
                f"❌ <b>Access Denied</b>\n\n"
                f"Hello <b>{m.from_user.mention}</b>,\n"
                f"To join <b>{chat.title}</b>, please add <code>{', '.join(REQUIRED_TAGS)}</code> to your bio.\n\n"
                f"After updating your bio, click the button below to try again:\n"
                f"<a href='{invite_link}'>Join {chat.title}</a>"
            )

            try:
                await client.send_message(m.from_user.id, denied_text, parse_mode="html", disable_web_page_preview=True)
                await client.send_sticker(m.from_user.id, "CAACAgUAAxkBAAKcH2f94mJ3mIfgQeXmv4j0PlEpIgYMAAJvFAACKP14V1j51qcs1b2wHgQ")
            except (UserNotMutualContact, PeerIdInvalid):
                pass
            except Exception as e:
                print(f"Failed to send PM to denied user: {e}")

    except Exception as e:
        print(f"Error processing join request: {e}")

# Register handler
@Client.on_chat_join_request()
async def join_request_handler(client, request):
    await handle_join_request(client, request, NEW_REQ_MODE, LOG_CHANNEL)
