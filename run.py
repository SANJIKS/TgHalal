import asyncio, logging, sys
from aiogram import Bot, Dispatcher
from app.utils.commands import set_commands

from config import TOKEN
from app.handlers.tariff_handlers import router
from app.handlers.main_handlers import router as main_router


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    await set_commands(bot)
    dp.include_router(router)
    dp.include_router(main_router)
    # dp.pre_checkout_query.register(process_payment_callback)
    await dp.start_polling(bot)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot stopped')