from datetime import datetime, timezone
from dateutil import tz, parser

from sqlalchemy import select, delete, update, func, join
from app.utils.models import Langs, async_session

import aiohttp

from config import API_URL


async def get_lang_text(lang, text):
    async with async_session() as session:
        result = await session.execute(
            select(getattr(Langs, text)).where(Langs.lang == lang)
        )
        return result.scalar()


async def check_user_request(user_data: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL + 'api/telegram-users/', data=user_data) as response:
            data = await response.json()
            lang = data['lang']

            if response.status == 200:
                if 'new' in data and data['new']:
                    return 'new user'
                
                if 'tariff' in data and 'tariff_end' in data:
                    now = datetime.now(tz=tz.gettz('UTC'))

                    if data['tariff'] == 'daily':
                        tariff_end = parser.parse(data['tariff_end'])
                        if tariff_end > now:
                            days_left = (tariff_end - now).days
                            # return f'Добро пожаловать в Halal Checker Bot! 🌿\nПожалуйста, загрузите фото состава пищевого продукта, чтобы узнать его статус.\nВаш текущий тариф - пробный. Осталось {days_left} дней.'
                            result_template = await get_lang_text(lang, 'daily_response')
                            result = result_template.replace('{days_left}', str(days_left))
                            return result
                        else:
                            # return 'Добро пожаловать в Halal Checker Bot! 🌿\nВаш пробный период истёк. Пожалуйста, пополните тариф.\nБолее подробная информация о тарифах /tariff'
                            result = await get_lang_text(lang, 'expired_response')
                            return result

                    elif data['tariff'] == 'month':
                        tariff_end = parser.parse(data['tariff_end'])
                        if tariff_end > now:
                            days_left = (tariff_end - now).days
                            # return f'Добро пожаловать в Halal Checker Bot! 🌿\nПожалуйста, загрузите фото состава пищевого продукта, чтобы узнать его статус.\nВаш текущий тариф - месячный. Осталось {days_left} дней.'
                            result_template = await get_lang_text(lang, 'month_response')
                            result = result_template.replace('{days_left}', str(days_left))
                            return result
                        else:
                            # return 'Добро пожаловать в Halal Checker Bot! 🌿\nВаш тариф истёк. Пожалуйста, пополните тариф.\nБолее подробная информация о тарифах /tariff'
                            result = await get_lang_text(lang, 'expired_response')
                            return result
                    
                    elif data['tariff'] == 'six-month':
                        tariff_end = parser.parse(data['tariff_end'])
                        if tariff_end > now:
                            days_left = (tariff_end - now).days
                            # return f'Добро пожаловать в Halal Checker Bot! 🌿\nПожалуйста, загрузите фото состава пищевого продукта, чтобы узнать его статус.\nВаш текущий тариф - 6 месяцев. Осталось {days_left} дней.'
                            result_template = await get_lang_text(lang, 'six_month_response')
                            result = result_template.replace('{days_left}', str(days_left))
                            return result
                        else:
                            # return 'Добро пожаловать в Halal Checker Bot! 🌿\nВаш тариф истёк. Пожалуйста, пополните тариф.\nБолее подробная информация о тарифах /tariff'
                            result = await get_lang_text(lang, 'expired_response')
                            return result
                    
                    elif data['tariff'] == 'year':
                        tariff_end = parser.parse(data['tariff_end'])
                        if tariff_end > now:
                            days_left = (tariff_end - now).days
                            # return f'Добро пожаловать в Halal Checker Bot! 🌿\nПожалуйста, загрузите фото состава пищевого продукта, чтобы узнать его статус.\nВаш текущий тариф - годовой. Осталось {days_left} дней.'
                            result_template = await get_lang_text(lang, 'year_response')
                            result = result_template.replace('{days_left}', str(days_left))
                            return result

                        else:
                            # return 'Добро пожаловать в Halal Checker Bot! 🌿\nВаш тариф истёк. Пожалуйста, пополните тариф.\nБолее подробная информация о тарифах /tariff'
                            result = await get_lang_text(lang, 'expired_response')
                            return result
                else:
                    return 'Добро пожаловать!'
            
            else:
                return 'Технические неполадки на стороне сервера('
            
async def change_tariff_request(chat_id: int, tariff: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL + 'api/change-tariff/', data={'chat_id': chat_id, 'tariff': tariff}) as response:
            if response.status == 200:
                return 'Тариф успешно изменен на ' + tariff.capitalize()
            else:
                return 'Ошибка при изменении тарифа. Пожалуйста попробуйте позже.'
            

async def change_lang_request(chat_id: int, lang: str):
    async with aiohttp.ClientSession() as session:
        async with session.patch(API_URL + f'api/telegram-users/{chat_id}/telegram_users_partial_update/', data={'lang': lang}) as response:
            if response.status == 200:
                return True
            else:
                return False           


async def get_user_lang(chat_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL + f'api/telegram-users/', data={'chat_id': str(chat_id)}) as response:
            if response.status == 200:
                data = await response.json()
                return data['lang']
            else:
                return False
            
def parse_tariff_end(tariff_end_str):
    formats = ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z"]

    for fmt in formats:
        try:
            tariff_end = datetime.strptime(tariff_end_str, fmt)
            return tariff_end
        except ValueError:
            pass

    # Если не удалось распознать ни один формат, можно бросить исключение или вернуть None
    raise ValueError("Невозможно распознать формат времени")


async def check_tariff_not_expired(chat_id):
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL + 'api/telegram-users/', json={'chat_id': chat_id}) as response:
            if response.status == 200:
                data = await response.json()
                if 'tariff' in data and 'tariff_end' in data:
                    try:
                        tariff_end = parse_tariff_end(data['tariff_end'])
                        now = datetime.now(timezone.utc)
                        return tariff_end > now
                    except ValueError as e:
                        print(f"Ошибка при обработке времени: {e}")
                        return False
                return False
    return False


async def tariffrequest(data, file_name):
    with open(file_name, 'rb') as photo_file:
        photo_bytes = photo_file.read()

    form_data = aiohttp.FormData()
    form_data.add_field('image', photo_bytes, filename='image.jpg', content_type='image/jpeg')

    for key, value in data.items():
        form_data.add_field(key, str(value))

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL + 'api/tariff-requests/', data=form_data) as response:
            if response.status == 201:
                return True
            else:
                print(response.status)
                print(response.text)
                return False