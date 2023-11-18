from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from app.utils.tariffs import check_user_request, change_tariff_request
from app.keyboards import tariffs, tariff_payment


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
    await message.answer(response)

@router.message(Command('tariff'))
async def select_tariff(message: Message):
    tariff_info = 'Выберите тариф, чтобы начать использовать нашего бота, который может распознавать халяль и харам товары:\n\n1. Тариф на месяц:\n   - Стоимость: 250 сом\n   - Период: 30 дней\n\n2. Тариф на полгода:\n   - Стоимость: 1200 сом\n   - Период: 180 дней\n\n3. Тариф на год:\n   - Стоимость: 2000 сом\n   - Период: 365 дней\n\nДля оплаты выбранного тарифа, нажмите на соответствующую кнопку \"Оплатить\".'
    await message.answer(tariff_info, reply_markup=tariffs)


@router.message(F.text.startswith('На год'))
@router.message(F.text.startswith('На полгода'))
@router.message(F.text.startswith('На месяц'))
async def change_tariff(message: Message):
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

    await message.answer(f'Для изменения тарифа на {selected_tariff.replace("_", " ")} необходимо оплатить {tariff_price}.', reply_markup=markup)


@router.callback_query(F.data.startswith('pay_'))
async def process_payment_callback(callback: CallbackQuery):
    selected_tariff = callback.data.replace('pay_', '').replace('_', ' ')
    response = await change_tariff_request(callback.message.chat.id, selected_tariff)
    await callback.message.answer(response)