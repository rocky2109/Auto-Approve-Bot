import random
import logging
from pyrogram import Client
from pyrogram.types import ChatJoinRequest
from pyrogram.errors import UserNotMutualContact, PeerIdInvalid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Map hashtags in channel description to lists of required @tags in user bio
TAG_MAP = {
    "#movie": ["@real_pirates", "@drama_loverx"],  # #movie allows either tag
    "#drama": ["@drama_loverx"],
    "#study": ["@ii_way_to_success_ii"],
    "#success": ["@myownsuccess", "@drama_loverx"],  # #success allows either tag
    "#goal": ["@goal_achieverr"],
    "#alone": ["@just_vibing_alone"],
}

# Function to detect the required tags based on channel description
def get_required_tags_from_description(description: str):
    description = description.lower()
    required_tags = []
    for hashtag, tags in TAG_MAP.items():
        if hashtag in description:
            required_tags.extend(tags)
    # Remove duplicates while preserving order
    return list(dict.fromkeys(required_tags))

# Function to check if the user has at least one required tag in their bio
def has_required_tag_in_bio(user_bio: str, required_tags: list):
    if not user_bio or not required_tags:
        return False
    user_bio = user_bio.lower()
    return any(tag.lower() in user_bio for tag in required_tags)

async def handle_join_request(client: Client, m: ChatJoinRequest, NEW_REQ_MODE: bool, LOG_GROUP: int):
    if not NEW_REQ_MODE:
        return

    try:
        chat = await client.get_chat(m.chat.id)
        description = chat.description or ""

        # Identify tags based on channel description
        required_tags = get_required_tags_from_description(description)
        if not required_tags:
            logger.info(f"No required tags found for chat {chat.id}")
            return

        user = await client.get_chat(m.from_user.id)
        bio = user.bio or ""

        # Generate a "request to join" invite link
        invite_link_obj = await client.create_chat_invite_link(
            chat_id=m.chat.id,
            name=f"Join {chat.title}",
            creates_join_request=True  # Requires admin approval
        )
        invite_link = invite_link_obj.invite_link

        if has_required_tag_in_bio(bio, required_tags):
            # Approve the join request
            await client.approve_chat_join_request(m.chat.id, m.from_user.id)

            full_name = f"{m.from_user.first_name or ''} {m.from_user.last_name or ''}".strip()
            member_count = chat.members_count

            # Prepare the approval message
            approve_text = (
                f"🔓 <b>Access Granted ✅</b>\n\n"
                f"<b><blockquote> Cheers, <a href='https://t.me/Real_Pirates'>{full_name}</a> ! 🥂</blockquote></b>\n"
                f"Your Request To Join <b><a href='{invite_link}'> {chat.title} </a></b> Has Been Approved! 🎉\n"
                f"We’re happy to have you with us. 🥰\n\n"
                f"💎 𝐌𝐞𝐦𝐛𝐞𝐫𝐬 𝐂𝐨𝐮𝐧𝐭: <b>{member_count:,}</b> 🚀\n"
                f"┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌\n"
                f"⚠️⚠️⚠️\n"
                f"<b><i>||If you remove the tag(s) {', '.join(required_tags)} from your bio, you will be removed from the channel. 💀||\n"
                f"These tags are required to remain a verified member of ≫  {chat.title}.\n"
                f"Make sure to keep at least one in your Bio to avoid removal. 😉</i></b>\n"
                f"<blockquote>Supported by <b>➩ @Real_Pirates 🏴‍☠️</b></blockquote>"
            )

            stickers = [
                "CAACAgUAAxkBAAKcLmf-E2SXmiXe99nF5KuHMMbeBsEoAALbHAACocj4Vkl1jIJ0iWpmHgQ",
                "CAACAgUAAxkBAAKcH2f94mJ3mIfgQeXmv4j0PlEpIgYMAAJvFAACKP14V1j51qcs1b2wHgQ",
                "CAACAgUAAxkBAAJLXmf2ThTMZwF8_lu8ZEwzHvRaouKUAAL9FAACiFywV69qth3g-gb4HgQ"
            ]

            # Send approval message and sticker
            try:
                await client.send_message(m.from_user.id, approve_text, disable_web_page_preview=True, parse_mode="html")
                await client.send_sticker(m.from_user.id, random.choice(stickers))
            except Exception as e:
                logger.error(f"Failed to send approval to {m.from_user.id}: {e}")

            try:
                await client.send_message(LOG_GROUP, approve_text, disable_web_page_preview=True, parse_mode="html")
                await client.send_sticker(LOG_GROUP, random.choice(stickers))
            except Exception as e:
                logger.error(f"Failed to send log message: {e}")

        else:
            # Decline the join request
            await client.decline_chat_join_request(m.chat.id, m.from_user.id)

            reject_text = (
                f"🔒 **Access Denied** ❌\n\n"
                f"Dear **{m.from_user.mention}** 🌝\n\n"
                f"To join <b>{chat.title}</b>, follow these **2 Simple Steps**: 🤫\n\n"
                f"🔹 **Step 1️⃣**\n"
                f"<b>Add one of these tags in your bio</b>: <code>{', '.join(required_tags)}</code> ✅\n\n"
                f"🔹 **Step 2️⃣**\n"
                f"After updating your bio, try joining again using the invite link: <a href='{invite_link}'>Join {chat.title}</a>.  \n"
                f"**I'll approve your request!** 😉\n\n"
                f"||/help|| 🌝"
            )

            try:
                await client.send_message(m.from_user.id, reject_text, disable_web_page_preview=True, parse_mode="html")
                await client.send_sticker(
                    m.from_user.id,
                    "CAACAgUAAxkBAAKcH2f94mJ3mIfgQeXmv4j0PlEpIgYMAAJvFAACKP14V1j51qcs1b2wHgQ"
                )
            except (UserNotMutualContact, PeerIdInvalid):
                pass
            except Exception as e:
                logger.error(f"Failed to send rejection to {m.from_user.id}: {e}")

    except Exception as e:
        logger.error(f"Error processing join request: {e}")
