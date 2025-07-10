import random
import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest, Message
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid, UserNotMutualContact
from config import *
from .database import db

logger = logging.getLogger(__name__)

# Updated TAG MAP with multiple tags for #study
TAG_MAP = {
    "#movie": ["@real_pirates", "@drama_loverx"],
    "#drama": ["@drama_loverx"],
    "#study": ["@II_LevelUP_II"],
    "#success": ["@ii_way_to_success_ii"],
    "#skill": ["@II_LevelUP_II"],
    "#alone": ["@just_vibing_alone"],
}


async def retry_with_backoff(retries, coroutine, *args, **kwargs):
    delay = 1
    for attempt in range(retries):
        try:
            return await coroutine(*args, **kwargs)
        except (TimeoutError, ConnectionError) as e:
            if attempt == retries - 1:
                raise e
            await asyncio.sleep(delay)
            delay *= 2


def get_required_tags_from_description(description: str):
    description = description.lower()
    required_tags = []
    for hashtag, tags in TAG_MAP.items():
        if hashtag in description:
            required_tags.extend(tags)
    return list(dict.fromkeys(required_tags))


def has_required_tag_in_bio(user_bio: str, required_tags: list):
    if not user_bio or not required_tags:
        return False
    user_bio = user_bio.lower()
    return any(tag.lower() in user_bio for tag in required_tags)

from pyrogram.errors import UserAlreadyParticipant

@Client.on_chat_join_request()
async def join_request_handler(client: Client, m: ChatJoinRequest):
    if not NEW_REQ_MODE:
        return

    try:
        chat = await client.get_chat(m.chat.id)
        description = chat.description or ""
        required_tags = get_required_tags_from_description(description)

        if not required_tags:
            logger.info(f"No required tags for chat {chat.id}")
            return

        user = await client.get_chat(m.from_user.id)
        bio = user.bio or ""

        invite_link_obj = await client.create_chat_invite_link(
            chat_id=m.chat.id,
            name=f"Join {chat.title}",
            creates_join_request=True
        )
        invite_link = invite_link_obj.invite_link

        full_name = f"{m.from_user.first_name or ''} {m.from_user.last_name or ''}".strip()
        member_count = chat.members_count

        if has_required_tag_in_bio(bio, required_tags):
            try:
                await client.approve_chat_join_request(m.chat.id, m.from_user.id)
            except UserAlreadyParticipant:
                logger.info(f"User {m.from_user.id} is already in {chat.title}")

            approve_text = (
                f"🔓 <b>Access Granted ✅</b>\n\n"
                f"<b><blockquote> Cheers, <a href='https://t.me/Real_Pirates'>{full_name}</a> ! 🥂</blockquote></b>\n"
                f"Request To Join <b><a href='{invite_link}'> {chat.title} </a></b> Approved! 🎉\n\n"
                f"💎 𝐌𝐞𝐦𝐛𝐞𝐫𝐬 𝐂𝐨𝐮𝐧𝐭: <b>{member_count:,}</b> 🚀\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            )

            warning_text = (
                f"⚠️ <b><i>Reminder:</i></b>\n"
                f"<i>Removing the tag(s) `{', '.join(required_tags)}` from your bio will result in removal from <b>{chat.title}</b>. 💀\n"
                f"Keep it to stay verified. 😉</i>"
            )

            # ✅ Send approve + warning to log/approve channel ONLY
            try:
                await client.send_message(APPROVE_CHANNEL, approve_text + warning_text, disable_web_page_preview=True)
                await client.send_sticker(APPROVE_CHANNEL, random.choice([
                    "CAACAgUAAxkBAAKcLmf-E2SXmiXe99nF5KuHMMbeBsEoAALbHAACocj4Vkl1jIJ0iWpmHgQ",
                    "CAACAgUAAxkBAAKcH2f94mJ3mIfgQeXmv4j0PlEpIgYMAAJvFAACKP14V1j51qcs1b2wHgQ",
                    "CAACAgUAAxkBAAJLXmf2ThTMZwF8_lu8ZEwzHvRaouKUAAL9FAACiFywV69qth3g-gb4HgQ"
                ]))
            except Exception as e:
                logger.warning(f"❌ Could not send to APPROVE_CHANNEL: {e}")

        else:
            await client.decline_chat_join_request(m.chat.id, m.from_user.id)

            tags_display = '\n'.join([f"<blockquote>● <code>{tag}</code> ♡</blockquote>" for tag in required_tags])

            reject_text = (
                f"🔒 <b>Access Denied ❌</b>\n\n"
                f"Dear <b>{m.from_user.mention}</b> 🌝 Your Request is Pending...\n\n"
                f"To join <b>{chat.title}</b> quickly:\n"
                f"🔹 <b>Step 1:</b> Add this tag in your bio:\n{tags_display}\n"
                f"🔹 <b>Step 2:</b> Retry via this link:\n{invite_link}\n\n"
                f"✨ I’ll approve you instantly if I detect the tag!"
            )

            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📢 Updates", url="https://t.me/II_Way_to_Success_II"),
                    InlineKeyboardButton("💬 Support", url="https://t.me/GeniusJunctionX")
                ]
            ])

            try:
                await client.send_message(m.from_user.id, reject_text, disable_web_page_preview=True, reply_markup=buttons)
                await client.send_sticker(m.from_user.id, random.choice([
                    "CAACAgUAAxkBAAKcLmf-E2SXmiXe99nF5KuHMMbeBsEoAALbHAACocj4Vkl1jIJ0iWpmHgQ",
                    "CAACAgUAAxkBAAKcH2f94mJ3mIfgQeXmv4j0PlEpIgYMAAJvFAACKP14V1j51qcs1b2wHgQ",
                    "CAACAgUAAxkBAAJLXmf2ThTMZwF8_lu8ZEwzHvRaouKUAAL9FAACiFywV69qth3g-gb4HgQ"
                ]))
            except Exception as e:
                logger.warning(f"❌ Could not DM rejected user: {e}")

    except Exception as e:
        logger.error(f"Join request handler error: {e}")


