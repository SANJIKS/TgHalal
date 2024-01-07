from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.utils.tariffs import change_lang_request

from app.keyboards import kbd_lang

router = Router()

@router.message(Command('lang'))
async def language_command(message: Message):
    await message.answer("Установить язык", reply_markup=kbd_lang)

@router.callback_query(F.data.startswith('lang_'))
async def change_language(callback: CallbackQuery):
    lang = callback.data.split('_')[1]
    chat_id = callback.message.chat.id
    response = await change_lang_request(chat_id, lang)
    if response:
        callback.message.answer('Язык успешно сменён!')
    else:
        callback.message.answer('Произошла ошибка.')