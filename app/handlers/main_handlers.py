from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputFile, FSInputFile
from aiogram.fsm.context import FSMContext
from app.utils.exctract_text import image_to_text
from app.utils.google_translate import translate, translate_to_russian

from app.utils.tariffs import check_tariff_not_expired, get_lang_text, get_user_lang
from app.utils.gpt import gpt_clear, gpt_response_halal
from app.utils.determine_status import determine_verdict
from app.keyboards import continue_markup

router = Router()

status_to_image = {
            "халяль": "app/status_imgs/halal.jpg",
            "харам": "app/status_imgs/haram.jpg",
            "машбух": "app/status_imgs/mashbuh.jpg",
            "макрух": "app/status_imgs/makruh.jpg"
        }

@router.message(F.text)
async def proccess_text(message: Message, state: FSMContext):
    check_tariff = await check_tariff_not_expired(message.chat.id)
    user_lang = await get_user_lang(message.chat.id)
    if not check_tariff:
        tariff_expired = await get_lang_text(user_lang, 'expired_tariff')
        await message.answer(tariff_expired)
        return
    
    
    
    processing_text = await get_lang_text(user_lang, 'processing')
    processing_msg = await message.answer(processing_text)

    clean_words = await gpt_clear(message.text)
    if not clean_words:
        not_found_text = await get_lang_text(user_lang, 'not_founds')
        await message.answer(not_found_text)
        await message.bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
        return

    data = await state.get_data()
    current_components = data.get('components', [])
        
    current_components.extend(clean_words.strip().split(', '))
    await state.update_data(components=current_components)

    product_composition_text = await get_lang_text(user_lang, 'found')
    product_composition1 = product_composition_text.split('_')[0]
    product_composition2 = product_composition_text.split('_')[1]

    product_composition = product_composition1 + '\n'.join(current_components) + '\n' + product_composition2

    await message.answer(product_composition, reply_markup=continue_markup)
    await message.bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)


@router.message(F.photo)
async def proccess_photo(message: Message, state: FSMContext):
    check_tariff = await check_tariff_not_expired(message.chat.id)
    user_lang = await get_user_lang(message.chat.id)
    if not check_tariff:
        tariff_expired = await get_lang_text(user_lang, 'expired_tariff')
        await message.answer(tariff_expired)
        return
    

    processing_img_text = await get_lang_text(user_lang, 'image_processing')
    processing_msg = await message.answer(processing_img_text)

    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    downloaded_file = await message.bot.download_file(file_info.file_path)
    file_name = f"images/photo_{message.date}.jpg"
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file.read())
    
    text = image_to_text(file_name)

    await message.bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)

    if not text:
        not_recognized = await get_lang_text(user_lang, 'not_recognize')
        await message.answer(not_recognized)
        return
    
    processing_text = await get_lang_text(user_lang, 'processing')
    processing_msg = await message.answer(processing_text)

    clean_words = await gpt_clear(text)
    if not clean_words:
        not_found_text = await get_lang_text(user_lang, 'not_founds')
        await message.answer(not_found_text)
        await message.bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
        return

    data = await state.get_data()
    current_components = data.get('components', [])
        
    current_components.extend(clean_words.strip().split(', '))
    await state.update_data(components=current_components)

    product_composition_text = await get_lang_text(user_lang, 'found')
    product_composition1 = product_composition_text.split('_')[0]
    product_composition2 = product_composition_text('_')[1]

    product_composition = product_composition1 + '\n'.join(current_components) + '\n' + product_composition2

    await message.answer(product_composition, reply_markup=continue_markup)
    await message.bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)

    downloaded_file.close()


@router.callback_query(F.data.startswith('continue'))
async def handle_continue(callback: CallbackQuery, state: FSMContext):
    user_lang = await get_user_lang(callback.message.chat.id)
    components = await state.get_data()
    translated_words = translate(','.join(components.get('components', [])))
    final_words = [char.strip().lower() for char in translated_words.split(',')]

    await callback.answer('Обработка...')
    status = await determine_verdict(final_words)

    await state.clear()
    verdict = status[0]
    words_with_status = status[1]

    if verdict == "харам":
        haram_components = [word for word, status in words_with_status.items() if status.lower() == "харам"]
        haram_list = "\n".join(translate_to_russian(i) for i in haram_components)
        forbidden_text = await get_lang_text(user_lang, 'forbidden')

        caption = forbidden_text + '\n' + str(haram_list)
    elif verdict == "халяль":
        gpt_otvet = await gpt_response_halal()
        caption = f"Вердикт: {verdict.upper()}\n{gpt_otvet}"
    else:
        caption = await get_lang_text(user_lang, 'unknown')

    image_file_path = status_to_image[verdict]
    photo = FSInputFile(image_file_path)

    await callback.message.answer_photo(photo, caption=caption)

