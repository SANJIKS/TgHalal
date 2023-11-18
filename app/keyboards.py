from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

tariffs = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='На месяц')],
    [KeyboardButton(text='На полгода')],
    [KeyboardButton(text='На год')]
], resize_keyboard=True)



def tariff_payment(tariff_price, tariff):
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Оплатить ' + tariff_price, callback_data=f'pay_{tariff}')]])
    return markup

continue_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Продолжить', callback_data='continue')]])