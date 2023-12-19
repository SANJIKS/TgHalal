from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, ContentType
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


prices = {
    'month': 25000,
    'six-month': 120000,
    'year': 200000
}


@router.callback_query(F.data.startswith('pay_'))
async def make_payment(callback: CallbackQuery):
    tariff = callback.data.split('_')[1]

    await callback.bot.send_invoice(
        chat_id=callback.message.chat.id,
        title='Обновление тарифа',
        description='Принятие платежа',
        provider_token='5707748563:LIVE:552637',
        payload=tariff,
        currency='kgs',
        prices=[
            LabeledPrice(
                label='Доступ к тарифу',
                amount=int(prices[tariff])
            )
        ],
        max_tip_amount=500,
        suggested_tip_amounts=[100, 200, 300, 400],
        start_parameter='start',
        provider_data=None,
        need_name=True,
        need_phone_number=True,


    )

@router.pre_checkout_query()
async def process_payment_callback(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

    # selected_tariff = pre_checkout_query.invoice_payload
    # chat_id = pre_checkout_query.from_user.id

    # response = await change_tariff_request(chat_id, selected_tariff)    
    # await bot.send_message(chat_id, response)

@router.message(F.successful_payment)
async def successful_payment(message: Message):
    print('\n\n\nAHAHAHAHAHh')
    
    await message.answer('Тариф успешно сменён!')
    selected_tariff = message.successful_payment.invoice_payload
    
    print('\n\n\n',message.successful_payment)

    response = await change_tariff_request(message.chat.id, selected_tariff)
    await message.answer(response)