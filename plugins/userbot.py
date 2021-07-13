import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from info import USERBOT_STRING_SESSION, API_ID, API_HASH, ADMINS, id_pattern
from utils import save_file

logger = logging.getLogger(__name__)
lock = asyncio.Lock()


@Client.on_message(filters.command(['index', 'indexfiles']) & filters.user(ADMINS))
async def index_files(bot, message):
    """İstifadəçi botunun köməyi ilə kanal və ya qrup sənədlərini qeyd edin"""

    if not USERBOT_STRING_SESSION:
        await message.reply('İnfo.py faylında və ya dəyişənlərdə "USERBOT_STRING_SESSION" düzəldin.')
    elif len(message.command) == 1:
        await message.reply('Zəhmət olmasa komanda kanal istifadəçi adı və ya id göstərin.\n\n'
                            'Misal: `/index -10012345678`')
    elif lock.locked():
        await message.reply('Əvvəlki proses tamamlanana qədər gözləyin.')
    else:
        msg = await message.reply('Qenerasiya olunur...⏳')
        raw_data = message.command[1:]
        user_bot = Client(USERBOT_STRING_SESSION, API_ID, API_HASH)
        chats = [int(chat) if id_pattern.search(chat) else chat for chat in raw_data]
        total_files = 0

        async with lock:
            try:
                async with user_bot:
                    for chat in chats:
                        
                        async for user_message in user_bot.iter_history(chat):
                            try:
                                message = await bot.get_messages(
                                    chat,
                                    user_message.message_id,
                                    replies=0,
                                )
                            except FloodWait as e:
                                await asyncio.sleep(e.x)
                                message = await bot.get_messages(
                                    chat,
                                    user_message.message_id,
                                    replies=0,
                                )
                            
                            for file_type in ("document", "video", "audio"):
                                media = getattr(message, file_type, None)
                                if media is not None:
                                    break
                            else:
                                continue
                            media.file_type = file_type
                            media.caption = message.caption
                            await save_file(media)
                            total_files += 1
            except Exception as e:
                logger.exception(e)
                await msg.edit(f'Xəta: {e}')
            else:
                await msg.edit(f'Cəmi {total_files} yoxlanıldı!')
