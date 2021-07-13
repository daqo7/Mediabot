import os
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import START_MSG, CHANNELS, ADMINS, INVITE_MSG
from utils import Media

logger = logging.getLogger(__name__)


@Client.on_message(filters.command('start'))
async def start(bot, message):
    """Komanda işləyicisini başladın"""
    if len(message.command) > 1 and message.command[1] == 'subscribe':
        await message.reply(INVITE_MSG)
    else:
        buttons = [[
            InlineKeyboardButton('Burada axtarın', switch_inline_query_current_chat=''),
            InlineKeyboardButton('İnline daxil olun', switch_inline_query=''),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(START_MSG, reply_markup=reply_markup)


@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
    """Kanalın əsas məlumatlarını göndərin"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Gözlənilməz KANALLAR növü")

    text = '📑 **İndeksli kanallar / qruplar**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Ümumi:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'İndeksli kanallar.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('total') & filters.user(ADMINS))
async def total(bot, message):
    """Bazada ümumi faylları göstərin"""
    msg = await message.reply("Qenerasiya olunur...⏳", quote=True)
    try:
        total = await Media.count_documents()
        await msg.edit(f'📁 Saxlanan fayllar: {total}')
    except Exception as e:
        logger.exception('Faylları yoxlamaq alınmadı')
        await msg.edit(f'Xəta: {e}')


@Client.on_message(filters.command('logger') & filters.user(ADMINS))
async def log_file(bot, message):
    """Günlük faylı göndər"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))


@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Məlumat bazasından faylı silin"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Qenerasiya olunur...⏳", quote=True)
    else:
        await message.reply('Silmək istədiyiniz fayla /delete göndərin', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('Bu fayl formatı dəstəklənmir')
        return

    result = await Media.collection.delete_one({
        'file_name': media.file_name,
        'file_size': media.file_size,
        'mime_type': media.mime_type,
        'caption': reply.caption
    })
    if result.deleted_count:
        await msg.edit('Fayl bazadan uğurla silindi')
    else:
        await msg.edit('Fayl bazada tapılmadı')
