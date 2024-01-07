from datetime import datetime, timezone
from dateutil import tz, parser

import aiohttp

from config import API_URL

async def check_user_request(user_data: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL + 'api/telegram-users/', data=user_data) as response:
            data = await response.json()

            if response.status == 200:
                if 'tariff' in data and 'tariff_end' in data:
                    now = datetime.now(tz=tz.gettz('UTC'))

                    if data['tariff'] == 'daily':
                        tariff_end = parser.parse(data['tariff_end'])
                        if tariff_end > now:
                            days_left = (tariff_end - now).days
                            return f'Добро пожаловать в Halal Checker Bot! 🌿\nПожалуйста, загрузите фото состава пищевого продукта, чтобы узнать его статус.\nВаш текущий тариф - пробный. Осталось {days_left} дней.'
                        else:
                            return 'Добро пожаловать в Halal Checker Bot! 🌿\nВаш пробный период истёк. Пожалуйста, пополните тариф.\nБолее подробная информация о тарифах /tariff'

                    elif data['tariff'] == 'month':
                        tariff_end = parser.parse(data['tariff_end'])
                        if tariff_end > now:
                            days_left = (tariff_end - now).days
                            return f'Добро пожаловать в Halal Checker Bot! 🌿\nПожалуйста, загрузите фото состава пищевого продукта, чтобы узнать его статус.\nВаш текущий тариф - месячный. Осталось {days_left} дней.'
                        else:
                            return 'Добро пожаловать в Halal Checker Bot! 🌿\nВаш тариф истёк. Пожалуйста, пополните тариф.\nБолее подробная информация о тарифах /tariff'
                    
                    elif data['tariff'] == 'six-month':
                        tariff_end = parser.parse(data['tariff_end'])
                        if tariff_end > now:
                            days_left = (tariff_end - now).days
                            return f'Добро пожаловать в Halal Checker Bot! 🌿\nПожалуйста, загрузите фото состава пищевого продукта, чтобы узнать его статус.\nВаш текущий тариф - 6 месяцев. Осталось {days_left} дней.'
                        else:
                            return 'Добро пожаловать в Halal Checker Bot! 🌿\nВаш тариф истёк. Пожалуйста, пополните тариф.\nБолее подробная информация о тарифах /tariff'
                    
                    elif data['tariff'] == 'year':
                        tariff_end = parser.parse(data['tariff_end'])
                        if tariff_end > now:
                            days_left = (tariff_end - now).days
                            return f'Добро пожаловать в Halal Checker Bot! 🌿\nПожалуйста, загрузите фото состава пищевого продукта, чтобы узнать его статус.\nВаш текущий тариф - годовой. Осталось {days_left} дней.'
                        else:
                            return 'Добро пожаловать в Halal Checker Bot! 🌿\nВаш тариф истёк. Пожалуйста, пополните тариф.\nБолее подробная информация о тарифах /tariff'
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
            

async def check_tariff_not_expired(chat_id):
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL + 'api/telegram-users/', json={'chat_id': chat_id}) as response:
            if response.status == 200:
                data = await response.json()
                if 'tariff' in data and 'tariff_end' in data:
                    tariff_end = datetime.strptime(data['tariff_end'], '%Y-%m-%dT%H:%M:%S.%f%z')
                    now = datetime.now(timezone.utc)
                    return tariff_end > now
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