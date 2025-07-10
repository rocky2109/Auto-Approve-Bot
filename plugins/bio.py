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
            await client.approve_chat_join_request(m.chat.id, m.from_user.id)

            approve_text = (
                f"🔓 <b>Access Granted ✅</b>\n\n"
                f"<b><blockquote> Cheers, <a href='https://t.me/Real_Pirates'>{full_name}</a> ! 🥂</blockquote></b>\n"
                f"Your Request To Join <b><a href='{invite_link}'> {chat.title} </a></b> Has Been Approved! 🎉\n"
                f"We’re happy to have you with us. 🥰\n\n"
                f"💎 𝐌𝐞𝐦𝐛𝐞𝐫𝐬 𝐂𝐨𝐮𝐧𝐭: <b>{member_count:,}</b> 🚀\n"
                f"┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌\n"
            )
            await m.reply_text(approve_text)

    # Second message: Warning about removing tags
            warning_text = (
                f"⚠️⚠️⚠️\n"
                f"<b><i>"
                f"||If you remove the tag(s) `{', '.join(required_tags)}` from your bio, you will be removed from the channel. 💀||\n"
                f"These tags are required to remain a verified member of > ≫  {chat.title}.\n"
                f"Make sure to keep that tag in your Bio to avoid removal. 😉"
                f"</i></b>"
            )
            await m.reply_text(warning_text)

            stickers = [
                "CAACAgUAAxkBAAKcLmf-E2SXmiXe99nF5KuHMMbeBsEoAALbHAACocj4Vkl1jIJ0iWpmHgQ",
                "CAACAgUAAxkBAAKcH2f94mJ3mIfgQeXmv4j0PlEpIgYMAAJvFAACKP14V1j51qcs1b2wHgQ",
                "CAACAgUAAxkBAAJLXmf2ThTMZwF8_lu8ZEwzHvRaouKUAAL9FAACiFywV69qth3g-gb4HgQ"
            ]

            try:
                await client.send_message(m.from_user.id, approve_text, disable_web_page_preview=True)
                await client.send_sticker(m.from_user.id, random.choice(stickers))
            except Exception as e:
                logger.warning(f"Could not DM approved user: {e}")

            try:
                await client.send_message(LOG_CHANNEL, approve_text, disable_web_page_preview=True)
                await client.send_sticker(LOG_CHANNEL, random.choice(stickers))
            except Exception as e:
                logger.warning(f"Could not send to log group: {e}")

        else:
            await client.decline_chat_join_request(m.chat.id, m.from_user.id)

            # Format each tag with bold
            tags_display = '\n'.join([f"<blockquote>● <code>{tag}</code> ♡</blockquote>" for tag in required_tags])

            reject_text = (
                f"🔒 <b>Access Denied ❌</b>\n\n"
                f"Dear <b>{m.from_user.mention}</b> 🌝 Your Request is Pending...\n\n" 
                f"if you want To join ⇙ Quickly"
                f"<blockquote><b><a href='{invite_link}'>{chat.title}</a></b></blockquote>"
                f"follow these <b>2 Simple Steps 😊</b>:\n"
                f"─‌─‌─‌─‌─‌─‌─‌─‌─‌─‌─‌─‌─‌─‌─‌─‌─‌─‌\n"
                f" 💡 <b><u>Step</u> 1️⃣</b>\n\n"
                f"Add This 👇 Tag in <b>Your Bio</b>\n"           
                f"{tags_display}\n"
                f"<i>Tap to Copy 👆</i>\n\n"
                f"𝐀𝐝𝐝 𝐐𝐮𝐢𝐜𝐤𝐥𝐲 𝐢𝐧 <b><a href='tg://settings'>Your Bio 👀</a></b>\n\n"                
                f" 💡 <b><u>Step</u> 2️⃣</b>\n\n"
                f"After updating your bio, try joining again by this Link 🔗 👇 \n<blockquote><b>{invite_link}</b></blockquote>\n"
                f"─‌─‌─‌─‌─‌─‌─‌─‌─‌─‌─‌─‌─‌─‌─‌─‌─‌─‌\n"
                f"✨ I’ll Approve you instantly if i detect the tag. Let's go! 😉"
            )
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📢 Updates", url="https://t.me/II_Way_to_Success_II"),
                    InlineKeyboardButton("💬 Support", url="https://t.me/GeniusJunctionX")
                ]
            ])

            try:
                await client.send_message(m.from_user.id, reject_text, disable_web_page_preview=True, reply_markup=buttons)
                await client.send_sticker(m.from_user.id, random.choice(stickers))
                
            except (UserNotMutualContact, PeerIdInvalid):
                pass
            except Exception as e:
                logger.warning(f"Could not DM rejected user: {e}")

    except Exception as e:
        logger.error(f"Join request handler error: {e}")
