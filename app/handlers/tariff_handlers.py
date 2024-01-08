from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, ContentType, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from app.utils.tariffs import check_user_request, change_tariff_request, get_lang_text, get_user_lang, tariffrequest
from app.keyboards import tariffs, tariff_payment, tariffs_selection, kbd_lang
from app.states import SendCheck


router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_data = {
        'chat_id': message.chat.id,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name,
        'username': message.from_user.username,
    }
    response = await check_user_request(user_data)
    if response == 'new user':
        await message.answer("Выберите язык: ", reply_markup=kbd_lang)
    else:
        await message.answer(response)


@router.message(Command('send_check'))
async def send_check_command(message: Message, state: FSMContext):
    await state.set_state(SendCheck.what_tariff)
    user_lang = await get_user_lang(message.chat.id)
    caption = await get_lang_text(user_lang, 'what_tariff')
    await message.answer(caption, reply_markup=tariffs_selection)


@router.message(SendCheck.what_tariff)
async def get_tariff(message: Message, state: FSMContext):
    tariff = message.text
    user_lang = await get_user_lang(message.chat.id)
    await state.update_data(tariff=tariff)
    await state.set_state(SendCheck.waiting_for_check)
    caption = await get_lang_text(user_lang, 'send_check_photo')
    await message.answer(caption)


@router.message(SendCheck.waiting_for_check)
async def handle_photo(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message.chat.id)
    if message.photo:
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        downloaded_file = await message.bot.download_file(file_info.file_path)
        file_name = f"images/photo_{message.date}.jpg"
        
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file.read())


        # Получаем сохраненные данные из состояния
        data = await state.get_data()
        tariff = data.get("tariff")
        username = message.from_user.username
        chat_id = message.chat.id


        data = {
            'username': username,
            'tariff': tariff,
            'chat_id': chat_id,
        }

        response = await tariffrequest(data, file_name)
        if response:
            caption = await get_lang_text(user_lang, 'success_check')
            await message.answer(caption)
            await state.set_state(SendCheck.finish)
        else:
            await message.answer('Повторите позже')
    else:
        caption = await get_lang_text(user_lang, 'please_send_photo')
        await message.answer(caption)


@router.message(Command('tariff'))
async def select_tariff(message: Message):
    user_lang = await get_user_lang(message.chat.id)
    tariff_info = await get_lang_text(user_lang, 'tariff_list')
    await message.answer(tariff_info, reply_markup=tariffs)


@router.message(Command('help'))
async def get_help(message: Message):
    user_lang = await get_user_lang(message.chat.id)
    text = await get_lang_text(user_lang, 'helping')
    await message.answer(text)


@router.message(F.text.startswith('На год'))
@router.message(F.text.startswith('На полгода'))
@router.message(F.text.startswith('На месяц'))
async def change_tariff(message: Message):
    user_lang = await get_user_lang(message.chat.id)
    selected_tariff = message.text.lower().replace(" ", "_")

    if selected_tariff == "на_месяц":
        tariff = 'month'
        tariff_price = "250 сом"
    elif selected_tariff == "на_полгода":
        tariff = 'six-month'
        tariff_price = "1200 сом"
    elif selected_tariff == "на_год":
        tariff = 'year'
        tariff_price = "2000 сом"
    else:
        tariff_price = "Неизвестно"

    markup = tariff_payment(tariff_price, tariff)
    selected_tariff = selected_tariff.replace("_", " ")

    tap_to_pay = await get_lang_text(user_lang, 'for_change_tariff')
    tap_to_pay = tap_to_pay.replace('{selected_tariff}', selected_tariff)
    tap_to_pay = tap_to_pay.replace('{tariff_price}', tariff_price)

    await message.answer(tap_to_pay, reply_markup=markup)


prices = {
    'month': 25000,
    'six-month': 120000,
    'year': 200000
}


@router.callback_query(F.data.startswith('pay_'))
async def make_payment(callback: CallbackQuery):
    tariff = callback.data.split('_')[1]

    photo = FSInputFile('app/status_imgs/requisites.png')

    user_lang = await get_user_lang(callback.message.chat.id)
    caption = await get_lang_text(user_lang, 'requisites')

    # caption = "Нажмите на кнопку для оплаты картой через сам тг, в этом случае тариф сменится автоматически\nПри оплате через другие реквизиты, после оплаты впишите команду /send_check и отправьте фото чека, оператор проверит чек и сменит вам тариф."

    await callback.message.answer_photo(photo, caption=caption)

    # await callback.bot.send_invoice(
    #     chat_id=callback.message.chat.id,
    #     title='Обновление тарифа',
    #     description='Принятие платежа',
    #     provider_token='5707748563:LIVE:552637',
    #     payload=tariff,
    #     currency='kgs',
    #     prices=[
    #         LabeledPrice(
    #             label='Доступ к тарифу',
    #             amount=int(prices[tariff])
    #         )
    #     ],
    #     max_tip_amount=500,
    #     suggested_tip_amounts=[100, 200, 300, 400],
    #     start_parameter='start',
    #     provider_data=None,
    #     need_name=True,
    #     need_phone_number=True,


    # )

@router.pre_checkout_query()
async def process_payment_callback(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):    
    await message.answer('Тариф успешно сменён!')
    selected_tariff = message.successful_payment.invoice_payload

    response = await change_tariff_request(message.chat.id, selected_tariff)
    await message.answer(response)